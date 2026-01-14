FROM python:3.12-slim

# Instalar FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Diretório para downloads
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Expor porta 8000 (Render espera 10000 por padrão, mas configuramos via env ou start command)
EXPOSE 8000

# Comando único para rodar o app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
