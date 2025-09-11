# Script completo para configurar Git e conectar ao repositório GitHub
# Sistema Cesar - Configuração Completa para Deploy

Write-Host "🚀 Iniciando configuração completa do Git para o Sistema Cesar..." -ForegroundColor Green

# Navegar para o diretório correto
Set-Location "c:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal"

# Verificar se Git está instalado
Write-Host "📋 Verificando instalação do Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Git não encontrado! Instale o Git primeiro." -ForegroundColor Red
    exit 1
}

# Configurar credenciais globais do Git
Write-Host "🔧 Configurando credenciais globais do Git..." -ForegroundColor Yellow
git config --global user.name "contatoroyalclubms-sudo"
git config --global user.email "contatoroyalclubms@gmail.com"

# Configurar autenticação por token
Write-Host "🔐 Configurando autenticação..." -ForegroundColor Yellow
git config --global credential.helper manager-core

# Inicializar repositório se não existir
if (-not (Test-Path ".git")) {
    Write-Host "📁 Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    git branch -M main
}
else {
    Write-Host "✅ Repositório Git já existe" -ForegroundColor Green
}

# Configurar remote origin
Write-Host "🔗 Configurando remote origin..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/contatoroyalclubms-sudo/sistema-cesar.git

# Verificar conexão
Write-Host "🔍 Verificando conexão com o repositório..." -ForegroundColor Yellow
try {
    git remote -v
    Write-Host "✅ Remote configurado com sucesso!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erro ao configurar remote" -ForegroundColor Red
}

# Criar .gitignore se não existir
if (-not (Test-Path ".gitignore")) {
    Write-Host "📝 Criando .gitignore..." -ForegroundColor Yellow
    @"
# Dependências
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Arquivos do sistema
.DS_Store
Thumbs.db

# Arquivos de ambiente
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build
dist/
build/
*.min.js
*.min.css

# Cache
.cache/
.parcel-cache/

# Arquivos temporários
*.tmp
*.temp
nul

# Screenshots de teste
*.png
!github-*.png

# Relatórios
MEEP_*.json
MEEP_*.md
*_REPORT.json
*_SUMMARY.md
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore criado!" -ForegroundColor Green
}

# Adicionar arquivos ao staging
Write-Host "📦 Adicionando arquivos ao staging..." -ForegroundColor Yellow
git add .

# Fazer commit inicial
Write-Host "💾 Fazendo commit inicial..." -ForegroundColor Yellow
$commitMessage = "🚀 Deploy inicial do Sistema Cesar V7 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m "$commitMessage"

# Configurar branch tracking
Write-Host "🌿 Configurando branch tracking..." -ForegroundColor Yellow
git branch --set-upstream-to=origin/main main

Write-Host "✅ Configuração do Git concluída com sucesso!" -ForegroundColor Green
Write-Host "🔗 Repositório: https://github.com/contatoroyalclubms-sudo/sistema-cesar" -ForegroundColor Cyan
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Push para o repositório: git push -u origin main" -ForegroundColor White
Write-Host "   2. Configurar GitHub Actions para deploy automático" -ForegroundColor White
Write-Host "   3. Configurar Railway/Vercel para hosting" -ForegroundColor White
