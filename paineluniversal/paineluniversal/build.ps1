# Script de Build Universal para Sistema de Eventos - PowerShell
# Constrói frontend e backend para produção

Write-Host "🏗️  Iniciando build do Sistema Universal..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Timestamp
$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# 1. Build do Frontend
Write-Host "[$Timestamp] 📦 Construindo Frontend..." -ForegroundColor Yellow
Write-Host "[$Timestamp] Instalando dependências do frontend..." -ForegroundColor White

Set-Location frontend

# Verificar se o package.json existe
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json não encontrado no diretório frontend!" -ForegroundColor Red
    exit 1
}

# Instalar dependências (pular se já existir node_modules)
if (-not (Test-Path "node_modules")) {
    Write-Host "[$Timestamp] Instalando dependências npm..." -ForegroundColor White
    npm install
} else {
    Write-Host "[$Timestamp] Dependências já instaladas, pulando npm install..." -ForegroundColor Green
}

# Build de produção
Write-Host "[$Timestamp] Executando build de produção..." -ForegroundColor White
$buildOutput = npm run build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[$Timestamp] ✅ Frontend construído com sucesso!" -ForegroundColor Green
    Write-Host "[$Timestamp] Arquivos de produção gerados em frontend/dist/" -ForegroundColor Green
    
    # Verificar se os arquivos foram gerados
    if (Test-Path "dist") {
        Write-Host "[$Timestamp] 📋 Principais arquivos gerados:" -ForegroundColor Cyan
        Get-ChildItem dist/ -Recurse | Where-Object { $_.Extension -in @('.html', '.js', '.css') } | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}} | Format-Table
        $distSize = (Get-ChildItem -Recurse dist/ | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "[$Timestamp] 📊 Tamanho total do build: $([math]::Round($distSize, 2)) MB" -ForegroundColor Cyan
    } else {
        Write-Host "[WARNING] Diretório dist não encontrado!" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] Falha no build do frontend" -ForegroundColor Red
    Write-Host $buildOutput -ForegroundColor Red
    exit 1
}

Set-Location ..

# 2. Verificação do Backend
Write-Host "[$Timestamp] 🐍 Verificando Backend..." -ForegroundColor Yellow

Set-Location backend

# Verificar se os arquivos principais existem
$RequiredFiles = @("app/main.py", "requirements.txt")
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[ERROR] Arquivo obrigatório não encontrado: $file" -ForegroundColor Red
        exit 1
    }
}

# Verificar se o ambiente virtual Python está ativo ou se as dependências estão instaladas
Write-Host "[$Timestamp] Verificando dependências do Python..." -ForegroundColor White

# Tentar importar o app principal
$pythonTest = python -c "import app.main; print('✅ Backend importado com sucesso')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[$Timestamp] ✅ Backend validado com sucesso!" -ForegroundColor Green
    
    # Listar algumas dependências instaladas
    Write-Host "[$Timestamp] 📋 Principais dependências Python:" -ForegroundColor Cyan
    $pipList = pip list | Select-String "fastapi|uvicorn|sqlalchemy|pydantic|python-dotenv"
    $pipList | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    
    $totalPackages = (pip list | Measure-Object).Count - 2
    Write-Host "[$Timestamp] Total de pacotes instalados: $totalPackages" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Falha na importação do backend" -ForegroundColor Red
    Write-Host "[INFO] Tentando instalar dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # Tentar novamente
    $pythonTestRetry = python -c "import app.main; print('✅ Backend importado após instalação')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[$Timestamp] ✅ Backend validado após instalação de dependências!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Backend ainda apresenta problemas após instalação" -ForegroundColor Red
        Write-Host $pythonTestRetry -ForegroundColor Red
        exit 1
    }
}

Set-Location ..

# 3. Resumo Final
Write-Host ""
Write-Host "🎉 BUILD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "[$Timestamp] ✅ Frontend: Construído e otimizado" -ForegroundColor Green
Write-Host "[$Timestamp] ✅ Backend: Validado e pronto" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Estrutura de produção:" -ForegroundColor Cyan
Write-Host "   frontend/dist/     - Arquivos estáticos para deploy" -ForegroundColor White
Write-Host "   backend/           - API Python pronta para execução" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Deploy do frontend: Enviar pasta frontend/dist/ para Railway/Vercel" -ForegroundColor White
Write-Host "   2. Deploy do backend: Configurar ambiente Python no Railway" -ForegroundColor White
Write-Host "   3. Configurar variáveis de ambiente de produção" -ForegroundColor White
Write-Host ""
Write-Host "⚡ Sistema pronto para deploy em produção!" -ForegroundColor Magenta
