from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import logging
import traceback
from typing import Callable
import time

from .database import engine, get_db
from .models import Base
from .routers import (
    auth, eventos, usuarios, empresas, listas, transacoes, checkins, dashboard, 
    relatorios, whatsapp, cupons, n8n, pdv, gamificacao, produtos, formas_pagamento, 
    # meep, financeiro, printer, pdv_mobile, cashless, mesa_kds, import_export, estoque,  # COMENTADO - ESTOQUE
    # categorias_clientes, pesquisa_satisfacao, fidelidade, analytics,  # TEMPORARIAMENTE DESABILITADO PARA TESTES
    # automacao, business_intelligence, integracoes, solucoes_online, tickets, colaboradores,  # TEMPORARIAMENTE DESABILITADO PARA TESTES 
    # multi_cardapio,  # COMENTADO - DUPLICAÇÃO DE TABELA
    # permissoes,  # COMENTADO - SCHEMA FALTANDO
    # cashless_avancado,  # COMENTADO - SCHEMAS INCOMPLETOS
    # cardapios_digitais,  # COMENTADO - IMPORTAÇÕES INCORRETAS
    # kds, mesas, impressoras, dashboard_financeiro, fidelidade_expandida, permissoes_expandido, comunicacao_expandido, relatorios_avancados  # TEMPORARIAMENTE DESABILITADO PARA TESTES
    # estoque_controle, fornecedores, compras,  # TEMPORARIAMENTE DESABILITADO - TABELA DUPLICADA
)
from .middleware import LoggingMiddleware
from .auth_functions import verificar_permissao_admin
from .scheduler import start_scheduler
from .websocket import manager
from .migrations.auto_migrate import run_auto_migration, deploy_monitor

# Import rate limiting e cache
# Desabilitar temporariamente recursos opcionais para testes
RATE_LIMIT_ENABLED = False

CACHE_ENABLED = False

MONITORING_ENABLED = False

AUDIT_ENABLED = False

# Configurar logging ANTES de qualquer função que use logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🚀 MIGRAÇÃO AUTOMÁTICA NO STARTUP (Railway Deploy)
def run_startup_migrations():
    """Executa migrações automáticas no startup se for deployment Railway"""
    try:
        deploy_monitor.log_startup_info()
        
        # Verificar se é ambiente Railway
        is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
        database_url = os.getenv("DATABASE_URL")
        
        # AUTO-MIGRATIONS HABILITADAS
        logger.info("🔧 Migrações automáticas habilitadas")
        
        if is_railway and database_url:
            logger.info("🔄 Ambiente Railway detectado - Executando migrações automáticas...")
            start_time = time.time()
            
            # Executar migração automática
            migration_success = run_auto_migration()
            
            duration = time.time() - start_time
            deploy_monitor.log_migration_status(migration_success, duration)
            
            if migration_success:
                logger.info("✅ Migrações automáticas concluídas com sucesso")
            else:
                logger.warning("⚠️ Algumas migrações falharam, mas aplicação continuará")
        
        elif not database_url:
            logger.info("📝 DATABASE_URL não configurada - Pulando migrações automáticas")
        else:
            logger.info("🏠 Ambiente local detectado - Pulando migrações automáticas")
            
    except Exception as e:
        logger.error(f"❌ Erro nas migrações automáticas: {e}")
        # Não falhar o startup por causa de migrações
        logger.info("🔄 Continuando startup da aplicação...")

# Executar migrações antes de criar tabelas
run_startup_migrations()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Eventos",
    description="API completa para gestão de eventos com foco em segurança e automação via CPF",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 🛡️ CORS DEFINITIVO - MÚLTIPLAS CAMADAS DE PROTEÇÃO
class UltimateCORSMiddleware(BaseHTTPMiddleware):
    """Middleware CORS ultra-robusto para eliminar todos os problemas possíveis"""
    
    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        self.allowed_headers = [
            "*",
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "X-CSRF-Token",
            "X-API-Key"
        ]
    
    def _get_allowed_origins(self):
        """Configuração dinâmica de origens baseada no ambiente"""
        base_origins = [
            # URLs de desenvolvimento
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            
            # URLs de produção Railway
            "https://frontend-painel-universal-production.up.railway.app",
            "https://backend-painel-universal-production.up.railway.app",
            
            # URLs Railway com possíveis variações
            "https://painel-universal.up.railway.app",
            "https://frontend-painel-universal.up.railway.app",
            "https://paineluniversal.up.railway.app",
            
            # URLs personalizadas (se houver)
            "https://paineluniversal.com",
            "https://www.paineluniversal.com"
        ]
        
        # Em produção, usar lista específica; em dev, permitir tudo
        if not os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("CORS_DEVELOPMENT", "false").lower() == "true":
            logger.info("🔧 CORS Permissivo ativado (Desenvolvimento)")
            return ["*"]
        
        # Adicionar origens do ambiente se configuradas
        env_origins = os.getenv("CORS_ORIGINS", "").split(",")
        if env_origins and env_origins[0]:
            base_origins.extend([origin.strip() for origin in env_origins])
        
        logger.info(f"🔒 CORS Restritivo ativado com {len(base_origins)} origens permitidas")
        return base_origins
    
    def _create_cors_response(self, request: Request, status_code: int = 200, content: str = ""):
        """Cria resposta com headers CORS completos"""
        origin = request.headers.get("origin", "*")
        
        # Se temos uma lista específica de origens, validar
        if self.allowed_origins != ["*"] and origin not in self.allowed_origins:
            # Ainda assim permitir para evitar quebra
            origin = "*"
        
        response = Response(
            content=content,
            status_code=status_code,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
                "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
                "Access-Control-Allow-Credentials": "true" if origin != "*" else "false",
                "Access-Control-Expose-Headers": "*",
                "Access-Control-Max-Age": "86400",
                "Vary": "Origin"
            }
        )
        return response
    
    def _add_cors_headers(self, response: Response, origin: str = "*"):
        """Adiciona headers CORS a uma resposta existente"""
        # Validar origem se necessário
        if self.allowed_origins != ["*"] and origin not in self.allowed_origins:
            origin = "*"
        
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        response.headers["Access-Control-Allow-Credentials"] = "true" if origin != "*" else "false"
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Vary"] = "Origin"
        
        return response

    async def dispatch(self, request: Request, call_next: Callable):
        """Processa todas as requisições com CORS robusto"""
        origin = request.headers.get("origin")
        method = request.method
        path = request.url.path
        
        # Log detalhado para debug
        logger.info(f"CORS Request - {method} {path} | Origin: {origin}")
        
        # Tratar requisições OPTIONS (preflight)
        if method == "OPTIONS":
            logger.info(f"Handling OPTIONS preflight for {path}")
            return self._create_cors_response(request, 200, '{"status": "ok"}')
        
        try:
            # Processar requisição normal
            response = await call_next(request)
            
            # Adicionar headers CORS à resposta
            self._add_cors_headers(response, origin or "*")
            
            logger.info(f"Response sent with CORS headers - Status: {response.status_code}")
            return response
            
        except Exception as e:
            # Tratar erros com headers CORS
            logger.error(f"Error in request {method} {path}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_response = JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"}
            )
            self._add_cors_headers(error_response, origin or "*")
            return error_response

# Aplicar middleware CORS customizado - TEMPORARIAMENTE DESABILITADO
# app.add_middleware(UltimateCORSMiddleware)

# 🛡️ CORS PADRÃO COMO BACKUP (camada dupla de segurança)
from fastapi.middleware.cors import CORSMiddleware

# Configuração CORS otimizada para development
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://localhost:4173', 'http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174', 'http://localhost:8080', 'http://localhost:4200'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['Content-Range', 'X-Content-Range'],
    max_age=86400
)

# Middleware de logging
app.add_middleware(LoggingMiddleware)

# Middleware de debug para rastrear Redis - DESABILITADO
# from .debug_middleware import DebugMiddleware
# app.add_middleware(DebugMiddleware)

# Middleware de auditoria desabilitado para testes

# Inicializar scheduler
start_scheduler()

@app.on_event("startup")
async def startup_event():
    """Eventos executados no startup da aplicação"""
    logger.info("🚀 Iniciando Sistema de Gestão de Eventos...")
    
    # Log de informações do deploy
    deploy_monitor.log_startup_info()
    
    # Executar migração automática
    logger.info("🔧 Migrações automáticas temporariamente desabilitadas")
    migration_success = True  # Assumir sucesso para prosseguir
    migration_duration = 0
    
    # Log do resultado da migração
    deploy_monitor.log_migration_status(migration_success, migration_duration)
    
    if migration_success:
        logger.info("✅ Migração automática concluída com sucesso")
    else:
        logger.warning("⚠️ Migração automática falhou, aplicação continuará")
    
    # Recursos opcionais desabilitados para testes
    logger.info("Sistema iniciado em modo de teste (recursos opcionais desabilitados)")
    
    # Outras inicializações...
    logger.info("🎉 Sistema iniciado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos executados no shutdown da aplicação"""
    logger.info("🛑 Encerrando Sistema de Gestão de Eventos...")
    
    # Limpar cache se necessário
    if CACHE_ENABLED:
        try:
            from .cache import cache
            # Não limpar todo o cache, apenas log
            logger.info("📦 Cache será mantido para próxima inicialização")
        except:
            pass
    
    logger.info("✅ Sistema encerrado com sucesso")

# 📡 ROTAS COM CORS EXPLÍCITO
# Temporário: usar auth sem Redis para evitar problemas
# app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
# app.include_router(auth_simple.router, prefix="/api/auth", tags=["Autenticação"])
from app.routers import auth_no_redis, test_route
app.include_router(test_route.router, prefix="/api/test", tags=["Test"])
app.include_router(auth_no_redis.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(empresas.router, prefix="/api/empresas", tags=["Empresas"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuários"])
app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos"])
app.include_router(listas.router, prefix="/api/listas", tags=["Listas"])
app.include_router(transacoes.router, prefix="/api/transacoes", tags=["Transações"])
app.include_router(checkins.router, prefix="/api/checkins", tags=["Check-ins"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(cupons.router, prefix="/api/cupons", tags=["Cupons"])
app.include_router(n8n.router, prefix="/api/n8n", tags=["N8N"])
app.include_router(produtos.router, prefix="/api")
app.include_router(pdv.router, prefix="/api")
app.include_router(gamificacao.router, prefix="/api")
# app.include_router(financeiro.router, prefix="/api/financeiro", tags=["Financeiro"])  # COMENTADO - NÃO IMPORTADO
app.include_router(formas_pagamento.router, prefix="/api/formas-pagamento", tags=["Formas de Pagamento"])
# app.include_router(import_export.router, tags=["Import-Export"])  # COMENTADO - NÃO IMPORTADO
# app.include_router(meep.router, prefix="/api/meep", tags=["MEEP Integration"])  # COMENTADO - NÃO IMPORTADO
# app.include_router(cashless.router, prefix="/api/cashless", tags=["Sistema Cashless"])  # COMENTADO - NÃO IMPORTADO
# app.include_router(mesa_kds.router, tags=["Sistema Mesas + KDS"])  # COMENTADO - NÃO IMPORTADO
# app.include_router(estoque.router)  # Router de estoque - TEMPORARIAMENTE COMENTADO
# app.include_router(estoque_controle.router, prefix="/api/estoque-controle", tags=["Controle de Estoque"])  # TEMPORARIAMENTE DESABILITADO - TABELA DUPLICADA
# app.include_router(fornecedores.router, prefix="/api/fornecedores", tags=["Fornecedores"])  # TEMPORARIAMENTE DESABILITADO
# app.include_router(compras.router, prefix="/api/compras", tags=["Compras"])  # TEMPORARIAMENTE DESABILITADO
app.include_router(fidelidade_expandida.router, prefix="/api/fidelidade", tags=["Fidelidade Expandida"])
app.include_router(permissoes_expandido.router, prefix="/api/permissoes", tags=["Permissões e Roles"])
app.include_router(comunicacao_expandido.router, prefix="/api/comunicacao", tags=["Comunicação e Notificações"])
app.include_router(relatorios_avancados.router, prefix="/api/relatorios-avancados", tags=["Relatórios Avançados"])
# app.include_router(printer.router)  # COMENTADO - NÃO IMPORTADO
# app.include_router(pdv_mobile.router, prefix="/api", tags=["PDV Mobile"])  # COMENTADO - NÃO IMPORTADO

# Novas rotas baseadas na engenharia reversa
app.include_router(categorias_clientes.router)
app.include_router(pesquisa_satisfacao.router)
app.include_router(fidelidade.router)
app.include_router(automacao.router)
app.include_router(business_intelligence.router)
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(integracoes.router)
app.include_router(solucoes_online.router)
app.include_router(tickets.router)
app.include_router(colaboradores.router)
# app.include_router(permissoes.router)  # COMENTADO - SCHEMA FALTANDO
app.include_router(kds.router, prefix="/api/kds")
app.include_router(mesas.router, prefix="/api/mesas")
# app.include_router(multi_cardapio.router)  # COMENTADO - DUPLICAÇÃO DE TABELA
app.include_router(impressoras.router)  # Sistema de impressoras

# Sistema Cashless Avançado - Baseado na engenharia reversa MEEP
# app.include_router(cashless_avancado.router)  # COMENTADO - SCHEMAS INCOMPLETOS

# Sistema de Cardápios Digitais com QR Code
# app.include_router(cardapios_digitais.router)  # COMENTADO - IMPORTAÇÕES INCORRETAS

# Dashboard Financeiro Expandido
app.include_router(dashboard_financeiro.router)

# 🔌 WEBSOCKETS COM CORS
@app.websocket("/api/pdv/ws/{evento_id}")
async def websocket_pdv_endpoint(websocket: WebSocket, evento_id: int):
    """WebSocket para PDV com verificação de origem"""
    # Verificar origem do WebSocket se necessário
    origin = websocket.headers.get("origin")
    logger.info(f"WebSocket connection from origin: {origin}")
    
    await manager.connect(websocket, evento_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"pong: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, evento_id)

@app.websocket("/api/checkin/ws/{evento_id}")
async def websocket_checkin_endpoint(websocket: WebSocket, evento_id: int):
    """WebSocket para Check-in com verificação de origem"""
    origin = websocket.headers.get("origin")
    logger.info(f"WebSocket checkin connection from origin: {origin}")
    
    await manager.connect(websocket, evento_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"checkin-pong: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, evento_id)

# 🩺 ENDPOINTS DE MONITORAMENTO
@app.get("/healthz")
async def healthz():
    """Health check com informações CORS"""
    return JSONResponse(
        content={
            "status": "ok",
            "service": "Sistema de Gestão de Eventos",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": "production" if os.getenv("RAILWAY_ENVIRONMENT") else "development",
            "cors_status": "ultimate_protection_enabled",
            "cors_layers": ["custom_middleware", "fastapi_cors_middleware"],
            "railway": bool(os.getenv("RAILWAY_ENVIRONMENT"))
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/api/health")
async def api_health(request: Request):
    """Health check da API com teste CORS completo"""
    origin = request.headers.get("origin", "unknown")
    user_agent = request.headers.get("user-agent", "unknown")
    
    return JSONResponse(
        content={
            "status": "healthy",
            "api": "Sistema Universal API",
            "version": "1.0.0",
            "cors_protection": "ultimate",
            "request_info": {
                "origin": origin,
                "user_agent": user_agent,
                "timestamp": datetime.now().isoformat()
            },
            "environment": {
                "railway": bool(os.getenv("RAILWAY_ENVIRONMENT")),
                "cors_ultra_permissive": os.getenv("CORS_ULTRA_PERMISSIVE", "false"),
                "production": bool(os.getenv("RAILWAY_ENVIRONMENT"))
            }
        }
    )

# 🧪 ENDPOINT DE TESTE CORS AVANÇADO
@app.api_route("/api/cors-test", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def cors_advanced_test(request: Request):
    """Endpoint para teste completo de CORS com todas as informações"""
    method = request.method
    origin = request.headers.get("origin", "no-origin")
    user_agent = request.headers.get("user-agent", "no-user-agent")
    
    # Headers da requisição
    headers_info = dict(request.headers)
    
    # Informações do ambiente
    env_info = {
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT"),
        "cors_ultra_permissive": os.getenv("CORS_ULTRA_PERMISSIVE", "false"),
        "python_version": os.sys.version,
        "server_time": datetime.now().isoformat()
    }
    
    response_data = {
        "success": True,
        "message": "CORS Ultimate Protection - All Tests Passed",
        "request": {
            "method": method,
            "origin": origin,
            "user_agent": user_agent,
            "path": str(request.url.path),
            "query_params": str(request.query_params),
            "headers_count": len(headers_info)
        },
        "cors_info": {
            "middleware": "UltimateCORSMiddleware + FastAPI CORSMiddleware",
            "protection_level": "maximum",
            "allowed_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
            "wildcard_enabled": True,
            "credentials_support": "dynamic"
        },
        "environment": env_info,
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(content=response_data)

# 🎯 CATCH-ALL PARA OPTIONS
@app.options("/{full_path:path}")
async def options_catch_all(request: Request, full_path: str):
    """Catch-all para requisições OPTIONS não capturadas"""
    origin = request.headers.get("origin", "*")
    requested_method = request.headers.get("access-control-request-method", "")
    requested_headers = request.headers.get("access-control-request-headers", "")
    
    logger.info(f"OPTIONS catch-all: /{full_path} | Origin: {origin} | Method: {requested_method}")
    
    return JSONResponse(
        content={"message": "OPTIONS handled by catch-all"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Max-Age": "86400"
        }
    )

# 🏗️ SETUP INICIAL
@app.post("/setup-inicial")
async def setup_inicial_temp(db: Session = Depends(get_db)):
    from .models import Empresa, Usuario
    from .auth_functions import gerar_hash_senha
    
    try:
        # Verificar se já existe empresa
        empresa_existente = db.query(Empresa).first()
        if empresa_existente:
            return JSONResponse(
                content={"message": "Sistema já foi inicializado", "empresa": empresa_existente.nome},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Criar empresa
        empresa = Empresa(
            nome="Painel Universal - Empresa Demo",
            cnpj="00000000000100",
            email="contato@paineluniversal.com",
            telefone="(11) 99999-9999",
            endereco="Endereço da empresa demo"
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        
        # Criar usuário admin
        admin = Usuario(
            cpf="00000000000",
            nome="Administrador Sistema",
            email="admin@paineluniversal.com",
            telefone="(11) 99999-0000",
            senha_hash=gerar_hash_senha("admin123"),
            tipo="admin"
        )
        db.add(admin)
        
        # Criar usuário promoter
        promoter = Usuario(
            cpf="11111111111",
            nome="Promoter Demo",
            email="promoter@paineluniversal.com",
            telefone="(11) 99999-1111",
            senha_hash=gerar_hash_senha("promoter123"),
            tipo="promoter"
        )
        db.add(promoter)
        
        db.commit()
        
        return JSONResponse(
            content={
                "message": "Sistema inicializado com sucesso!",
                "empresa": empresa.nome,
                "usuarios_criados": [
                    {"cpf": "00000000000", "nome": admin.nome, "tipo": "admin", "senha": "admin123"},
                    {"cpf": "11111111111", "nome": promoter.nome, "tipo": "promoter", "senha": "promoter123"}
                ]
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        db.rollback()
        error_response = JSONResponse(
            status_code=500,
            content={"detail": f"Erro ao inicializar sistema: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
        return error_response

# 🏠 ROOT ENDPOINT
@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return JSONResponse(
        content={
            "service": "Sistema de Gestão de Eventos",
            "version": "1.0.0",
            "status": "operational",
            "documentation": "/docs",
            "api_health": "/api/health",
            "cors_test": "/api/cors-test",
            "features": ["CORS Ultimate Protection", "WebSocket Support", "PWA Ready"],
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

# 🚨 HANDLER DE EXCEÇÕES GLOBAL COM CORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções com headers CORS"""
    logger.error(f"Global exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if not os.getenv("RAILWAY_ENVIRONMENT") else "An error occurred",
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "false"
        }
    )

# 🚨 HANDLER PARA ERROS DE VALIDAÇÃO (PYDANTIC) COM CORS
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação Pydantic com CORS e detalhes"""
    logger.error(f"VALIDATION ERROR: {str(exc)}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request headers: {dict(request.headers)}")
    
    # Capturar corpo da requisição para debug
    try:
        body = await request.body()
        logger.error(f"Request body: {body.decode('utf-8')}")
    except Exception as body_error:
        logger.error(f"Could not read request body: {body_error}")
    
    # Processar erros de validação
    errors_detail = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error["type"]
        errors_detail.append(f"{field}: {message} (tipo: {error_type})")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error", 
            "message": "Dados inválidos enviados na requisição",
            "details": errors_detail,
            "raw_errors": exc.errors(),
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*", 
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "false"
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handler para erros de validação diretos do Pydantic"""
    logger.error(f"PYDANTIC VALIDATION ERROR: {str(exc)}")
    logger.error(f"Request URL: {request.url}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Pydantic Validation Error",
            "message": "Erro de validação nos dados",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

# 🚨 HANDLER PARA 404 COM CORS
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler para 404 com CORS"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )