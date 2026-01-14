import os
from celery import Celery
import yt_dlp

# Configuração do Celery
celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

DOWNLOAD_DIR = "/app/downloads"

@celery.task(bind=True)
def download_audio_task(self, url: str, format: str = "mp3"):
    """
    Baixa o vídeo. Se format='mp3', extrai áudio. Se 'mp4', baixa vídeo completo.
    """
    
    # Configuração Base
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/{self.request.id}_%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    if format == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        # MP4 (Video + Audio)
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            # Precisamos encontrar o arquivo final
            # Filtramos pelo ID da task e pela extensão esperada format
            target_ext = f".{format}"
            
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(self.request.id) and f.endswith(target_ext):
                    return f 
            
            return None

    except Exception as e:
        raise Exception(f"Erro no download: {str(e)}")
