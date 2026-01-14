# 🎵 SonicStream (Lite)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)

**SonicStream** é uma aplicação web moderna e robusta para extração de áudio (MP3) e vídeo (MP4) de diversas plataformas (YouTube, Instagram, X/Twitter, etc.). Construída com foco em performance, privacidade e experiência do usuário.

> **Versão Lite:** Esta versão foi otimizada para rodar em container único, usando Threads em memória em vez de sistemas complexos de fila (Redis), ideal para rodar em casa (Self-Hosted) ou VPS pequenas.

---

## ✨ Funcionalidades

- **💎 Interface Premium**: Design glassmorphism moderno, totalmente responsivo e com modo escuro nativo.
- **📱 PWA (Progressive Web App)**: Instale no celular ou desktop como um aplicativo nativo. Funciona offline (cache de assets).
- **🎬 Multi-Formato**: Escolha entre extrair apenas o áudio (**MP3**) ou baixar o vídeo completo (**MP4**).
- **⚡ Processamento In-Memory**: Sistema leve de filas em memória para processar downloads sem travar a interface.
- **📋 Magic Paste**: Detecção automática da área de transferência para colar links com um clique.
- **🧹 Auto-Limpeza**: Sistema inteligente que remove arquivos antigos (>24h) automaticamente para economizar espaço no servidor.
- **📂 Histórico de Downloads**: Lista os arquivos recentes disponíveis para download direto.
- **🌐 Cloudflare Tunnel**: Acesso externo seguro "Out-of-the-box".

## 🚀 Arquitetura e Tecnologias

O projeto utiliza uma stack moderna e containerizada:

- **Backend**: Python 3.12 + FastAPI.
- **Core de Download**: `yt-dlp` + `FFmpeg`.
- **Frontend**: HTML5, CSS3 (Vanilla + Google Fonts Inter), JavaScript Moderno.
- **Infraestrutura**: Docker & Docker Compose com Cloudflare Tunnel.

## 🛠️ Como Rodar (Local & Externo)

### 1. Iniciar a Aplicação
Basta ter o Docker instalado e rodar:

```bash
docker compose up -d --build
```

O sistema irá subir:
1. **App**: O site em si.
2. **Tunnel**: O conector da Cloudflare para acesso externo.

### 2. Acessar o Sistema

#### 🏠 Opção A: Acesso Local (Wi-Fi de casa)
Se estiver na mesma rede, use o IP do computador.
Descubra seu IP com `hostname -I` e acesse:
`http://SEU_IP_LOCAL:8090` (Ex: `http://192.168.1.15:8090`)

#### 🌍 Opção B: Acesso Externo (Internet/4G)
Para acessar de qualquer lugar do mundo (Sem abrir portas no roteador), pegue o link mágico nos logs:

```bash
docker logs sonicstream_tunnel 2>&1 | grep "trycloudflare.com"
```
Copie o link gerado (Ex: `https://entregando-algo.trycloudflare.com`).

---

## 🤝 Contribuição

Sinta-se à vontade para abrir **Issues** ou enviar **Pull Requests**. Sugestões são sempre bem-vindas!

---

<p align="center">
  Feito com 💜 por <a href="https://github.com/clenio77">Clenio</a>
</p>
