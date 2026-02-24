# ========================================
# SCRIPT DE ENVIO PARA VPS - VERSÃO SIMPLIFICADA
# ========================================
# Este script envia o projeto completo para a VPS via SCP
# Como a VPS já tem VPN, não precisa de túnel SSH!
#
# COMO USAR:
# 1. Configurar IP da VPS abaixo
# 2. Executar: .\enviar-para-vps.ps1
#
# ========================================

# ========== CONFIGURAÇÕES ==========
$VPS_IP = "SEU_IP_VPS_AQUI"          # Trocar pelo IP da VPS Hostinger
$VPS_USER = "root"                    # Trocar se usar outro usuário
$VPS_PATH = "/opt/valemilk-maps"      # Caminho na VPS
# ===================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         📦 ENVIAR PROJETO PARA VPS - Vale Milk Maps          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Validar configuração
if ($VPS_IP -eq "SEU_IP_VPS_AQUI") {
    Write-Host "❌ ERRO: Configure o IP da VPS neste arquivo primeiro!" -ForegroundColor Red
    Write-Host "   Abra enviar-para-vps.ps1 e altere a linha:" -ForegroundColor Yellow
    Write-Host '   $VPS_IP = "SEU_IP_DA_VPS"' -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

$projectPath = $PSScriptRoot

Write-Host "📋 Configuração:" -ForegroundColor Green
Write-Host "   Origem : $projectPath" -ForegroundColor White
Write-Host "   Destino: ${VPS_USER}@${VPS_IP}:${VPS_PATH}" -ForegroundColor White
Write-Host ""

# Arquivos a incluir (excluir cache e arquivos temporários)
$tempZip = Join-Path $env:TEMP "valemilk-maps-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"

Write-Host "📁 Preparando arquivos para envio..." -ForegroundColor Yellow
Write-Host "   Criando arquivo ZIP temporário..." -ForegroundColor Gray

# Criar lista de arquivos a incluir
$filesToInclude = Get-ChildItem -Path $projectPath -Exclude @(
    "__pycache__",
    "*.pyc",
    ".git",
    "*.log",
    "mapa_*.html",
    "valemilk-maps*.zip"
) -Recurse | Where-Object { 
    $_.FullName -notmatch "__pycache__" -and
    $_.FullName -notmatch "\.git" -and
    $_.Extension -ne ".pyc"
}

# Criar ZIP
try {
    Compress-Archive -Path (Get-ChildItem -Path $projectPath -Exclude @("__pycache__", ".git", "*.pyc", "mapa_*.html") | Select-Object -ExpandProperty FullName) -DestinationPath $tempZip -Force
    Write-Host "✅ Arquivo ZIP criado: $tempZip" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao criar ZIP: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "📊 Tamanho do arquivo: $([math]::Round((Get-Item $tempZip).Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""

# Confirmar envio
$confirm = Read-Host "Deseja enviar para ${VPS_USER}@${VPS_IP}? (s/n)"
if ($confirm -ne "s") {
    Write-Host "❌ Cancelado pelo usuário." -ForegroundColor Yellow
    Remove-Item $tempZip -Force
    exit 0
}

Write-Host ""
Write-Host "🚀 Enviando arquivos..." -ForegroundColor Green
Write-Host ""

# Criar diretório na VPS
Write-Host "📂 Criando diretório na VPS..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} "mkdir -p ${VPS_PATH}"

# Enviar ZIP
Write-Host "📤 Enviando arquivo ZIP..." -ForegroundColor Yellow
scp $tempZip ${VPS_USER}@${VPS_IP}:${VPS_PATH}/valemilk-maps.zip

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Arquivo enviado!" -ForegroundColor Green
    
    # Descompactar na VPS
    Write-Host ""
    Write-Host "📦 Descompactando na VPS..." -ForegroundColor Yellow
    ssh ${VPS_USER}@${VPS_IP} "cd ${VPS_PATH} && unzip -o valemilk-maps.zip && rm valemilk-maps.zip"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Arquivos descompactados com sucesso!" -ForegroundColor Green
        
        # Limpar arquivo temporário local
        Remove-Item $tempZip -Force
        
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║                    ✅ ENVIO CONCLUÍDO!                        ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1️⃣  Conectar na VPS:" -ForegroundColor Yellow
        Write-Host "   ssh ${VPS_USER}@${VPS_IP}" -ForegroundColor White
        Write-Host ""
        Write-Host "2️⃣  Executar deploy:" -ForegroundColor Yellow
        Write-Host "   cd ${VPS_PATH}" -ForegroundColor White
        Write-Host "   chmod +x deploy-vps.sh" -ForegroundColor White
        Write-Host "   bash deploy-vps.sh" -ForegroundColor White
        Write-Host ""
        Write-Host "3️⃣  Acessar aplicação:" -ForegroundColor Yellow
        Write-Host "   http://${VPS_IP}:3000" -ForegroundColor White
        Write-Host ""
        
    } else {
        Write-Host "❌ Erro ao descompactar na VPS" -ForegroundColor Red
    }
    
} else {
    Write-Host ""
    Write-Host "❌ Erro ao enviar arquivos. Código: $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
    Remove-Item $tempZip -Force
}

Write-Host ""
pause
