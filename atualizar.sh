#!/bin/bash
# ========================================
# SCRIPT DE ATUALIZAÇÃO AUTOMÁTICA
# ========================================
# Execute este script na VPS para atualizar a aplicação
# após fazer push no GitHub
#
# Uso: bash atualizar.sh
# ========================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║            🔄 ATUALIZAÇÃO - Vale Milk Maps                    ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

PROJECT_DIR="/opt/valemilk-maps"

# Verificar se está no diretório correto
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Diretório $PROJECT_DIR não encontrado!${NC}"
    echo -e "   Executando de onde está..."
    PROJECT_DIR=$(pwd)
fi

cd $PROJECT_DIR

# Verificar se é um repositório Git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}❌ Este não é um repositório Git!${NC}"
    exit 1
fi

echo -e "${GREEN}📍 Diretório: $PROJECT_DIR${NC}"
echo ""

# Mostrar branch atual
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${CYAN}🌿 Branch atual: ${CURRENT_BRANCH}${NC}"
echo ""

# Baixar atualizações
echo -e "${YELLOW}📥 Baixando atualizações do GitHub...${NC}"
git fetch origin

# Verificar se há mudanças
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}✅ Aplicação já está atualizada!${NC}"
    echo ""
    docker-compose ps
    exit 0
fi

echo -e "${CYAN}🆕 Novas atualizações encontradas!${NC}"
echo ""

# Mostrar mudanças
echo -e "${YELLOW}📝 Mudanças a serem aplicadas:${NC}"
git log HEAD..origin/$CURRENT_BRANCH --oneline --no-decorate
echo ""

# Pull
echo -e "${YELLOW}⬇️  Aplicando atualizações...${NC}"
git pull origin $CURRENT_BRANCH

echo ""
echo -e "${YELLOW}🛑 Parando containers...${NC}"
docker-compose down

echo ""
echo -e "${YELLOW}🔨 Reconstruindo aplicação...${NC}"
docker-compose build

echo ""
echo -e "${YELLOW}🚀 Iniciando aplicação...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}⏳ Aguardando inicialização (15 segundos)...${NC}"
sleep 15

echo ""
echo -e "${GREEN}✅ Atualização concluída!${NC}"
echo ""

# Status
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 Status da Aplicação:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}📋 Para ver os logs:${NC}"
echo -e "   ${YELLOW}docker-compose logs -f${NC}"
echo ""
