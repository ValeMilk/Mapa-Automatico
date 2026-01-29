# Script para rodar o Mapa Geral otimizado

Write-Host "🚀 Parando container antigo (se existir)..." -ForegroundColor Cyan
docker-compose -f docker-compose.mapageral.yml down 2>$null

Write-Host ""
Write-Host "🔨 Construindo e iniciando Mapa Geral otimizado..." -ForegroundColor Cyan
docker-compose -f docker-compose.mapageral.yml up -d --build

Write-Host ""
Write-Host "⏳ Aguardando inicialização (20s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "📋 Logs do container:" -ForegroundColor Cyan
docker logs mapa_geral_app --tail 30

Write-Host ""
Write-Host "✅ Mapa Geral disponível em: http://10.1.1.115:8000/" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos úteis:" -ForegroundColor Yellow
Write-Host "  Ver logs:      docker logs mapa_geral_app -f"
Write-Host "  Reiniciar:     docker-compose -f docker-compose.mapageral.yml restart"
Write-Host "  Parar:         docker-compose -f docker-compose.mapageral.yml down"
