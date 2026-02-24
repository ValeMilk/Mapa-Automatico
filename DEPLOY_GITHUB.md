# 🚀 Deploy Via GitHub - Guia Completo

## 📋 Passos Resumidos

1. ✅ Criar repositório no GitHub
2. ✅ Fazer push do código
3. ✅ Clonar na VPS
4. ✅ Configurar .env
5. ✅ Rodar aplicação

---

## 1️⃣ Subir Código no GitHub

### **No seu PC (PowerShell):**

```powershell
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"

# Inicializar Git (se ainda não tiver)
git init

# Adicionar todos os arquivos
git add .

# Fazer primeiro commit
git commit -m "🚀 Initial commit - Vale Milk Maps"

# Criar repositório no GitHub primeiro:
# https://github.com/new
# Nome sugerido: valemilk-maps

# Adicionar remote (trocar SEU_USUARIO pelo seu usuário GitHub)
git remote add origin https://github.com/SEU_USUARIO/valemilk-maps.git

# Push para GitHub
git branch -M main
git push -u origin main
```

### **⚠️ IMPORTANTE: Segurança**

O arquivo `.gitignore` já está configurado para **NÃO** enviar:
- ✅ Mapas gerados (`mapa_*.html`)
- ✅ Cache Python (`__pycache__`)
- ✅ Arquivos temporários
- ⚠️ **NUNCA suba o arquivo `.env` com senhas reais!**

Criamos um `.env.example` que vai para o GitHub sem dados sensíveis.

---

## 2️⃣ Deploy na VPS via Git

### **Conectar na VPS:**

```bash
ssh root@IP_DA_VPS
```

### **Instalar Git (se necessário):**

```bash
apt update
apt install git -y
git --version
```

### **Clonar Repositório:**

```bash
# Ir para diretório de projetos
cd /opt

# Clonar do GitHub (trocar SEU_USUARIO)
git clone https://github.com/SEU_USUARIO/valemilk-maps.git

# Entrar no diretório
cd valemilk-maps
```

### **Configurar Ambiente:**

```bash
# Copiar exemplo para .env
cp .env.example .env

# Editar com dados reais
nano .env
```

Cole as credenciais reais:

```env
DB_SERVER=10.1.0.3\SQLSTANDARD
DB_NAME=dbactions
DB_USER=analistarpt
DB_PASSWORD=mM=DU9lUd3C$qb@

APP_PORT=3000
FLASK_ENV=production
COMPRESS_LEVEL=6
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

### **Verificar Conexão SQL:**

```bash
# Testar se VPS alcança o SQL Server
ping 10.1.0.3 -c 2
```

### **Instalar Docker (se necessário):**

```bash
# Verificar se já tem
docker --version

# Se não tiver, instalar:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### **Iniciar Aplicação:**

```bash
# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

Aguarde ver:
```
✅ Todos os mapas iniciais foram gerados!
[INFO] Listening at: http://0.0.0.0:3000
```

**Pressione Ctrl+C para sair dos logs**

---

## 🌐 Acessar Aplicação

```
http://IP_DA_VPS:3000
```

---

## 🔄 Atualizar Aplicação (quando fizer mudanças)

### **No PC (após editar código):**

```powershell
cd "C:\Users\PC 0025\Desktop\Nicolas\mapaotimizado automatico"

# Adicionar mudanças
git add .

# Commit
git commit -m "✨ Descrição das mudanças"

# Push
git push
```

### **Na VPS (para atualizar):**

```bash
cd /opt/valemilk-maps

# Baixar atualizações
git pull

# Reiniciar aplicação
docker-compose down
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

---

## 🎯 Script de Deploy Automático

Crie um arquivo `atualizar.sh` na VPS:

```bash
nano /opt/valemilk-maps/atualizar.sh
```

Cole:

```bash
#!/bin/bash
cd /opt/valemilk-maps
echo "📥 Baixando atualizações..."
git pull
echo "🔄 Reiniciando aplicação..."
docker-compose down
docker-compose up -d --build
echo "✅ Atualização concluída!"
docker-compose ps
```

Tornar executável:

```bash
chmod +x /opt/valemilk-maps/atualizar.sh
```

**Uso:** Sempre que atualizar o GitHub, rode na VPS:

```bash
/opt/valemilk-maps/atualizar.sh
```

---

## 🔐 Repositório Privado vs Público

### **Se for repositório PÚBLICO:**
- ⚠️ **NUNCA** faça commit do arquivo `.env` com senhas
- ✅ Use sempre `.env.example` com valores fake
- ✅ Configure `.gitignore` (já está pronto)

### **Se for repositório PRIVADO:**
- ✅ Mais seguro, mas ainda assim use `.env.example`
- ✅ Mantenha `.env` no `.gitignore`
- ✅ Considere usar GitHub Actions para deploy automático

---

## 🔑 Autenticação GitHub

### **Opção 1: HTTPS com Token (Recomendado)**

1. Criar Personal Access Token:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token
   - Selecionar `repo` scope
   - Copiar token

2. Ao fazer `git push`, usar:
   - Username: seu_usuario
   - Password: token_copiado

### **Opção 2: SSH (Mais fácil para VPS)**

**Na VPS:**

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "vps@valemilk"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub
```

**No GitHub:**
- Settings → SSH and GPG keys → New SSH key
- Colar a chave pública

**Usar URL SSH ao clonar:**

```bash
git clone git@github.com:SEU_USUARIO/valemilk-maps.git
```

---

## 📁 Estrutura Recomendada no GitHub

```
valemilk-maps/
├── .gitignore                    ← Ignora arquivos sensíveis
├── .env.example                  ← Exemplo sem senhas
├── README.md                     ← Documentação principal
├── DEPLOY_VPS_SIMPLES.md        ← Guia de deploy
├── LEIA-ME-VPS.md               ← Guia rápido
├── app.py                        ← Aplicação Flask
├── MapaAutomatico.py            ← Gerador de mapas 1-5
├── mapa_geral_module.py         ← Mapa geral (tipo 6)
├── requirements.txt              ← Dependências Python
├── docker-compose.yml           ← Orquestração Docker
├── Dockerfile                    ← Imagem Docker
├── deploy-vps.sh                ← Script de deploy
├── atualizar.sh                 ← Script de atualização
├── ROTA SEMANA.csv              ← Dados de rotas
├── nginx.conf                    ← Configuração Nginx
└── static/
    └── logo_valemilk.png        ← Logo
```

---

## 🎨 README.md no GitHub

O arquivo `README.md` atual já está ótimo! Ele será exibido na página principal do repositório.

---

## ✅ Checklist Final

- [ ] Arquivo `.gitignore` criado
- [ ] Arquivo `.env.example` criado (sem senhas)
- [ ] Repositório criado no GitHub
- [ ] Código enviado via `git push`
- [ ] VPS com acesso ao GitHub configurado
- [ ] Projeto clonado na VPS via `git clone`
- [ ] Arquivo `.env` configurado na VPS (com senhas reais)
- [ ] Docker instalado na VPS
- [ ] Aplicação rodando: `docker-compose up -d --build`
- [ ] Acesso funcionando: `http://IP_VPS:3000`

---

## 🆘 Problemas Comuns

### Erro: "Permission denied (publickey)"

Configurar SSH key ou usar HTTPS com token.

### Erro: Git não encontra repositório

Verificar URL do remote:
```bash
git remote -v
```

Corrigir se necessário:
```bash
git remote set-url origin https://github.com/SEU_USUARIO/valemilk-maps.git
```

### Erro: Conflitos ao fazer git pull

```bash
# Ver status
git status

# Descartar mudanças locais
git reset --hard origin/main

# Ou fazer stash
git stash
git pull
git stash pop
```

---

## 🚀 Próximos Passos (Opcional)

1. **GitHub Actions** - Deploy automático ao fazer push
2. **Webhook** - VPS atualiza automaticamente
3. **Domínio + SSL** - HTTPS com Let's Encrypt
4. **Monitoramento** - Uptime Robot ou similar

---

**Pronto! Agora você tem um workflow profissional de deploy via Git! 🎉**
