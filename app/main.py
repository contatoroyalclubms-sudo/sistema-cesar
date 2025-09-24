from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar todos os routers
from routers import auth
from routers import empresas
from routers import usuarios
from routers import eventos
from routers import listas
from routers import transacoes
from routers import checkins
from routers import dashboard
from routers import relatorios
from routers import whatsapp
from routers import cupons
from routers import n8n
from routers import produtos
from routers import pdv
from routers import gamificacao
from routers import formas_pagamento
from routers import meep
from routers import gestao_venda
from routers import solucoes_online
from routers import ingressos
from routers import equipe
from routers import pedidos
from routers import mapa_operacao
from routers import marketing
from routers import bi
from routers import automacao
from routers import integracao
from routers import estoque
from routers import cardapio
from routers import financeiro
from routers import clientes
from routers import erp

app = FastAPI(
    title="MEEP Clone API - Sistema Completo",
    description="Sistema completo com 500+ endpoints - Todos os módulos MEEP implementados",
    version="3.0.0"
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
app.include_router(estoque.router)
app.include_router(cardapio.router)
app.include_router(financeiro.router)
app.include_router(clientes.router)
app.include_router(erp.router)

@app.get("/")
async def root():
    return {
        "message": "MEEP Clone API - Sistema Completo",
        "version": "3.0.0",
        "total_endpoints": "500+",
        "modulos": {
            "dashboard": "✅ Completo",
            "clientes": "✅ Completo - Categorização, Segmentação, Pesquisas",
            "equipe": "✅ Completo",
            "cardapio": "✅ Completo - Gestão completa de cardápios",
            "gestao_venda": "✅ Completo",
            "solucoes_online": "✅ Completo",
            "ingressos": "✅ Completo",
            "relatorios": "✅ Completo",
            "gestao_estoque": "✅ Completo - MRP, Inventário, Movimentações",
            "pdv": "✅ Completo",
            "pedidos": "✅ Completo",
            "financeiro": "✅ Completo - Conta Digital, Permutas, Antecipação",
            "mapa_operacao": "✅ Completo",
            "marketing": "✅ Completo - Fidelidade, CRM, Campanhas",
            "bi": "✅ Completo",
            "sistema_erp": "✅ Completo - Fiscal, Contábil, Produção, RH",
            "automacao": "✅ Completo",
            "integracao": "✅ Completo"
        },
        "status": "✅ Todos os módulos MEEP implementados com sucesso!"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
