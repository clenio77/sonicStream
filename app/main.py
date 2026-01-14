from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import uuid
import threading
import yt_dlp
import time
import shutil

app = FastAPI(title="SonicStream Lite")

# Configuração
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Diretório temporário (No Render, usamos /tmp ou diretório local efêmero)
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Estado em Memória (In-Memory Database)
# Estrutura: { "task_id": { "status": "PENDING|PROCESSING|SUCCESS|FAILURE", "result": "filename", "msg": "" } }
tasks_db = {}

class VideoRequest(BaseModel):
    url: str
    format: str = "mp3"

def process_download(task_id: str, url: str, fmt: str):
    """Função background que roda em Thread"""
    print(f"🚀 Iniciando task {task_id} para {url} em {fmt}")
    tasks_db[task_id]["status"] = "PROCESSING"
    
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/{task_id}_%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        if fmt == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # MP4
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                info = info['entries'][0]

            # Encontrar o arquivo gerado
            target_ext = f".{fmt}"
            filename = None
            
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(task_id) and f.endswith(target_ext):
                    filename = f
                    break
            
            if filename:
                tasks_db[task_id]["status"] = "SUCCESS"
                tasks_db[task_id]["result"] = filename
            else:
                tasks_db[task_id]["status"] = "FAILURE"
                tasks_db[task_id]["msg"] = "Arquivo não encontrado após download."

    except Exception as e:
        print(f"❌ Erro na task {task_id}: {e}")
        tasks_db[task_id]["status"] = "FAILURE"
        tasks_db[task_id]["result"] = str(e)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/extract")
async def extract_audio(video: VideoRequest):
    # Gerar ID único
    task_id = str(uuid.uuid4())
    
    # Inicializar status
    tasks_db[task_id] = {
        "status": "PENDING", 
        "result": None,
        "created_at": time.time()
    }
    
    # Iniciar Thread (não bloqueia o servidor)
    thread = threading.Thread(target=process_download, args=(task_id, video.url, video.format))
    thread.daemon = True # Mata a thread se o app cair
    thread.start()
    
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        return JSONResponse(status_code=404, content={"status": "FAILURE", "result": "Task not found"})
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "result": task["result"]
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        media_type = 'audio/mpeg' if filename.endswith('.mp3') else 'video/mp4'
        return FileResponse(path=file_path, filename=filename, media_type=media_type)
    return JSONResponse(status_code=404, content={"message": "File not found"})

@app.get("/api/downloads")
async def list_downloads():
    """Lista downloads e limpa memória antiga"""
    files = []
    MAX_AGE = 24 * 60 * 60 # 24h arquivo
    now_ts = time.time()

    # 1. Limpar Tasks antigas da memória (> 1 hora)
    keys_to_delete = []
    for tid, tdata in tasks_db.items():
        if now_ts - tdata['created_at'] > 3600: # 1h
            keys_to_delete.append(tid)
    for k in keys_to_delete:
        del tasks_db[k]
        
    # 2. Listar Arquivos
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if not (f.endswith(".mp3") or f.endswith(".mp4")): continue
            
            path = os.path.join(DOWNLOAD_DIR, f)
            try:
                stats = os.stat(path)
                # Auto-Cleanup Arquivos (>24h)
                if now_ts - stats.st_mtime > MAX_AGE:
                    os.remove(path)
                    continue

                files.append({
                    "filename": f,
                    "size": stats.st_size,
                    "created_at": stats.st_mtime,
                    "type": "mp3" if f.endswith(".mp3") else "mp4"
                })
            except: pass

    files.sort(key=lambda x: x['created_at'], reverse=True)
    return files
