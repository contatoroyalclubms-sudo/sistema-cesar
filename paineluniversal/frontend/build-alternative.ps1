# Script de Build Alternativo
# Build com timeout e fallback

Write-Host "🏗️ Iniciando build do frontend..." -ForegroundColor Cyan

# Limpar cache
Write-Host "🧹 Limpando cache..." -ForegroundColor Yellow
Remove-Item node_modules\.vite -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item dist -Recurse -Force -ErrorAction SilentlyContinue

# Verificar se existe package.json
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json não encontrado!" -ForegroundColor Red
    exit 1
}

# Build com timeout de 3 minutos
Write-Host "📦 Executando build com timeout..." -ForegroundColor Yellow

$buildJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run build 2>&1
}

if (Wait-Job $buildJob -Timeout 180) {
    $output = Receive-Job $buildJob
    Remove-Job $buildJob
    
    if ($output -like "*built in*" -or (Test-Path "dist")) {
        Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
        
        if (Test-Path "dist") {
            $distFiles = Get-ChildItem dist -Recurse | Measure-Object
            Write-Host "📊 Arquivos gerados: $($distFiles.Count)" -ForegroundColor Cyan
            
            $distSize = (Get-ChildItem -Recurse dist | Measure-Object -Property Length -Sum).Sum / 1MB
            Write-Host "📊 Tamanho total: $([math]::Round($distSize, 2)) MB" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Build falhou!" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⏰ Build timeout - parando processo..." -ForegroundColor Yellow
    Stop-Job $buildJob
    Remove-Job $buildJob
    
    Write-Host "🔧 Tentando build alternativo sem otimizações..." -ForegroundColor Yellow
    
    # Build manual sem otimizações
    $env:NODE_ENV="production"
    $buildResult = npx vite build --minify=false --sourcemap=false --mode=production 2>&1
    
    if (Test-Path "dist") {
        Write-Host "✅ Build alternativo concluído!" -ForegroundColor Green
    } else {
        Write-Host "❌ Build alternativo também falhou!" -ForegroundColor Red
        Write-Host $buildResult -ForegroundColor Red
        exit 1
    }
}

Write-Host "🎉 Frontend pronto para deploy!" -ForegroundColor Green
