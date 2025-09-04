#!/bin/bash

echo "🚀 Iniciando build completo do Sistema MEEP..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar se Docker está rodando
if ! docker --version >/dev/null 2>&1; then
    error "Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi

if ! docker-compose --version >/dev/null 2>&1; then
    error "Docker Compose não encontrado! Instale o Docker Compose primeiro."
    exit 1
fi

log "Docker e Docker Compose encontrados ✅"

# Parar containers existentes
log "Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Remover volumes órfãos se necessário
if [ "$1" == "--clean" ]; then
    warn "Modo clean ativado - removendo volumes..."
    docker-compose down -v --remove-orphans
    docker system prune -f
fi

# Verificar arquivos .env
if [ ! -f ".env" ]; then
    warn "Arquivo .env não encontrado, copiando do exemplo..."
    cp .env.example .env
    warn "⚠️  Configure o arquivo .env antes de continuar!"
fi

# Build dos serviços
log "Construindo imagens Docker..."
if docker-compose build --no-cache; then
    log "Build concluído com sucesso ✅"
else
    error "Falha no build dos containers"
    exit 1
fi

# Aplicar migrações do banco
log "Aplicando migrações do banco de dados..."
docker-compose up -d postgres redis
sleep 10

# Aguardar banco estar pronto
log "Aguardando banco de dados ficar pronto..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U painel_user -d paineluniversal >/dev/null 2>&1; then
        log "Banco de dados pronto ✅"
        break
    fi
    echo -n "."
    sleep 2
done

# Executar migrações
log "Executando migrações MEEP..."
docker-compose run --rm fastapi-backend python create_meep_migration.py

# Iniciar todos os serviços
log "Iniciando todos os serviços..."
if docker-compose up -d; then
    log "Todos os serviços iniciados ✅"
else
    error "Falha ao iniciar serviços"
    exit 1
fi

# Aguardar serviços ficarem prontos
log "Aguardando serviços ficarem prontos..."
sleep 15

# Health checks
log "Verificando saúde dos serviços..."

# Backend FastAPI
if curl -f http://localhost:8000/healthz >/dev/null 2>&1; then
    log "Backend FastAPI: ✅ Saudável"
else
    warn "Backend FastAPI: ⚠️  Não responsivo"
fi

# MEEP Service
if curl -f http://localhost:3001/health >/dev/null 2>&1; then
    log "MEEP Service: ✅ Saudável"
else
    warn "MEEP Service: ⚠️  Não responsivo"
fi

# Frontend
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    log "Frontend: ✅ Saudável"
else
    warn "Frontend: ⚠️  Não responsivo"
fi

# Nginx
if curl -f http://localhost:80/health >/dev/null 2>&1; then
    log "Nginx: ✅ Saudável"
else
    warn "Nginx: ⚠️  Não responsivo"
fi

# Status final
log "Verificando status dos containers..."
docker-compose ps

echo ""
log "🎉 Sistema MEEP deployado com sucesso!"
echo ""
info "📋 URLs de acesso:"
info "   Frontend: http://localhost:3000"
info "   Backend API: http://localhost:8000"
info "   MEEP Service: http://localhost:3001"
info "   Docs API: http://localhost:8000/docs"
info "   Nginx Proxy: http://localhost:80"
echo ""
info "📊 Monitoramento:"
info "   Health Check: curl http://localhost:8000/healthz"
info "   MEEP Health: curl http://localhost:3001/health"
info "   Logs: docker-compose logs -f [service_name]"
echo ""
info "🛠️  Comandos úteis:"
info "   Ver logs: docker-compose logs -f"
info "   Parar: docker-compose down"
info "   Rebuild: docker-compose build --no-cache"
info "   Shell backend: docker-compose exec fastapi-backend bash"
info "   Shell MEEP: docker-compose exec meep-service sh"
echo ""

# Mostrar usuários padrão
if [ -f ".env" ]; then
    info "👤 Usuários padrão (configurar no .env se necessário):"
    info "   Admin: admin@paineluniversal.com / admin123"
    info "   Promoter: promoter@paineluniversal.com / promoter123"
fi

echo ""
log "Sistema pronto para uso! 🚀"
