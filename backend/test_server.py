#!/usr/bin/env python3
"""
Teste de inicialização do servidor
"""

try:
    import uvicorn
    from app.main import app
    
    print("✅ Aplicação importada com sucesso")
    print("✅ Uvicorn disponível")
    print("✅ Servidor pronto para iniciar")
    
    # Tentar importar todos os routers
    from app.routers import auth, eventos, usuarios, empresas, listas, transacoes, checkins, dashboard, relatorios, whatsapp, cupons, n8n, pdv, financeiro, gamificacao
    print("✅ Todos os routers importados com sucesso")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
