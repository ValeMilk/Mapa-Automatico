# 🚀 Deploy na VPS Hostinger - Guia Completo

## 📋 Problema a Resolver

**Situação atual:** Aplicação rodando no PC local (10.1.1.115) conectando ao SQL Server local (10.1.0.3)

**Objetivo:** Hospedar na VPS Hostinger para rodar 24/7 mesmo com PC desligado

**Desafio:** VPS precisa acessar o banco SQL Server que está na sua rede local

---

## 🔐 SOLUÇÃO: Túnel SSH Reverso (Recomendado para começar)

### Como funciona:
1. PC cria túnel SSH para a VPS
2. VPS acessa SQL Server através do túnel
3. Aplicação roda 24/7 na VPS
4. PC precisa estar ligado apenas quando precisar acessar o banco

---

## 📦 Passo 1: Preparar Arquivos Locais

### 1.1 Criar arquivo .env para produção

```bash
# Copiar este conteúdo para um arquivo .env no seu PC local
DB_SERVER=127.0.0.1\\SQLSTANDARD
DB_PORT=1433
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@

APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
```

⚠️ **Nota:** Usamos `127.0.0.1` porque o túnel SSH vai mapear a porta local 1433 da VPS para o SQL Server local

---

## 🌐 Passo 2: Acessar sua VPS

### 2.1 Conectar via SSH

```bash
ssh root@SEU_IP_VPS
# ou
ssh seu_usuario@SEU_IP_VPS
```

**Exemplo:**
```bash
ssh root@45.67.89.123
```

---

## 📥 Passo 3: Clonar Projeto na VPS

```bash
# Criar diretório
cd /opt
git clone https://github.com/SEU_USUARIO/Mapa-Automatico.git valemilk-maps
cd valemilk-maps

# OU se não tiver no GitHub, enviar via SCP do seu PC:
# Na sua máquina Windows (PowerShell):
# scp -r "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico" root@SEU_IP_VPS:/opt/valemilk-maps
```

---

## 🔧 Passo 4: Configurar VPS

### 4.1 Instalar Docker (se necessário)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
```

### 4.2 Instalar Docker Compose

```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 4.3 Criar .env na VPS

```bash
cd /opt/valemilk-maps
nano .env
```

Cole o conteúdo:
```env
DB_SERVER=127.0.0.1\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@

APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 🔗 Passo 5: Criar Túnel SSH Reverso (NO SEU PC WINDOWS)

### 5.1 Criar script de túnel automático

No seu **PC Windows**, crie um arquivo `tunel-vps.ps1`:

```powershell
# tunel-vps.ps1
# Túnel SSH Reverso para conectar VPS ao SQL Server local

$VPS_IP = "SEU_IP_VPS"  # Trocar pelo IP da VPS
$VPS_USER = "root"       # Trocar se usar outro usuário

Write-Host "🔗 Criando túnel SSH reverso para VPS..." -ForegroundColor Green
Write-Host "   VPS:1433 -> SQL Server Local (10.1.0.3:1433)" -ForegroundColor Yellow

# -R : Reverse tunnel (VPS:1433 -> Local:1433 -> SQL 10.1.0.3:1433)
# -N : Não executar comandos remotos
# -f : Rodar em background
ssh -R 1433:10.1.0.3:1433 ${VPS_USER}@${VPS_IP} -N

Write-Host "✅ Túnel ativo! Mantenha este terminal aberto." -ForegroundColor Green
```

### 5.2 Executar o túnel

```powershell
# No PowerShell do seu PC:
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"
.\tunel-vps.ps1
```

**Importante:** 
- ✅ Esse script precisa ficar rodando para manter o túnel ativo
- ✅ Use `Task Scheduler` no Windows para iniciar automaticamente com o PC

---

## 🚀 Passo 6: Iniciar Aplicação na VPS

### 6.1 Build e Start

```bash
# Na VPS
cd /opt/valemilk-maps
docker-compose up -d --build
```

### 6.2 Verificar logs

```bash
docker-compose logs -f
```

Você deve ver:
```
🚀 Gerando mapas iniciais...
✅ Todos os mapas iniciais foram gerados!
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:3000
```

---

## 🌍 Passo 7: Acessar Aplicação

### 7.1 Teste direto por IP

```
http://SEU_IP_VPS:3000
```

### 7.2 (Opcional) Configurar domínio

Se tiver um domínio (ex: maps.valemilk.com.br):

1. Apontar DNS A record para IP da VPS
2. Instalar Nginx na VPS:

```bash
apt install nginx -y
cp /opt/valemilk-maps/nginx.conf /etc/nginx/sites-available/valemilk
ln -s /etc/nginx/sites-available/valemilk /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

3. Instalar SSL com Certbot:

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d maps.valemilk.com.br
```

---

## 🔄 Manter Túnel Sempre Ativo (Windows)

### Opção A: Agendador de Tarefas

1. Abra `Task Scheduler` (Agendador de Tarefas)
2. **Create Task** → "VPS Tunnel"
3. **Triggers:** "At system startup"
4. **Actions:** 
   - Program: `powershell.exe`
   - Arguments: `-File "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico\tunel-vps.ps1"`
5. **Conditions:** Desmarcar "Start only if on AC power"

### Opção B: NSSM (Serviço Windows)

```powershell
# Download NSSM
# Instalar como serviço
nssm install VPSTunnel "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" "-File C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico\tunel-vps.ps1"
nssm start VPSTunnel
```

---

## ✅ Checklist Final

- [ ] VPS com Docker instalado
- [ ] Projeto clonado/enviado para `/opt/valemilk-maps`
- [ ] `.env` configurado na VPS
- [ ] Túnel SSH rodando do PC para VPS
- [ ] Container rodando: `docker ps | grep valemilk`
- [ ] Aplicação acessível: `http://SEU_IP_VPS:3000`
- [ ] Mapas carregando corretamente
- [ ] Túnel configurado para iniciar automaticamente

---

## 🆘 Troubleshooting

### Erro: "No module named 'app'"
```bash
cd /opt/valemilk-maps
ls -la app.py  # Verificar se existe
docker-compose logs
```

### Erro: Não conecta no banco
```bash
# Na VPS, testar conexão:
docker exec -it valemilk_app bash
apt update && apt install telnet -y
telnet 127.0.0.1 1433

# Se não conectar, verificar túnel no PC Windows
```

### Túnel SSH perdendo conexão

Adicione ao arquivo `~/.ssh/config` no PC:
```
Host vps-valemilk
    HostName SEU_IP_VPS
    User root
    ServerAliveInterval 30
    ServerAliveCountMax 3
    ExitOnForwardFailure yes
```

Use: `ssh -R 1433:10.1.0.3:1433 vps-valemilk -N`

---

## 📊 Monitoramento

### Ver logs em tempo real
```bash
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

### Ver uso de recursos
```bash
docker stats valemilk_app
```

---

## 🔄 Atualizar Aplicação

```bash
# Na VPS
cd /opt/valemilk-maps
git pull  # ou enviar arquivos via SCP
docker-compose down
docker-compose up -d --build
```

---

## 💡 Alternativas ao Túnel SSH

### Opção 2: Tailscale (VPN Simples)

**Vantagens:** Mais estável, não precisa manter túnel manualmente

1. Instalar Tailscale no PC e na VPS
2. Conectar ambos na mesma rede Tailscale
3. Usar IP Tailscale do PC no `.env` da VPS

**No PC Windows:**
```powershell
# Download: https://tailscale.com/download/windows
# Instalar e criar conta
```

**Na VPS:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

Depois use o IP Tailscale do PC (ex: 100.x.x.x) no `.env`:
```env
DB_SERVER=100.x.x.x\SQLSTANDARD
```

### Opção 3: ZeroTier (Similar ao Tailscale)

Processo similar ao Tailscale.

---

## 📞 Suporte

Em caso de dúvidas:
1. Verificar logs: `docker-compose logs -f`
2. Testar conexão de rede
3. Verificar firewall da VPS
4. Confirmar que túnel está ativo

---

**Boa sorte com o deploy! 🚀**
