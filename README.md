# 🗺️ Vale Milk - Sistema de Mapas Automatizados

## 📖 Descrição

Sistema de geração e visualização de mapas de rotas para entregas da Vale Milk, com filtros inteligentes e otimização de rotas.

## ✨ Funcionalidades

- 🚚 **6 Tipos de Mapas:**
  - Mapa Motorista (Amanhã)
  - Mapa Cliente (5 dias)
  - Mapa Motorista do Dia
  - Mapa Interior Semana
  - Mapa Interior Geral
  - Mapa Geral de Clientes (1219 clientes)

- 🔍 **Filtros Avançados:**
  - Regional (L81-CAPITAL / L82-INTERIOR)
  - Rota
  - ID Cliente
  - Nome Cliente
  - Vendedor
  - Supervisor

- ⚡ **Otimizações:**
  - Compressão GZIP (Level 6)
  - Cache de 5 minutos
  - Gunicorn (2 workers, 4 threads)
  - Pré-geração de mapas

- 🎨 **Interface Moderna:**
  - UI responsiva com gradientes azuis
  - Busca em tempo real nos filtros
  - Contador de registros visíveis
  - Ícones customizados por supervisor

## 🚀 Deploy Rápido na VPS

### Método 1: Instalação Automática

```bash
ssh root@SEU_IP_VPS
curl -fsSL https://raw.githubusercontent.com/ValeMilk/Mapa-Automatico/main/install.sh | bash
```

### Método 2: Manual

```bash
# 1. Clonar repositório
git clone https://github.com/ValeMilk/Mapa-Automatico.git
cd Mapa-Automatico

# 2. Configurar ambiente
cp .env.example .env
nano .env  # Edite com suas configurações

# 3. Executar deploy
chmod +x deploy.sh
./deploy.sh
```

📚 **Guia completo:** [DEPLOY.md](DEPLOY.md)

## 💻 Desenvolvimento Local

### Requisitos

- Python 3.11+
- Docker & Docker Compose
- SQL Server (ou acesso remoto)

### Setup

```bash
# 1. Clonar repositório
git clone https://github.com/ValeMilk/Mapa-Automatico.git
cd Mapa-Automatico

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Edite .env com suas configurações

# 4. Executar com Docker
docker-compose up -d

# Ou rodar diretamente
python app.py
```

## 📁 Estrutura do Projeto

```
Mapa-Automatico/
├── app.py                    # Aplicação Flask principal
├── MapaAutomatico.py         # Geração de mapas tipos 1-5
├── mapa_geral_module.py      # Módulo mapa geral (tipo 6)
├── ROTA SEMANA.csv          # CSV de rotas e motoristas
├── docker-compose.yml        # Configuração Docker
├── Dockerfile               # Imagem Docker
├── requirements.txt         # Dependências Python
├── nginx.conf               # Configuração Nginx (opcional)
├── deploy.sh                # Script de deploy
├── install.sh               # Script de instalação rápida
├── DEPLOY.md                # Guia completo de deploy
└── .env.example             # Exemplo de variáveis de ambiente
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
DB_SERVER=IP_DO_SQL_SERVER\SQLSTANDARD
DB_NAME=dbactions
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
```

## 🌐 Rotas da Aplicação

- `/` - Homepage com lista de mapas
- `/mapa_1` - Mapa Motorista (Amanhã)
- `/mapa_2` - Mapa Cliente (5 dias)
- `/mapa_3` - Mapa Motorista do Dia
- `/mapa_4` - Mapa Interior Semana
- `/mapa_5` - Mapa Interior Geral
- `/mapa_geral` - Mapa Geral de Clientes (com filtros)

## 🐳 Comandos Docker Úteis

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Reconstruir
docker-compose build --no-cache

# Ver status
docker-compose ps
```

## 📊 Monitoramento

### Logs da aplicação
```bash
docker-compose logs -f valemilk-web
```

### Status do container
```bash
docker stats valemilk_app
```

## 🔄 Atualização

```bash
cd /opt/Mapa-Automatico
git pull origin main
./deploy.sh
```

## 🆘 Troubleshooting

### Problema: Container não inicia
```bash
docker-compose logs
docker-compose build --no-cache
```

### Problema: Erro de conexão com banco
- Verificar `.env` está configurado corretamente
- Testar conexão: `telnet IP_SQL_SERVER 1433`
- Verificar firewall do SQL Server

### Problema: Porta 3000 em uso
```bash
netstat -tulpn | grep 3000
# Ou mudar APP_PORT no .env
```

## 📈 Performance

- **Tempo de carregamento:** < 2s (primeira vez), < 500ms (cache)
- **Compressão:** ~70% redução no tamanho HTML
- **Mapas pré-gerados:** Atualização automática a cada 5 minutos
- **Workers:** 2 workers Gunicorn com 4 threads cada

## 🔐 Segurança

- Variáveis sensíveis em `.env` (não commitado)
- HTTPS via Nginx + Certbot (recomendado)
- Firewall configurado (UFW)
- Conexão SSL com SQL Server

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📝 Changelog

### v2.0.0 (2026-01-29)
- ✨ Adicionado filtro Regional (L81/L82)
- ⚡ Otimização com atributos data-* nos marcadores
- 🎨 UI moderna com gradientes azuis
- 🔧 Melhorias no sistema de filtros

### v1.0.0 (2025-XX-XX)
- 🎉 Release inicial

## 📄 Licença

Propriedade de **Vale Milk Indústria e Comércio Ltda.**

## 👥 Equipe

- **Desenvolvimento:** Equipe Vale Milk TI
- **Suporte:** suporte@valemilk.com.br

---

**Desenvolvido com ❤️ para Vale Milk**
