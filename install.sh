#!/bin/bash
# Quick Install Script - Vale Milk Maps
# Execute: curl -fsSL https://raw.githubusercontent.com/ValeMilk/Mapa-Automatico/main/install.sh | bash

set -e

echo "╔══════════════════════════════════════════╗"
echo "║   Vale Milk Maps - Instalação Rápida   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Execute como root ou use sudo"
    exit 1
fi

echo "📦 Instalando dependências..."
apt update -qq
apt install -y git curl > /dev/null 2>&1

echo "📂 Clonando repositório..."
cd /opt
if [ -d "Mapa-Automatico" ]; then
    echo "⚠️  Diretório já existe. Atualizando..."
    cd Mapa-Automatico
    git pull
else
    git clone https://github.com/ValeMilk/Mapa-Automatico.git
    cd Mapa-Automatico
fi

echo "⚙️  Configurando ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANTE: Configure o arquivo .env antes de continuar!${NC}"
    echo ""
    echo "Execute os seguintes comandos:"
    echo "  cd /opt/Mapa-Automatico"
    echo "  nano .env"
    echo ""
    echo "Depois execute:"
    echo "  ./deploy.sh"
    exit 0
fi

echo "🚀 Executando deploy..."
chmod +x deploy.sh
./deploy.sh

echo ""
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo ""
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):3000"
