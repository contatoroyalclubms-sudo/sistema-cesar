# Script de Build Simples
Write-Host "🏗️ Iniciando build do frontend..." -ForegroundColor Cyan

# Limpar dist anterior
if (Test-Path "dist") {
    Remove-Item dist -Recurse -Force
    Write-Host "🧹 Diretório dist limpo" -ForegroundColor Yellow
}

# Limpar cache do vite
if (Test-Path "node_modules\.vite") {
    Remove-Item node_modules\.vite -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "🧹 Cache do Vite limpo" -ForegroundColor Yellow
}

Write-Host "📦 Executando build..." -ForegroundColor Yellow

# Build básico
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build

if (Test-Path "dist") {
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
    
    # Estatísticas
    $files = Get-ChildItem dist -Recurse
    $totalFiles = $files.Count
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1MB
    
    Write-Host "📊 Arquivos gerados: $totalFiles" -ForegroundColor Cyan
    Write-Host "📊 Tamanho total: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
    
    Write-Host "🎉 Frontend pronto para deploy!" -ForegroundColor Green
} else {
    Write-Host "❌ Build falhou - diretório dist não foi criado" -ForegroundColor Red
}
