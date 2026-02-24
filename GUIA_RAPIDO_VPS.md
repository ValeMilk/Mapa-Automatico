# 🚀 Guia Rápido - Deploy VPS Hostinger

## ⚡ Resumo em 5 Passos

### 1️⃣ **Editar tunel-vps.ps1** (neste PC)
```powershell
$VPS_IP = "45.67.89.123"  # Trocar pelo IP da sua VPS
```

### 2️⃣ **Enviar projeto para VPS**
```powershell
# Opção A: Se tiver Git na VPS
# ssh root@VPS_IP
# cd /opt && git clone https://...

# Opção B: Enviar via SCP
.\enviar-para-vps.ps1  # Ou copiar manualmente
```

### 3️⃣ **Configurar .env na VPS**
```bash
# Na VPS via SSH
cd /opt/valemilk-maps
nano .env
```

Cole:
```env
DB_SERVER=127.0.0.1\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@
APP_PORT=3000
FLASK_ENV=production
```

### 4️⃣ **Iniciar túnel** (neste PC - manter aberto!)
```powershell
.\tunel-vps.ps1
```

### 5️⃣ **Subir aplicação na VPS**
```bash
# Na VPS
docker-compose up -d --build
docker-compose logs -f
```

## 🌐 Acessar

```
http://SEU_IP_VPS:3000
```

## 📖 Guia Completo

Ver: [DEPLOY_VPS.md](DEPLOY_VPS.md)

## ⚠️ Importante

- ✅ Túnel precisa ficar ativo (configure como serviço Windows)
- ✅ PC precisa estar ligado para app acessar banco
- ✅ Alternativa: Use Tailscale VPN (mais estável)

## 🆘 Problemas?

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Testar conexão banco
docker exec -it valemilk_app bash
telnet 127.0.0.1 1433
```
