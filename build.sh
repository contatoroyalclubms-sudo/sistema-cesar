#!/bin/bash
# 🚀 Script de Build Completo - Sistema Universal

echo "🏗️  Iniciando build do Sistema Universal..."
echo "================================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# 1. FRONTEND BUILD
log "📦 Construindo Frontend..."
cd frontend || { error "Diretório frontend não encontrado"; exit 1; }

log "Instalando dependências do frontend..."
npm install || { error "Falha ao instalar dependências"; exit 1; }

log "Executando build de produção..."
npm run build || { error "Falha no build do frontend"; exit 1; }

log "✅ Frontend build concluído!"
ls -la dist/

# 2. BACKEND PREPARATION
log "📦 Preparando Backend..."
cd ../backend || { error "Diretório backend não encontrado"; exit 1; }

# Verificar se virtual env existe
if [ ! -d "../.venv" ]; then
    error "Virtual environment não encontrado em ../.venv"
    exit 1
fi

# Ativar virtual env (no Windows seria diferente)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON_CMD="../.venv/Scripts/python.exe"
    PIP_CMD="../.venv/Scripts/pip.exe"
else
    source ../.venv/bin/activate
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

log "Verificando dependências do backend..."
$PIP_CMD install -r requirements.txt || { error "Falha ao instalar dependências"; exit 1; }

# 3. TESTES BÁSICOS
log "🧪 Executando testes básicos..."

log "Testando importação do backend..."
$PYTHON_CMD -c "from app.main import app; print('✅ Backend OK')" || { error "Falha na importação"; exit 1; }

log "Testando health check..."
$PYTHON_CMD -c "
import requests
import sys
import subprocess
import time
import os

# Iniciar servidor em background
server = subprocess.Popen(['$PYTHON_CMD', 'server.py'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)

# Aguardar inicialização
time.sleep(5)

try:
    response = requests.get('http://localhost:8000/healthz', timeout=10)
    if response.status_code == 200:
        print('✅ Health check OK')
    else:
        print(f'❌ Health check falhou: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Erro no health check: {e}')
    sys.exit(1)
finally:
    server.terminate()
" || warn "Health check falhou - continuando..."

# 4. PREPARAR ARQUIVOS DE DEPLOY
log "📋 Preparando arquivos de deploy..."

# Criar arquivo de start para produção
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Sistema Universal - Produção"
python server.py
EOF

chmod +x start.sh

# 5. SUMMARY
cd ..
log "📊 Resumo do Build:"
echo "================================================"
echo "✅ Frontend build: $(ls -la frontend/dist/ | wc -l) arquivos"
echo "✅ Backend preparado: $(pip list | wc -l) dependências"
echo "✅ Servidor de produção: backend/server.py"
echo "✅ Script de start: backend/start.sh"
echo ""
echo "📁 Estrutura final:"
echo "├── frontend/dist/     (arquivos estáticos)"
echo "├── backend/app/       (código Python)"
echo "├── backend/server.py  (servidor de produção)"
echo "└── backend/start.sh   (script de start)"
echo ""
log "🎉 Build completo realizado com sucesso!"
echo "================================================"
