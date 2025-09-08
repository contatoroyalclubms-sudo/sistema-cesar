"""
Servidor mínimo para testar sem middlewares
"""
import os
os.environ["DISABLE_REDIS"] = "true"

from fastapi import FastAPI
from app.routers import auth_no_redis
from app.database import engine
from app.models import Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

# App mínimo
app = FastAPI(title="Minimal Server")

# Apenas a rota de auth
app.include_router(auth_no_redis.router, prefix="/api/auth")

@app.get("/")
def root():
    return {"status": "minimal server running"}

if __name__ == "__main__":
    import uvicorn
    print("[MINIMAL] Starting minimal server without middlewares...")
    uvicorn.run(app, host="127.0.0.1", port=8002)