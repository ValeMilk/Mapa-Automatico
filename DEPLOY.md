# 🚀 Deploy na VPS Hostinger - Vale Milk Maps

## 📋 Pré-requisitos

1. **VPS Hostinger** com Ubuntu/Debian
2. **Acesso SSH** à VPS
3. **Git instalado** na VPS
4. **Acesso ao banco de dados SQL Server**

---

## 🔐 Passo 1: Conectar na VPS via SSH

```bash
ssh root@SEU_IP_VPS
# ou
ssh seu_usuario@SEU_IP_VPS
```

---

## 📦 Passo 2: Instalar Dependências Básicas

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Git
apt install -y git curl

# Instalar Docker (será feito automaticamente pelo script)
```

---

## 📂 Passo 3: Clonar o Repositório

```bash
cd /opt
git clone https://github.com/ValeMilk/Mapa-Automatico.git
cd Mapa-Automatico
```

---

## ⚙️ Passo 4: Configurar Variáveis de Ambiente

```bash
# Copiar exemplo de .env
cp .env.example .env

# Editar configurações
nano .env
```

**Edite o arquivo `.env` com suas configurações:**

```env
# IMPORTANTE: Altere o DB_SERVER para o IP correto
DB_SERVER=SEU_IP_SQL_SERVER\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=sua_senha_aqui

APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
```

**Salvar:** `Ctrl + O` → `Enter` → `Ctrl + X`

---

## 🗄️ Passo 5: Configurar Acesso ao Banco de Dados

### Opção A: VPN (Recomendado para segurança)

Se o SQL Server está na rede local (10.1.0.3), você precisa de VPN:

1. **WireGuard** (mais rápido)
2. **OpenVPN**
3. **Tailscale** (mais fácil)

### Opção B: SQL Server com IP Público

1. Configure o SQL Server para aceitar conexões externas
2. Libere a porta 1433 no firewall
3. Use o IP público no `.env`

### Opção C: Túnel SSH Reverso

```bash
# No computador com SQL Server (Windows)
ssh -R 1433:10.1.0.3:1433 root@SEU_IP_VPS -N
```

---

## 🚀 Passo 6: Executar Deploy

```bash
# Dar permissão de execução ao script
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

O script irá:
- ✅ Instalar Docker e Docker Compose
- ✅ Construir a imagem
- ✅ Subir a aplicação
- ✅ Mostrar status e logs

---

## 🌐 Passo 7: Configurar Firewall

```bash
# Permitir porta 3000
ufw allow 3000/tcp

# Permitir SSH (se ainda não permitiu)
ufw allow 22/tcp

# Ativar firewall
ufw enable
```

---

## 🔐 Passo 8: Configurar Domínio (Opcional)

### Com Nginx como Proxy Reverso

```bash
# Instalar Nginx
apt install -y nginx

# Criar configuração
nano /etc/nginx/sites-available/valemilk
```

**Conteúdo:**

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Ativar site
ln -s /etc/nginx/sites-available/valemilk /etc/nginx/sites-enabled/

# Testar configuração
nginx -t

# Reiniciar Nginx
systemctl restart nginx
```

### Instalar SSL (HTTPS) com Certbot

```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
certbot --nginx -d seu-dominio.com

# Renovação automática já está configurada
```

---

## 📊 Passo 9: Monitorar Aplicação

### Ver logs em tempo real
```bash
cd /opt/Mapa-Automatico
docker-compose logs -f
```

### Ver status dos containers
```bash
docker-compose ps
```

### Reiniciar aplicação
```bash
docker-compose restart
```

### Parar aplicação
```bash
docker-compose down
```

### Iniciar aplicação
```bash
docker-compose up -d
```

---

## 🔄 Passo 10: Atualizar Aplicação

```bash
cd /opt/Mapa-Automatico

# Puxar updates do Git
git pull origin main

# Redeployar
./deploy.sh
```

---

## 🆘 Problemas Comuns

### 1. Erro de conexão com SQL Server

**Sintoma:** `Login failed for user` ou timeout

**Solução:**
- Verifique se o IP/porta do SQL Server estão corretos no `.env`
- Teste conexão: `telnet IP_SQL_SERVER 1433`
- Verifique firewall do SQL Server
- Confirme que SQL Server aceita conexões remotas

### 2. Container não inicia

**Sintoma:** Container em estado "Exit" ou "Restarting"

**Solução:**
```bash
# Ver logs de erro
docker-compose logs

# Reconstruir sem cache
docker-compose build --no-cache
docker-compose up -d
```

### 3. Porta 3000 já em uso

**Solução:**
```bash
# Ver o que está usando a porta
netstat -tulpn | grep 3000

# Matar processo
kill -9 PID

# Ou mudar porta no docker-compose.yml
```

### 4. Aplicação lenta

**Solução:**
- Aumentar recursos da VPS
- Verificar logs: `docker stats`
- Otimizar cache no app.py

---

## 📝 Backup Automático

### Criar script de backup
```bash
nano /opt/backup-valemilk.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do código
cd /opt/Mapa-Automatico
tar -czf $BACKUP_DIR/valemilk-code-$DATE.tar.gz .

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $BACKUP_DIR/valemilk-code-$DATE.tar.gz"
```

```bash
chmod +x /opt/backup-valemilk.sh

# Adicionar ao crontab (backup diário às 2h)
crontab -e
# Adicionar linha:
0 2 * * * /opt/backup-valemilk.sh
```

---

## 🎯 Resumo Rápido

```bash
# 1. Conectar VPS
ssh root@SEU_IP

# 2. Clonar projeto
cd /opt
git clone https://github.com/ValeMilk/Mapa-Automatico.git
cd Mapa-Automatico

# 3. Configurar
cp .env.example .env
nano .env  # Editar configurações

# 4. Deploy
chmod +x deploy.sh
./deploy.sh

# 5. Testar
curl http://localhost:3000
```

---

## 📞 Suporte

- 📧 Email: suporte@valemilk.com.br
- 📱 WhatsApp: (85) XXXX-XXXX
- 🌐 Site: https://valemilk.com.br

---

**Desenvolvido com ❤️ para Vale Milk**
