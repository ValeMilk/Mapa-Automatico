# 🚀 Deploy Rápido - VPS com VPN

## ✅ Sua Situação

- ✅ VPS Hostinger já conectada via VPN ao SQL Server (10.1.0.3)
- ✅ Não precisa de túnel SSH
- ✅ Deploy direto e simples

---

## 📦 Passo 1: Enviar Arquivos

**No seu PC Windows (PowerShell):**

```powershell
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"

# Criar arquivo compactado (excluindo cache)
$exclude = @("__pycache__", "*.pyc", ".git")
Compress-Archive -Path * -DestinationPath valemilk-maps.zip -Force

# Enviar para VPS via SCP
scp valemilk-maps.zip root@IP_DA_VPS:/opt/
```

**Ou use WinSCP/FileZilla para copiar a pasta inteira para `/opt/valemilk-maps`**

---

## 🚀 Passo 2: Deploy na VPS

**Conectar na VPS:**

```bash
ssh root@IP_DA_VPS
```

**Descompactar e executar script:**

```bash
# Criar diretório
mkdir -p /opt/valemilk-maps
cd /opt

# Descompactar
unzip valemilk-maps.zip -d valemilk-maps
cd valemilk-maps

# Executar script de deploy
chmod +x deploy-vps.sh
bash deploy-vps.sh
```

O script vai:
- ✅ Verificar conexão com 10.1.0.3
- ✅ Instalar Docker (se necessário)
- ✅ Criar arquivo .env automaticamente
- ✅ Fazer build e iniciar aplicação

---

## 🌐 Pronto!

Acesse: `http://IP_DA_VPS:3000`

---

## 📋 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Status
docker-compose ps
```

---

## 🔄 Atualizar Código

Quando fizer alterações:

```powershell
# No PC Windows
scp app.py root@IP_VPS:/opt/valemilk-maps/
scp MapaAutomatico.py root@IP_VPS:/opt/valemilk-maps/
```

```bash
# Na VPS
cd /opt/valemilk-maps
docker-compose restart
```

---

## 📖 Documentação Completa

Ver: [DEPLOY_VPS_SIMPLES.md](DEPLOY_VPS_SIMPLES.md)
