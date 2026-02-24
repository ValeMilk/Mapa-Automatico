#!/bin/bash
# ========================================
# INSTALAÇÃO AUTOMATIZADA - VPS HOSTINGER
# ========================================
# Este script instala e configura tudo automaticamente na VPS
#
# COMO USAR:
# curl -fsSL https://raw.githubusercontent.com/.../install-vps.sh | bash
# OU
# wget -O - https://raw.githubusercontent.com/.../install-vps.sh | bash
# OU baixar e executar: bash install-vps.sh
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

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🗺️  VALE MILK MAPS - INSTALAÇÃO VPS HOSTINGER         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Este script precisa ser executado como root${NC}"
    echo -e "${YELLOW}   Use: sudo bash install-vps.sh${NC}"
    exit 1
fi

PROJECT_DIR="/opt/valemilk-maps"

echo -e "${BLUE}📋 Instalação será feita em: ${PROJECT_DIR}${NC}"
echo ""

# ========== PASSO 1: Atualizar Sistema ==========
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[1/7] 📦 Atualizando sistema...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
apt update && apt upgrade -y
apt install -y curl wget git nano

# ========== PASSO 2: Instalar Docker ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[2/7] 🐋 Instalando Docker...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✅ Docker instalado${NC}"
else
    echo -e "${YELLOW}⚡ Docker já instalado${NC}"
fi

# ========== PASSO 3: Instalar Docker Compose ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[3/7] 🔧 Instalando Docker Compose...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
else
    echo -e "${YELLOW}⚡ Docker Compose já instalado${NC}"
fi

docker-compose --version

# ========== PASSO 4: Criar Diretório do Projeto ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[4/7] 📁 Criando diretório do projeto...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
echo -e "${GREEN}✅ Diretório criado: ${PROJECT_DIR}${NC}"

# ========== PASSO 5: Baixar/Clonar Projeto ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[5/7] 📥 Obtendo código do projeto...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "${YELLOW}⚠️  ATENÇÃO: Agora você precisa colocar os arquivos do projeto aqui!${NC}"
echo ""
echo -e "Opções:"
echo -e "  ${BLUE}1.${NC} Se tiver Git repository:"
echo -e "     ${GREEN}git clone https://github.com/SEU_USUARIO/Mapa-Automatico.git .${NC}"
echo ""
echo -e "  ${BLUE}2.${NC} Se tiver os arquivos no PC Windows:"
echo -e "     No PowerShell do seu PC:"
echo -e "     ${GREEN}scp -r \"C:\\Users\\PC 0025\\Desktop\\Nicolas\\mapaotimizado automatico\\*\" root@$(hostname -I | awk '{print $1}'):${PROJECT_DIR}${NC}"
echo ""
echo -e "  ${BLUE}3.${NC} Usando o script enviar-para-vps.ps1 (recomendado):"
echo -e "     No PowerShell do seu PC:"
echo -e "     ${GREEN}.\\enviar-para-vps.ps1${NC}"
echo ""
read -p "Pressione ENTER após copiar os arquivos para continuar..."

# Verificar se arquivos foram copiados
if [ ! -f "${PROJECT_DIR}/app.py" ]; then
    echo -e "${RED}❌ Arquivo app.py não encontrado!${NC}"
    echo -e "${YELLOW}   Copie os arquivos do projeto para ${PROJECT_DIR} e execute este script novamente.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arquivos do projeto encontrados${NC}"

# ========== PASSO 6: Configurar .env ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[6/7] ⚙️  Configurando variáveis de ambiente...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo -e "${YELLOW}⚠️  Criando arquivo .env...${NC}"
    cat > ${PROJECT_DIR}/.env << 'ENVEOF'
# Configuração do Banco de Dados
# IMPORTANTE: Use 127.0.0.1 se estiver usando túnel SSH
DB_SERVER=127.0.0.1\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@

# Configuração da Aplicação
APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
ENVEOF
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
    echo -e "${YELLOW}⚠️  REVISE o arquivo .env se necessário:${NC}"
    echo -e "   ${GREEN}nano ${PROJECT_DIR}/.env${NC}"
    echo ""
    read -p "Pressione ENTER para continuar ou Ctrl+C para editar o .env agora..."
else
    echo -e "${YELLOW}⚡ Arquivo .env já existe${NC}"
fi

# ========== PASSO 7: Iniciar Aplicação ==========
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[7/7] 🚀 Iniciando aplicação...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Parar containers antigos se existirem
docker-compose down 2>/dev/null || true

# Build e start
docker-compose up -d --build

echo ""
echo -e "${GREEN}⏳ Aguardando aplicação inicializar...${NC}"
sleep 10

# Verificar status
if docker ps | grep -q valemilk_app; then
    echo -e "${GREEN}✅ Container rodando!${NC}"
else
    echo -e "${RED}❌ Container não está rodando${NC}"
    echo -e "${YELLOW}   Verificar logs: docker-compose logs${NC}"
    exit 1
fi

# ========== FINALIZAÇÃO ==========
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}║                  ${GREEN}✅ INSTALAÇÃO CONCLUÍDA!${CYAN}                      ║${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

VPS_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}📊 Status:${NC}"
docker-compose ps
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌐 Acesso à Aplicação:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "   ${BLUE}http://${VPS_IP}:3000${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE - TÚNEL SSH:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Para conectar ao SQL Server local você precisa criar um túnel SSH"
echo -e "a partir do seu PC Windows. Execute no PowerShell:"
echo ""
echo -e "   ${GREEN}cd \"C:\\Users\\PC 0025\\Desktop\\Nicolas\\mapaotimizado automatico\"${NC}"
echo -e "   ${GREEN}.\\tunel-vps.ps1${NC}"
echo ""
echo -e "${YELLOW}(Edite o arquivo tunel-vps.ps1 primeiro e configure o IP da VPS)${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📋 Comandos Úteis:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "   Ver logs           : ${GREEN}docker-compose logs -f${NC}"
echo -e "   Reiniciar          : ${GREEN}docker-compose restart${NC}"
echo -e "   Parar              : ${GREEN}docker-compose down${NC}"
echo -e "   Iniciar            : ${GREEN}docker-compose up -d${NC}"
echo -e "   Status containers  : ${GREEN}docker-compose ps${NC}"
echo -e "   Rebuild completo   : ${GREEN}docker-compose up -d --build${NC}"
echo ""

echo -e "${GREEN}🎉 Tudo pronto! Boa sorte!${NC}"
echo ""
