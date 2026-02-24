#!/bin/bash
# ========================================
# SCRIPT DE DEPLOY SIMPLIFICADO - VPS COM VPN
# ========================================
# Execute este script na VPS após copiar os arquivos do projeto
#
# COMO USAR:
# 1. Copiar projeto para /opt/valemilk-maps
# 2. bash deploy-vps.sh
#
# ========================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          🚀 DEPLOY VALE MILK MAPS - VPS HOSTINGER             ║
║                     (Com VPN para SQL Server)                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

PROJECT_DIR="/opt/valemilk-maps"

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Erro: Arquivo app.py não encontrado!${NC}"
    echo -e "${YELLOW}   Execute este script dentro do diretório do projeto:${NC}"
    echo -e "   ${GREEN}cd ${PROJECT_DIR} && bash deploy-vps.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Diretório do projeto encontrado${NC}"
echo ""

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Criando...${NC}"
    cat > .env << 'ENVEOF'
# Configuração do Banco de Dados
# VPS conectada via VPN, usa IP direto da rede local
DB_SERVER=10.1.0.3\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@

# Configuração da Aplicação
APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
ENVEOF
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

echo ""

# Testar conexão com SQL Server
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 Testando conexão com SQL Server (10.1.0.3)...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ping -c 2 10.1.0.3 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SQL Server acessível via rede!${NC}"
else
    echo -e "${RED}❌ AVISO: Não foi possível fazer ping em 10.1.0.3${NC}"
    echo -e "${YELLOW}   Verifique se a VPN está ativa e conectada à rede local${NC}"
    read -p "Deseja continuar mesmo assim? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo ""

# Verificar Docker
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🐋 Verificando Docker...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não instalado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✅ Docker instalado${NC}"
else
    echo -e "${GREEN}✅ Docker já instalado${NC}"
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose não instalado. Instalando...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
else
    echo -e "${GREEN}✅ Docker Compose já instalado${NC}"
fi

echo ""

# Parar containers antigos
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🛑 Parando containers antigos...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker-compose down 2>/dev/null || true

echo ""

# Build e Start
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Iniciando aplicação...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker-compose up -d --build

echo ""
echo -e "${YELLOW}⏳ Aguardando aplicação inicializar (20 segundos)...${NC}"
sleep 20

# Verificar status
if docker ps | grep -q valemilk_app; then
    echo -e "${GREEN}✅ Container rodando!${NC}"
else
    echo -e "${RED}❌ Container não está rodando${NC}"
    echo -e "${YELLOW}   Verificar logs com: docker-compose logs${NC}"
    exit 1
fi

# Mostrar logs recentes
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📋 Últimas 30 linhas do log:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker-compose logs --tail=30

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}║              ${GREEN}✅ DEPLOY CONCLUÍDO COM SUCESSO!${CYAN}                ║${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

VPS_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}🌐 Acesse a aplicação em:${NC}"
echo -e "   ${BLUE}http://${VPS_IP}:3000${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📋 Comandos úteis:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "   Ver logs           : ${GREEN}docker-compose logs -f${NC}"
echo -e "   Reiniciar          : ${GREEN}docker-compose restart${NC}"
echo -e "   Parar              : ${GREEN}docker-compose down${NC}"
echo -e "   Status             : ${GREEN}docker-compose ps${NC}"
echo -e "   Uso de recursos    : ${GREEN}docker stats valemilk_app${NC}"
echo ""

echo -e "${GREEN}🎉 Tudo pronto!${NC}"
echo ""
