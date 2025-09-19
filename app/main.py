from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar todos os routers
from app.routers import auth
from app.routers import empresas
from app.routers import usuarios
from app.routers import eventos
from app.routers import listas
from app.routers import transacoes
from app.routers import checkins
from app.routers import dashboard
from app.routers import relatorios
from app.routers import whatsapp
from app.routers import cupons
from app.routers import n8n
from app.routers import produtos
from app.routers import pdv
from app.routers import gamificacao
from app.routers import formas_pagamento
from app.routers import meep
from app.routers import gestao_venda
from app.routers import solucoes_online
from app.routers import ingressos
from app.routers import equipe
from app.routers import pedidos
from app.routers import mapa_operacao
from app.routers import marketing
from app.routers import bi
from app.routers import automacao
from app.routers import integracao

app = FastAPI(
    title="MEEP Clone API",
    description="Clone completo com 250+ endpoints - Sistema Universal v6",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Registrar todos os routers
app.include_router(auth.router)
app.include_router(empresas.router)
app.include_router(usuarios.router)
app.include_router(eventos.router)
app.include_router(listas.router)
app.include_router(transacoes.router)
app.include_router(checkins.router)
app.include_router(dashboard.router)
app.include_router(relatorios.router)
app.include_router(whatsapp.router)
app.include_router(cupons.router)
app.include_router(n8n.router)
app.include_router(produtos.router)
app.include_router(pdv.router)
app.include_router(gamificacao.router)
app.include_router(formas_pagamento.router)
app.include_router(meep.router)
app.include_router(gestao_venda.router)
app.include_router(solucoes_online.router)
app.include_router(ingressos.router)
app.include_router(equipe.router)
app.include_router(pedidos.router)
app.include_router(mapa_operacao.router)
app.include_router(marketing.router)
app.include_router(bi.router)
app.include_router(automacao.router)
app.include_router(integracao.router)

@app.get("/")
async def root():
    return {"message": "MEEP Clone API - 141+ endpoints prontos!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
