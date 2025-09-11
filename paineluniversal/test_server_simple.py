#!/usr/bin/env python3
"""
Servidor FastAPI simplificado para teste PostgreSQL
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

# Imports locais
from backend.app.database import get_db
from backend.app import models

# Criar app
app = FastAPI(
    title="Painel Universal API",
    description="API do Sistema Universal - PostgreSQL",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Painel Universal API - PostgreSQL",
        "status": "online",
        "database": "PostgreSQL"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check com teste de banco"""
    try:
        # Testar conexão com banco
        empresas_count = db.query(models.Empresa).count()
        usuarios_count = db.query(models.Usuario).count()
        produtos_count = db.query(models.Produto).count()
        
        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "data": {
                "empresas": empresas_count,
                "usuarios": usuarios_count,
                "produtos": produtos_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/usuarios")
async def list_usuarios(db: Session = Depends(get_db)):
    """Listar usuários"""
    try:
        usuarios = db.query(models.Usuario).limit(10).all()
        return [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "tipo": u.tipo,
                "ativo": u.ativo
            }
            for u in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produtos")
async def list_produtos(db: Session = Depends(get_db)):
    """Listar produtos"""
    try:
        produtos = db.query(models.Produto).limit(10).all()
        return [
            {
                "id": p.id,
                "nome": p.nome,
                "preco": float(p.preco),
                "tipo_usuario": p.tipo_usuario,
                "status": p.status
            }
            for p in produtos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
