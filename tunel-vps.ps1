# ========================================
# TÚNEL SSH REVERSO - VPS HOSTINGER
# ========================================
# Este script cria um túnel SSH reverso permitindo que a VPS
# acesse o SQL Server local através da porta 1433
#
# COMO USAR:
# 1. Editar variáveis abaixo com IP e usuário da VPS
# 2. Executar: .\tunel-vps.ps1
# 3. Manter terminal aberto (ou configurar como serviço)
#
# ========================================

# ========== CONFIGURAÇÕES ==========
$VPS_IP = "SEU_IP_VPS_AQUI"          # Trocar pelo IP da VPS Hostinger
$VPS_USER = "root"                    # Trocar se usar outro usuário
$SQL_SERVER_LOCAL = "10.1.0.3"       # IP do SQL Server na rede local
$SQL_PORT = "1433"                    # Porta do SQL Server
# ===================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🔗 TÚNEL SSH REVERSO - Vale Milk Maps VPS               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Validar se variáveis foram configuradas
if ($VPS_IP -eq "SEU_IP_VPS_AQUI") {
    Write-Host "❌ ERRO: Você precisa editar este arquivo e definir o IP da VPS!" -ForegroundColor Red
    Write-Host "   Abra o arquivo tunel-vps.ps1 e altere a linha:" -ForegroundColor Yellow
    Write-Host '   $VPS_IP = "SEU_IP_DA_VPS"' -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "📋 Configuração do Túnel:" -ForegroundColor Green
Write-Host "   VPS Destino    : $VPS_USER@$VPS_IP" -ForegroundColor White
Write-Host "   SQL Server Local: $SQL_SERVER_LOCAL`:$SQL_PORT" -ForegroundColor White
Write-Host "   Mapeamento      : VPS:1433 -> Local SQL Server" -ForegroundColor White
Write-Host ""

# Verificar se SSH está disponível
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshPath) {
    Write-Host "❌ ERRO: SSH não encontrado!" -ForegroundColor Red
    Write-Host "   Instale o OpenSSH Client em: Configurações > Aplicativos > Recursos Opcionais" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "🔍 Verificando conexão com a VPS..." -ForegroundColor Yellow

# Testar conexão SSH
$testConnection = Test-Connection -ComputerName $VPS_IP -Count 2 -Quiet
if (-not $testConnection) {
    Write-Host "⚠️  AVISO: Não foi possível fazer ping na VPS ($VPS_IP)" -ForegroundColor Yellow
    Write-Host "   Continuando mesmo assim (firewall pode bloquear ICMP)..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "🚀 Iniciando túnel SSH reverso..." -ForegroundColor Green
Write-Host "   Você pode precisar inserir a senha SSH da VPS." -ForegroundColor Gray
Write-Host ""
Write-Host "   MANTENHA ESTA JANELA ABERTA!" -ForegroundColor Yellow
Write-Host "   Para parar, pressione Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Criar túnel SSH reverso
# -R 1433:10.1.0.3:1433 = Mapeia porta 1433 da VPS para SQL Server local
# -N = Não executar comandos remotos
# -v = Verbose (remover o -v para menos logs)
# -o ServerAliveInterval=30 = Manter conexão viva
# -o ServerAliveCountMax=3 = Reconectar automaticamente

try {
    ssh -R ${SQL_PORT}:${SQL_SERVER_LOCAL}:${SQL_PORT} `
        ${VPS_USER}@${VPS_IP} `
        -N `
        -o ServerAliveInterval=30 `
        -o ServerAliveCountMax=3 `
        -o ExitOnForwardFailure=yes
}
catch {
    Write-Host ""
    Write-Host "❌ Erro ao criar túnel: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "✅ Túnel encerrado." -ForegroundColor Green
