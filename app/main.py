from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from celery.result import AsyncResult
from pydantic import BaseModel
import os
import secrets
from app.worker import download_audio_task

app = FastAPI(title="Video to MP3 Extractor")
security = HTTPBasic()

# Configuração de Auth (Ler de variáveis de ambiente)
AUTH_USER = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASS = os.environ.get("AUTH_PASSWORD", "admin")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, AUTH_USER)
    is_correct_password = secrets.compare_digest(credentials.password, AUTH_PASS)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Configuração de templates e estáticos
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
DOWNLOAD_DIR = "/app/downloads"

# Modelo de Input
class VideoRequest(BaseModel):
    url: str
    format: str = "mp3"  # mp3 ou mp4

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/extract")
async def extract_audio(video: VideoRequest):
    """Inicia o job no Celery"""
    task = download_audio_task.delay(video.url, video.format)
    return {"task_id": task.id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Checa o status da tarefa no Redis"""
    task_result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None
    }

    if task_result.status == 'SUCCESS':
        response["result"] = task_result.result # Nome do arquivo
    elif task_result.status == 'FAILURE':
        response["result"] = str(task_result.result)
        
    return JSONResponse(response)

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Serve o arquivo MP3/MP4"""
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        media_type = 'audio/mpeg' if filename.endswith('.mp3') else 'video/mp4'
        return FileResponse(path=file_path, filename=filename, media_type=media_type)
    return JSONResponse(status_code=404, content={"message": "File not found"})

@app.get("/api/downloads")
async def list_downloads():
    """Lista os arquivos baixados e remove antigos (> 24h)"""
    files = []
    
    # 24 horas em segundos
    MAX_AGE = 24 * 60 * 60 
    now = os.path.getmtime('.') # Time de referência (hacky but works) ou time.time()
    import time
    now_ts = time.time()

    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, f)
            
            # Verificação de segurança basica
            if not (f.endswith(".mp3") or f.endswith(".mp4")):
                continue

            try:
                stats = os.stat(file_path)
                file_age = now_ts - stats.st_mtime
                
                # Auto-Cleanup: Deletar se for maior que 24h
                if file_age > MAX_AGE:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up old file: {f}")
                    continue

                files.append({
                    "filename": f,
                    "size": stats.st_size,
                    "created_at": stats.st_mtime,
                    "type": "mp3" if f.endswith(".mp3") else "mp4"
                })
            except Exception as e:
                print(f"Error processing file {f}: {e}")

    # Ordenar por mais novo
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return files
