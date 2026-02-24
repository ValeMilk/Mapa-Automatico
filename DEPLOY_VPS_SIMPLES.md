# 🚀 Deploy VPS Hostinger - Versão Simplificada (Com VPN)

## ✅ Pré-requisito Atendido

✅ **VPS já conectada via VPN ao SQL Server local (10.1.0.3)**  
✅ **Não precisa de túnel SSH!**

---

## 🎯 Deploy em 4 Passos Simples

### **Passo 1: Conectar na VPS**

```bash
ssh root@SEU_IP_VPS
# Exemplo: ssh root@45.67.89.123
```

---

### **Passo 2: Instalar Docker (se necessário)**

```bash
# Testar se já tem Docker
docker --version

# Se não tiver, instalar:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

---

### **Passo 3: Enviar Projeto para VPS**

**⭐ Recomendado: Via GitHub**

```bash
# Na VPS
cd /opt

# Clonar repositório (trocar SEU_USUARIO pelo seu GitHub username)
git clone https://github.com/SEU_USUARIO/valemilk-maps.git

cd valemilk-maps
```

✅ **Vantagens:**
- Fácil atualizar depois (`git pull`)
- Versionamento completo
- Deploy profissional

---

**Opção B: Via SCP (do seu PC Windows)**

```powershell
# No PowerShell do seu PC:
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"

# Enviar usando o script automatizado
.\enviar-para-vps.ps1

# Ou manualmente com SCP:
# scp -r * root@SEU_IP_VPS:/opt/valemilk-maps/
```

---

**Opção C: Via WinSCP/FileZilla**

Use interface gráfica para copiar a pasta para `/opt/valemilk-maps`

---

### **Passo 4: Configurar e Iniciar**

```bash
# Na VPS, dentro de /opt/valemilk-maps

# 4.1 Criar arquivo .env
nano .env
```

Cole este conteúdo no .env:

```env
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
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

```bash
# 4.2 Testar conexão com SQL Server (importante!)
ping 10.1.0.3

# 4.3 Iniciar aplicação
docker-compose up -d --build

# 4.4 Ver logs
docker-compose logs -f
```

Você deve ver:
```
🚀 Gerando mapas iniciais...
✅ Todos os mapas iniciais foram gerados!
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:3000
```

**Pressione Ctrl+C para sair dos logs**

---

## 🌐 Acessar Aplicação

```
http://SEU_IP_VPS:3000
```

Exemplo: `http://45.67.89.123:3000`

---

## 🎨 (Opcional) Configurar Domínio + SSL

### 1. Instalar Nginx

```bash
apt install nginx -y
```

### 2. Configurar Nginx

```bash
nano /etc/nginx/sites-available/valemilk
```

Cole:

```nginx
server {
    listen 80;
    server_name maps.seudominio.com.br;  # Trocar pelo seu domínio
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

```bash
# Ativar configuração
ln -s /etc/nginx/sites-available/valemilk /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 3. Instalar SSL (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d maps.seudominio.com.br
```

Agora acessar: `https://maps.seudominio.com.br`

---

## 🔄 Atualizar Aplicação

Quando mudar código no PC:

```bash
# 1. Enviar arquivos atualizados
# scp app.py root@VPS:/opt/valemilk-maps/
# scp MapaAutomatico.py root@VPS:/opt/valemilk-maps/
# etc...

# 2. Na VPS, reiniciar
cd /opt/valemilk-maps
docker-compose down
docker-compose up -d --build
```

Ou criar script de deploy automático.

---

## 📋 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver status
docker-compose ps

# Reiniciar aplicação
docker-compose restart

# Parar aplicação
docker-compose down

# Iniciar aplicação
docker-compose up -d

# Rebuild completo
docker-compose up -d --build

# Ver uso de recursos
docker stats valemilk_app

# Entrar no container
docker exec -it valemilk_app bash
```

---

## 🆘 Troubleshooting

### Erro: Não conecta ao banco

```bash
# Testar conexão SQL Server
ping 10.1.0.3
telnet 10.1.0.3 1433

# Verificar VPN ativa
ip route  # Deve mostrar rota para 10.1.0.0/24
```

### Erro: Porta 3000 já em uso

```bash
# Ver o que está usando a porta
netstat -tulpn | grep 3000

# Trocar porta no .env
nano .env
# Mudar: APP_PORT=3001
docker-compose down
docker-compose up -d
```

### Mapas não carregam

```bash
# Ver logs detalhados
docker-compose logs -f

# Verificar se arquivos HTML foram gerados
docker exec valemilk_app ls -lh /app/*.html

# Regenerar mapas manualmente
docker exec -it valemilk_app bash
python -c "from MapaAutomatico import gerar_mapa_com_query; gerar_mapa_com_query(1)"
```

### Erro de memória

```bash
# Ver uso de recursos
docker stats

# Se precisar, adicionar swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 🔒 Segurança Recomendada

### 1. Firewall

```bash
# UFW (Ubuntu/Debian)
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 3000  # App (se não usar Nginx)
ufw enable
```

### 2. Fail2Ban (proteção contra bruteforce SSH)

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Remover senhas hardcoded (IMPORTANTE!)

Atualmente as senhas do banco estão no código. Migrar para .env:

```python
# Em app.py e MapaAutomatico.py, trocar por:
import os
DB_SERVER = os.getenv('DB_SERVER', '10.1.0.3\\SQLSTANDARD')
DB_USER = os.getenv('DB_USER', 'analistarpt')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

---

## 📊 Monitoramento

### Logs do Sistema

```bash
# Ver logs do Docker
journalctl -u docker -f

# Ver logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Monitoramento de Performance

```bash
# Instalar htop
apt install htop -y
htop

# Ver uso de disco
df -h

# Ver uso de memória
free -h
```

---

## 🎉 Pronto!

Agora sua aplicação roda 24/7 na VPS, mesmo com o PC desligado!

A VPS acessa o banco via VPN sempre que precisar atualizar os mapas.

**Nota:** Certifique-se que a VPN da VPS está sempre conectada ao SQL Server.
