# ========================================
# GIT COMMIT E PUSH RÁPIDO
# ========================================
# Script para facilitar commits e pushes no GitHub
#
# Uso: .\git-push.ps1 "mensagem do commit"
# ========================================

param(
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage
)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              📤 Git Push - Vale Milk Maps                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se está em um repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "❌ ERRO: Este não é um repositório Git!" -ForegroundColor Red
    Write-Host "   Execute 'git init' primeiro." -ForegroundColor Yellow
    exit 1
}

# Status
Write-Host "📊 Status atual:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Verificar se há mudanças
$changes = git status --porcelain
if (-not $changes) {
    Write-Host "✅ Nenhuma mudança para commitar." -ForegroundColor Green
    exit 0
}

# Pedir mensagem de commit se não foi fornecida
if (-not $CommitMessage) {
    Write-Host "📝 Digite a mensagem do commit:" -ForegroundColor Cyan
    $CommitMessage = Read-Host "Mensagem"
    
    if (-not $CommitMessage) {
        Write-Host "❌ Mensagem vazia. Cancelado." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔍 Mudanças a serem commitadas:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Confirmar
$confirm = Read-Host "Deseja continuar com o commit e push? (s/n)"
if ($confirm -ne "s") {
    Write-Host "❌ Cancelado pelo usuário." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "📦 Adicionando arquivos..." -ForegroundColor Yellow
git add .

Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m "$CommitMessage"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer commit!" -ForegroundColor Red
    exit 1
}

Write-Host "📤 Enviando para GitHub..." -ForegroundColor Yellow
git push

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                  ✅ PUSH CONCLUÍDO!                           ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Repositório atualizado no GitHub!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Para atualizar na VPS, execute:" -ForegroundColor Yellow
    Write-Host "   ssh root@IP_VPS" -ForegroundColor White
    Write-Host "   cd /opt/valemilk-maps" -ForegroundColor White
    Write-Host "   bash atualizar.sh" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push!" -ForegroundColor Red
    Write-Host "   Verifique suas credenciais e conexão." -ForegroundColor Yellow
    exit 1
}
