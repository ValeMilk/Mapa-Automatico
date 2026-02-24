# 🎯 GUIA RÁPIDO: Subir no GitHub e Deploy

## 📤 1. Subir no GitHub (no seu PC)

```powershell
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"

# Inicializar Git (se ainda não tiver)
git init

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "🚀 Initial commit - Vale Milk Maps"

# Criar repositório no GitHub:
# Acesse: https://github.com/new
# Nome: valemilk-maps
# Tipo: Private (recomendado) ou Public

# Conectar ao GitHub (trocar SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/valemilk-maps.git
git branch -M main
git push -u origin main
```

## 📥 2. Deploy na VPS

```bash
# Conectar na VPS
ssh root@IP_DA_VPS

# Clonar repositório (trocar SEU_USUARIO)
cd /opt
git clone https://github.com/SEU_USUARIO/valemilk-maps.git
cd valemilk-maps

# Configurar credenciais
cp .env.example .env
nano .env  # Colocar senha real do SQL Server

# Executar deploy
chmod +x deploy-vps.sh
bash deploy-vps.sh
```

## 🌐 3. Acessar

```
http://IP_DA_VPS:3000
```

## 🔄 4. Atualizar depois (quando fizer mudanças)

**No PC:**
```powershell
git add .
git commit -m "✨ Descrição da mudança"
git push
```

**Na VPS:**
```bash
cd /opt/valemilk-maps
bash atualizar.sh
```

---

**Pronto! 🎉**

Documentação completa: [DEPLOY_GITHUB.md](DEPLOY_GITHUB.md)
