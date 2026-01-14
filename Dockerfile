FROM python:3.12-slim

# Instala o FFmpeg (Obrigatório para o yt-dlp converter para mp3)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Cria diretório de downloads
RUN mkdir -p /app/downloads

# Variavel de ambiente para o Python não bufferizar logs
ENV PYTHONUNBUFFERED=1
