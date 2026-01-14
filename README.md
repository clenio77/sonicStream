# 🎵 SonicStream

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)

**SonicStream** é uma aplicação web moderna e robusta para extração de áudio (MP3) e vídeo (MP4) de diversas plataformas (YouTube, Instagram, X/Twitter, etc.). Construída com foco em performance, privacidade e experiência do usuário.

---

## ✨ Funcionalidades

- **💎 Interface Premium**: Design glassmorphism moderno, totalmente responsivo e com modo escuro nativo.
- **📱 PWA (Progressive Web App)**: Instale no celular ou desktop como um aplicativo nativo. Funciona offline (cache de assets).
- **🎬 Multi-Formato**: Escolha entre extrair apenas o áudio (**MP3**) ou baixar o vídeo completo (**MP4**).
- **⚡ Processamento Assíncrono**: Arquitetura baseada em filas (Celery + Redis) para processar downloads pesados sem travar a interface.
- **📋 Magic Paste**: Detecção automática da área de transferência para colar links com um clique.
- **🧹 Auto-Limpeza**: Sistema inteligente que remove arquivos antigos (>24h) automaticamente para economizar espaço no servidor.
- **📂 Histórico de Downloads**: Lista os arquivos recentes disponíveis para download direto.

## 🚀 Arquitetura e Tecnologias

O projeto utiliza uma stack moderna e containerizada:

- **Backend**: Python 3.12 + FastAPI (Alta performance e validação de dados).
- **Worker**: Celery (Gerenciamento de tarefas em background).
- **Broker**: Redis (Fila de mensagens e cache).
- **Core de Download**: `yt-dlp` + `FFmpeg` (Suporte a milhares de sites e conversão de mídia).
- **Frontend**: HTML5, CSS3 (Vanilla + Google Fonts Inter), JavaScript Moderno.
- **Infraestrutura**: Docker & Docker Compose.

## 🛠️ Como Rodar Localmente

### Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Compose instalados.

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/clenio77/sonicStream.git
   cd sonicStream
   ```

2. **Inicie a aplicação**
   Utilizamos o Docker Compose para subir todos os serviços (API, Worker, Redis) com um único comando:
   ```bash
   docker compose up -d --build
   ```

3. **Acesse**
   Abra seu navegador em: [http://localhost:8000](http://localhost:8000)

## 🐳 Deploy (Produção)

O projeto inclui um script facilitador para deploy em servidores Linux (Ubuntu/Debian):

```bash
chmod +x deploy.sh
./deploy.sh
```

O script irá verificar a instalação do Docker, configurar permissões e subir os containers automaticamente.

## 🔒 Variáveis de Ambiente

O projeto é "Zero Config" por padrão, mas você pode customizar via variáveis de ambiente no `docker-compose.yml`:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `CELERY_BROKER_URL` | URL de conexão do Redis | `redis://redis:6379/0` |

---

## 🤝 Contribuição

Sinta-se à vontade para abrir **Issues** ou enviar **Pull Requests**. Sugestões são sempre bem-vindas!

---

<p align="center">
  Feito com 💜 por <a href="https://github.com/clenio77">Clenio</a>
</p>
