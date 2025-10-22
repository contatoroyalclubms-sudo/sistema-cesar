from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Importar routers seguindo estrutura NIP organizacional
from app.routers import (
    # Core
    auth, dashboard,
    # Financeiro
    financeiro,
    # PDV e Vendas  
    pdv, gestao_venda,
    # Operações
    estoque, produtos,
    # Marketing e CRM
    marketing, clientes,
    # Business Intelligence
    bi, relatorios,
    # ERP e Automação
    erp, automacao,
    # Integração e APIs
    integracao, n8n, whatsapp,
    # Gestão
    usuarios, empresas, equipe,
    # Eventos e Entretenimento
    eventos, ingressos, listas, checkins,
    # Outros módulos
    cardapio, cupons, formas_pagamento, gamificacao,
    mapa_operacao, meep, pedidos, solucoes_online, transacoes
)

app = FastAPI(
    title="Sistema NIP - API Unificada Meep Compatible",
    description="API unificada do Sistema NIP compatível com o portal Meep - Todos os módulos implementados",
    version="4.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Endpoint de health check
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health Check - Verifica se a API está funcionando
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "message": "Sistema NIP - API operacional"
    }

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
