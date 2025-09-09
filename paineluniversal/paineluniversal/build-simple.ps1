# Script de Build Universal para Sistema de Eventos
# Constroi frontend e backend para producao

Write-Host "Iniciando build do Sistema Universal..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# 1. Build do Frontend
Write-Host "[$Timestamp] Construindo Frontend..." -ForegroundColor Yellow

Set-Location frontend

if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json nao encontrado!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "node_modules")) {
    Write-Host "[$Timestamp] Instalando dependencias npm..." -ForegroundColor White
    npm install
} else {
    Write-Host "[$Timestamp] Dependencias ja instaladas..." -ForegroundColor Green
}

Write-Host "[$Timestamp] Executando build de producao..." -ForegroundColor White
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "[$Timestamp] Frontend construido com sucesso!" -ForegroundColor Green
    
    if (Test-Path "dist") {
        Write-Host "[$Timestamp] Arquivos principais gerados:" -ForegroundColor Cyan
        Get-ChildItem dist/ -Recurse | Where-Object { $_.Extension -in @('.html', '.js', '.css') } | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}} -First 10 | Format-Table
        $distSize = (Get-ChildItem -Recurse dist/ | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "[$Timestamp] Tamanho total: $([math]::Round($distSize, 2)) MB" -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] Falha no build do frontend" -ForegroundColor Red
    exit 1
}

Set-Location ..

# 2. Verificacao do Backend
Write-Host "[$Timestamp] Verificando Backend..." -ForegroundColor Yellow

Set-Location backend

$RequiredFiles = @("app/main.py", "requirements.txt")
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[ERROR] Arquivo obrigatorio nao encontrado: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[$Timestamp] Verificando dependencias do Python..." -ForegroundColor White

$pythonTest = python -c "import app.main; print('Backend importado com sucesso')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[$Timestamp] Backend validado com sucesso!" -ForegroundColor Green
    
    Write-Host "[$Timestamp] Principais dependencias Python:" -ForegroundColor Cyan
    $pipList = pip list | Select-String "fastapi|uvicorn|sqlalchemy|pydantic|python-dotenv"
    $pipList | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    
    $totalPackages = (pip list | Measure-Object).Count - 2
    Write-Host "[$Timestamp] Total de pacotes instalados: $totalPackages" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Falha na importacao do backend" -ForegroundColor Red
    Write-Host "[INFO] Tentando instalar dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    $pythonTestRetry = python -c "import app.main; print('Backend importado apos instalacao')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[$Timestamp] Backend validado apos instalacao!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Backend ainda apresenta problemas" -ForegroundColor Red
        exit 1
    }
}

Set-Location ..

# 3. Resumo Final
Write-Host ""
Write-Host "BUILD CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "[$Timestamp] Frontend: Construido e otimizado" -ForegroundColor Green
Write-Host "[$Timestamp] Backend: Validado e pronto" -ForegroundColor Green
Write-Host ""
Write-Host "Estrutura de producao:" -ForegroundColor Cyan
Write-Host "   frontend/dist/     - Arquivos estaticos para deploy" -ForegroundColor White
Write-Host "   backend/           - API Python pronta para execucao" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "   1. Deploy do frontend: Enviar pasta frontend/dist/ para Railway/Vercel" -ForegroundColor White
Write-Host "   2. Deploy do backend: Configurar ambiente Python no Railway" -ForegroundColor White
Write-Host "   3. Configurar variaveis de ambiente de producao" -ForegroundColor White
Write-Host ""
Write-Host "Sistema pronto para deploy em producao!" -ForegroundColor Magenta
