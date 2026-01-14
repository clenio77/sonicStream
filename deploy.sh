#!/bin/bash

# Script de Deploy para DigitalOcean (Ubuntu com Docker)
# Uso: chmod +x deploy.sh && ./deploy.sh

echo "🚀 Iniciando Deploy do Video Extractor..."

# 1. Verificar se Docker está instalado
if ! command -v docker &> /dev/null
then
    echo "🐳 Docker não encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    echo "✅ Docker instalado!"
else
    echo "✅ Docker já está instalado."
fi

# 2. Configurar permissões (evitar sudo no docker)
if ! groups $USER | grep &>/dev/null 'docker'; then
    echo "🔑 Adicionando usuário ao grupo docker..."
    sudo usermod -aG docker $USER
    echo "⚠️ Você precisará fazer logout e login novamente para as permissões surtirem efeito."
    echo "   Rode o script novamente após o login."
    exit 1
fi

# 3. Build e Subida dos Containers
echo "🏗️ Construindo e subindo containers..."
# Forçar rebuild para garantir código novo
docker compose down
docker compose up --build -d

# 4. Verificação de status
echo "🔍 Verificando status..."
sleep 5
if docker compose ps | grep "Up"; then
    echo "🎉 Deploy concluído com SUCESSO!"
    echo "🌐 Acesse: http://localhost:8000"
    echo "👤 Usuário padrão: admin"
    echo "🔑 Senha padrão: secret"
else
    echo "❌ Falha no deploy. Verifique logs com: docker compose logs"
fi
