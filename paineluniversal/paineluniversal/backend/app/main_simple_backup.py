from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Gestão de Eventos",
    description="API para gestão de eventos",
    version="1.0.0"
)

# CORS simples e robusto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar e registrar rotas após configuração básica
try:
    from .database import engine
    from .models import Base
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")
    
    # Importar routers
    from .routers import (
        auth, eventos, usuarios, empresas, listas, 
        transacoes, checkins, dashboard, relatorios
    )
    
    # Registrar routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
    app.include_router(empresas.router, prefix="/api/empresas", tags=["Empresas"])
    app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuários"])
    app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos"])
    app.include_router(listas.router, prefix="/api/listas", tags=["Listas"])
    app.include_router(transacoes.router, prefix="/api/transacoes", tags=["Transações"])
    app.include_router(checkins.router, prefix="/api/checkins", tags=["Check-ins"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
    
    logger.info("✅ All routers registered successfully")
    
except Exception as e:
    logger.error(f"❌ Error during startup: {e}")
    # Continuar mesmo com erro para permitir debug

# Health check endpoints
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "service": "Sistema de Gestão de Eventos",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/healthz")
async def healthz():
    return JSONResponse(
        content={
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/health")
async def api_health():
    return JSONResponse(
        content={
            "status": "healthy",
            "api": "Sistema Universal API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    )

# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    
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
            "Access-Control-Allow-Headers": "*"
        }
    )

# OPTIONS handler
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        }
    )

logger.info("🎉 FastAPI application configured successfully")
