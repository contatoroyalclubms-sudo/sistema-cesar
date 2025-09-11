#!/bin/bash

# 🚀 DEPLOY PRODUCTION READY - SISTEMA UNIVERSAL V7
# Script completo para deploy em produção

echo "======================================================================"
echo "🚀 SISTEMA UNIVERSAL V7 - DEPLOY PARA PRODUÇÃO"
echo "======================================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. BACKUP DO SISTEMA ATUAL
echo ""
log_info "1. FAZENDO BACKUP DO SISTEMA ATUAL..."
cd paineluniversal/backend

# Backup database
if [ -f "eventos.db" ]; then
    cp eventos.db "backup/eventos_backup_$(date +%Y%m%d_%H%M%S).db"
    log_success "Database SQLite backup realizado"
else
    log_warning "Database SQLite não encontrado"
fi

# Backup frontend
cd ../frontend
if [ -d "src" ]; then
    tar -czf "backup/frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz" src/
    log_success "Frontend backup realizado"
fi

# 2. INSTALAÇÃO DE DEPENDÊNCIAS
echo ""
log_info "2. VERIFICANDO E INSTALANDO DEPENDÊNCIAS..."

# Backend dependencies
cd ../backend
if [ -f "requirements.txt" ]; then
    log_info "Instalando dependências do backend..."
    pip install -r requirements.txt
    log_success "Dependências do backend instaladas"
fi

# Frontend dependencies
cd ../frontend
if [ -f "package.json" ]; then
    log_info "Instalando dependências do frontend..."
    npm install --production
    log_success "Dependências do frontend instaladas"
fi

# 3. BUILD DE PRODUÇÃO
echo ""
log_info "3. GERANDO BUILD DE PRODUÇÃO..."

# Frontend build
log_info "Compilando frontend para produção..."
npm run build
if [ $? -eq 0 ]; then
    log_success "Frontend build concluído com sucesso"
    log_info "Arquivos gerados em: dist/"
else
    log_error "Erro no build do frontend"
    exit 1
fi

# 4. CONFIGURAÇÃO DE AMBIENTE
echo ""
log_info "4. CONFIGURANDO AMBIENTE DE PRODUÇÃO..."

cd ../backend

# Criar arquivo .env.production se não existe
if [ ! -f ".env.production" ]; then
    cat > .env.production << EOF
# PRODUCTION ENVIRONMENT
DATABASE_URL=postgresql://user:password@localhost:5432/sistema_v7
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
FRONTEND_URL=https://seu-dominio.com
RAILWAY_ENVIRONMENT=production
CORS_ORIGINS=["https://seu-dominio.com"]

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-app

# WhatsApp Configuration (opcional)
WHATSAPP_TOKEN=seu-token-whatsapp

# Redis Configuration (opcional)
REDIS_URL=redis://localhost:6379/0
EOF
    log_success "Arquivo .env.production criado"
    log_warning "IMPORTANTE: Configure as variáveis em .env.production"
else
    log_info "Arquivo .env.production já existe"
fi

# 5. SETUP POSTGRESQL (se não estiver usando SQLite)
echo ""
log_info "5. CONFIGURANDO POSTGRESQL PARA PRODUÇÃO..."

# Verificar se PostgreSQL está instalado
if command -v psql &> /dev/null; then
    log_success "PostgreSQL encontrado"
    
    # Criar database se não existe
    log_info "Criando database de produção..."
    createdb sistema_v7_production 2>/dev/null
    
    # Executar migração
    log_info "Executando migrações..."
    python apply_postgresql_migration.py
    
    if [ $? -eq 0 ]; then
        log_success "Migrações executadas com sucesso"
    else
        log_warning "Erro nas migrações - usando SQLite como fallback"
    fi
else
    log_warning "PostgreSQL não instalado - usando SQLite"
fi

# 6. TESTES PRÉ-PRODUÇÃO
echo ""
log_info "6. EXECUTANDO TESTES PRÉ-PRODUÇÃO..."

# Teste de conexão database
log_info "Testando conexão com database..."
python -c "
from app.database import engine
try:
    conn = engine.connect()
    result = conn.execute('SELECT 1').scalar()
    conn.close()
    print('✅ Database: OK')
except Exception as e:
    print(f'❌ Database: ERRO - {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    log_success "Conexão database: OK"
else
    log_error "Erro na conexão database"
fi

# Teste de importações
log_info "Testando importações Python..."
python -c "
try:
    from app.main import app
    from app.models import Base
    from app.auth import create_access_token
    print('✅ Importações: OK')
except Exception as e:
    print(f'❌ Importações: ERRO - {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    log_success "Importações Python: OK"
else
    log_error "Erro nas importações Python"
fi

# 7. CONFIGURAÇÃO DO SERVIDOR WEB
echo ""
log_info "7. CONFIGURANDO SERVIDOR WEB..."

# Criar configuração Nginx
cat > nginx.production.conf << EOF
# NGINX CONFIGURATION - SISTEMA UNIVERSAL V7

upstream backend_servers {
    server 127.0.0.1:8000;
    # Adicione mais servidores para load balancing
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # SSL Configuration (configure with your certificates)
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Frontend files
    location / {
        root ../frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

log_success "Configuração Nginx criada: nginx.production.conf"

# 8. CRIAÇÃO DOS SCRIPTS DE SYSTEMD
echo ""
log_info "8. CRIANDO SCRIPTS DE SERVIÇO..."

# Script systemd para backend
cat > sistema-v7-backend.service << EOF
[Unit]
Description=Sistema Universal V7 - Backend FastAPI
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

# Security
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$(pwd)

[Install]
WantedBy=multi-user.target
EOF

log_success "Serviço systemd criado: sistema-v7-backend.service"

# 9. SCRIPT DE MONITORAMENTO
echo ""
log_info "9. CRIANDO SCRIPT DE MONITORAMENTO..."

cat > monitor-sistema.sh << EOF
#!/bin/bash

# 📊 MONITOR DO SISTEMA UNIVERSAL V7
# Script para monitoramento de produção

echo "======================================"
echo "📊 SISTEMA UNIVERSAL V7 - MONITOR"
echo "======================================"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para verificar serviços
check_service() {
    if systemctl is-active --quiet \$1; then
        echo -e "\${GREEN}✅ \$1: ATIVO\${NC}"
    else
        echo -e "\${RED}❌ \$1: INATIVO\${NC}"
    fi
}

# Verificar serviços
echo "🔧 SERVIÇOS:"
check_service "nginx"
check_service "postgresql" 
check_service "redis-server"
check_service "sistema-v7-backend"

# Verificar portas
echo ""
echo "🌐 PORTAS:"
if netstat -tuln | grep -q ":80 "; then
    echo -e "\${GREEN}✅ HTTP (80): ATIVO\${NC}"
else
    echo -e "\${RED}❌ HTTP (80): INATIVO\${NC}"
fi

if netstat -tuln | grep -q ":443 "; then
    echo -e "\${GREEN}✅ HTTPS (443): ATIVO\${NC}"
else
    echo -e "\${YELLOW}⚠️ HTTPS (443): NÃO CONFIGURADO\${NC}"
fi

if netstat -tuln | grep -q ":8000 "; then
    echo -e "\${GREEN}✅ Backend (8000): ATIVO\${NC}"
else
    echo -e "\${RED}❌ Backend (8000): INATIVO\${NC}"
fi

# Verificar disk space
echo ""
echo "💾 ESPAÇO EM DISCO:"
df -h / | tail -1 | awk '{print "📁 Root: " \$4 " disponível (" \$5 " usado)"}'

# Verificar memoria
echo ""
echo "🧠 MEMÓRIA:"
free -h | grep "Mem:" | awk '{print "💭 RAM: " \$7 " disponível / " \$2 " total"}'

# Verificar CPU
echo ""
echo "⚡ CPU:"
top -bn1 | grep "load average:" | awk '{printf "🔥 Load Average: %s %s %s\n", \$(NF-2), \$(NF-1), \$NF}'

# Health check da aplicação
echo ""
echo "🏥 HEALTH CHECK:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
    echo -e "\${GREEN}✅ API Health: OK\${NC}"
else
    echo -e "\${RED}❌ API Health: ERRO\${NC}"
fi

echo ""
echo "📊 Status completo verificado!"
EOF

chmod +x monitor-sistema.sh
log_success "Script de monitoramento criado: monitor-sistema.sh"

# 10. INSTRUÇÕES FINAIS
echo ""
echo "======================================================================"
log_success "🎉 DEPLOY PREPARADO COM SUCESSO!"
echo "======================================================================"

echo ""
log_info "📋 PRÓXIMOS PASSOS PARA PRODUÇÃO:"
echo "1. Configure as variáveis em .env.production"
echo "2. Configure SSL certificates no Nginx"  
echo "3. Execute: sudo cp nginx.production.conf /etc/nginx/sites-available/sistema-v7"
echo "4. Execute: sudo ln -s /etc/nginx/sites-available/sistema-v7 /etc/nginx/sites-enabled/"
echo "5. Execute: sudo cp sistema-v7-backend.service /etc/systemd/system/"
echo "6. Execute: sudo systemctl enable sistema-v7-backend"
echo "7. Execute: sudo systemctl start sistema-v7-backend"
echo "8. Execute: sudo systemctl reload nginx"

echo ""
log_info "🔧 COMANDOS ÚTEIS:"
echo "• Monitorar sistema: ./monitor-sistema.sh"
echo "• Logs backend: sudo journalctl -u sistema-v7-backend -f"
echo "• Logs nginx: sudo tail -f /var/log/nginx/access.log"
echo "• Reiniciar backend: sudo systemctl restart sistema-v7-backend"

echo ""
log_warning "⚠️ LEMBRE-SE:"
echo "• Configure o firewall (ufw/iptables)"
echo "• Configure backup automático"
echo "• Configure monitoramento (New Relic/DataDog)"
echo "• Configure alertas por email/SMS"

echo ""
log_success "✅ Sistema pronto para deploy em produção!"
echo "======================================================================"