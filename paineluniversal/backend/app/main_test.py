#!/usr/bin/env python3
"""
Servidor principal do Painel Universal - Versão para testes
Carrega apenas routers essenciais para evitar problemas com pandas
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging

# Imports locais
from .database import engine, get_db, Base
from .models import Usuario, Empresa, Produto
from . import models

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

# Criar app
app = FastAPI(
    title="Painel Universal API - Teste",
    description="API do Sistema Universal - PostgreSQL (Versão de Teste)",
    version="1.0.0-test"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROTAS BÁSICAS ====================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Painel Universal API - PostgreSQL Test",
        "status": "online",
        "database": "PostgreSQL",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check completo"""
    try:
        # Testar conexão e contar dados
        empresas_count = db.query(models.Empresa).count()
        usuarios_count = db.query(models.Usuario).count()
        produtos_count = db.query(models.Produto).count()
        
        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "empresas": empresas_count,
                "usuarios": usuarios_count,
                "produtos": produtos_count,
                "total_registros": empresas_count + usuarios_count + produtos_count
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ==================== ROTAS DE USUÁRIOS ====================

@app.get("/api/usuarios")
async def listar_usuarios(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar usuários com paginação"""
    try:
        usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
        total = db.query(models.Usuario).count()
        
        return {
            "usuarios": [
                {
                    "id": u.id,
                    "nome": u.nome,
                    "email": u.email,
                    "cpf": u.cpf,
                    "tipo": u.tipo,
                    "ativo": u.ativo,
                    "criado_em": u.criado_em.isoformat() if u.criado_em else None
                }
                for u in usuarios
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usuarios/{usuario_id}")
async def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obter usuário específico"""
    try:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "cpf": usuario.cpf,
            "tipo": usuario.tipo,
            "ativo": usuario.ativo,
            "telefone": usuario.telefone,
            "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
            "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter usuário {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTAS DE PRODUTOS ====================

@app.get("/api/produtos")
async def listar_produtos(
    skip: int = 0, 
    limit: int = 100,
    categoria: str = None,
    tipo_usuario: str = None,
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros"""
    try:
        query = db.query(models.Produto)
        
        # Aplicar filtros
        if categoria:
            query = query.filter(models.Produto.categoria == categoria)
        if tipo_usuario:
            query = query.filter(models.Produto.tipo_usuario == tipo_usuario)
        
        produtos = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return {
            "produtos": [
                {
                    "id": p.id,
                    "nome": p.nome,
                    "descricao": p.descricao,
                    "preco": float(p.preco) if p.preco else 0,
                    "tipo_usuario": p.tipo_usuario,
                    "categoria": p.categoria,
                    "status": p.status,
                    "estoque_atual": p.estoque_atual,
                    "controla_estoque": p.controla_estoque,
                    "codigo_interno": p.codigo_interno
                }
                for p in produtos
            ],
            "total": total,
            "filtros": {
                "categoria": categoria,
                "tipo_usuario": tipo_usuario
            }
        }
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTAS DE EMPRESAS ====================

@app.get("/api/empresas")
async def listar_empresas(db: Session = Depends(get_db)):
    """Listar empresas"""
    try:
        empresas = db.query(models.Empresa).all()
        
        return {
            "empresas": [
                {
                    "id": e.id,
                    "nome": e.nome,
                    "cnpj": e.cnpj,
                    "email": e.email,
                    "telefone": e.telefone,
                    "ativa": e.ativa,
                    "criado_em": e.criado_em.isoformat() if e.criado_em else None
                }
                for e in empresas
            ],
            "total": len(empresas)
        }
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTAS DE ESTATÍSTICAS ====================

@app.get("/api/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """Estatísticas do dashboard"""
    try:
        # Contar registros por tipo
        stats = {
            "usuarios": {
                "total": db.query(models.Usuario).count(),
                "ativos": db.query(models.Usuario).filter(models.Usuario.ativo == True).count(),
                "admins": db.query(models.Usuario).filter(models.Usuario.tipo == 'admin').count(),
                "promoters": db.query(models.Usuario).filter(models.Usuario.tipo == 'promoter').count(),
                "clientes": db.query(models.Usuario).filter(models.Usuario.tipo == 'cliente').count(),
            },
            "empresas": {
                "total": db.query(models.Empresa).count(),
                "ativas": db.query(models.Empresa).filter(models.Empresa.ativa == True).count(),
            },
            "produtos": {
                "total": db.query(models.Produto).count(),
                "ativos": db.query(models.Produto).filter(models.Produto.status == 'ATIVO').count(),
            }
        }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "estatisticas": stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTA DE TESTE INTEGRADO ====================

@app.get("/api/test/integration")
async def test_integration(db: Session = Depends(get_db)):
    """Teste de integração completo"""
    try:
        results = {
            "database_connection": False,
            "tables_accessible": False,
            "data_integrity": False,
            "queries_working": False,
            "errors": []
        }
        
        # Teste 1: Conexão com banco
        try:
            db.execute("SELECT 1")
            results["database_connection"] = True
        except Exception as e:
            results["errors"].append(f"Database connection: {str(e)}")
        
        # Teste 2: Acesso às tabelas
        try:
            db.query(models.Usuario).count()
            db.query(models.Empresa).count()
            db.query(models.Produto).count()
            results["tables_accessible"] = True
        except Exception as e:
            results["errors"].append(f"Table access: {str(e)}")
        
        # Teste 3: Integridade dos dados
        try:
            # Verificar se há dados básicos
            empresas = db.query(models.Empresa).count()
            usuarios = db.query(models.Usuario).count()
            if empresas > 0 and usuarios > 0:
                results["data_integrity"] = True
            else:
                results["errors"].append("No basic data found")
        except Exception as e:
            results["errors"].append(f"Data integrity: {str(e)}")
        
        # Teste 4: Queries complexas
        try:
            # Query com join implícito
            from sqlalchemy import text
            result = db.execute(text("""
                SELECT u.tipo, COUNT(*) as total 
                FROM usuarios u 
                GROUP BY u.tipo
            """))
            query_results = result.fetchall()
            if query_results:
                results["queries_working"] = True
        except Exception as e:
            results["errors"].append(f"Complex queries: {str(e)}")
        
        # Status geral
        all_tests_passed = all([
            results["database_connection"],
            results["tables_accessible"],
            results["data_integrity"],
            results["queries_working"]
        ])
        
        return {
            "status": "success" if all_tests_passed else "partial",
            "all_tests_passed": all_tests_passed,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de integração: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
