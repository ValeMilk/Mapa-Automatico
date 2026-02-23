#!/bin/bash
# Script de Deploy para VPS Hostinger
# Uso: ./deploy.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy Vale Milk Maps..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto${NC}"
    exit 1
fi

# 2. Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edite o arquivo .env com as configurações corretas!${NC}"
    echo "Execute: nano .env"
    exit 1
fi

# 3. Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado!${NC}"
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✅ Docker instalado com sucesso${NC}"
fi

# 4. Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose não encontrado. Instalando...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
fi

# 5. Parar containers antigos
echo "🛑 Parando containers antigos..."
docker-compose down || true

# 6. Limpar recursos não utilizados
echo "🧹 Limpando recursos Docker não utilizados..."
docker system prune -f

# 7. Build da imagem
echo "🏗️  Construindo imagem Docker..."
docker-compose build --no-cache

# 8. Subir aplicação
echo "🚀 Iniciando aplicação..."
docker-compose up -d

# 9. Verificar status
echo "📊 Verificando status..."
sleep 5
docker-compose ps

# 10. Mostrar logs
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "📋 Para ver os logs em tempo real, execute:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Aplicação disponível em: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "🔧 Comandos úteis:"
echo "   docker-compose logs -f          # Ver logs"
echo "   docker-compose restart          # Reiniciar"
echo "   docker-compose down             # Parar"
echo "   docker-compose up -d            # Iniciar"
