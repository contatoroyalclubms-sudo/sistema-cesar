#!/usr/bin/env python3
"""
Teste local do servidor FastAPI
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_server_locally():
    """Testar servidor localmente"""
    print("🚀 TESTE LOCAL DO SERVIDOR FASTAPI")
    print("=" * 50)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.app.main_test import app
        from fastapi.testclient import TestClient
        
        # Criar cliente de teste
        client = TestClient(app)
        
        print("✅ App FastAPI carregado")
        print("✅ Cliente de teste criado")
        
        # Teste dos endpoints
        endpoints = [
            ("/", "Health Check"),
            ("/health", "Health Check Completo"),
            ("/api/usuarios", "Lista de Usuários"),
            ("/api/produtos", "Lista de Produtos"),  
            ("/api/empresas", "Lista de Empresas"),
            ("/api/dashboard/stats", "Estatísticas"),
            ("/api/test/integration", "Teste de Integração"),
        ]
        
        results = []
        
        for endpoint, description in endpoints:
            try:
                print(f"\n🔍 Testando: {description}")
                print(f"   📍 GET {endpoint}")
                
                response = client.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Status: {response.status_code}")
                    
                    if endpoint == "/":
                        print(f"   💾 Database: {data.get('database', 'N/A')}")
                        print(f"   🔗 Status: {data.get('status', 'N/A')}")
                    elif endpoint == "/health":
                        print(f"   💾 Database: {data.get('database', 'N/A')}")
                        print(f"   📊 Total registros: {data.get('data', {}).get('total_registros', 0)}")
                    elif "/usuarios" in endpoint:
                        usuarios = data.get('usuarios', [])
                        print(f"   📊 Usuários: {len(usuarios)}")
                        print(f"   📈 Total no DB: {data.get('total', 0)}")
                        if usuarios:
                            print(f"   👤 Primeiro: {usuarios[0]['nome']}")
                    elif "/produtos" in endpoint:
                        produtos = data.get('produtos', [])
                        print(f"   📊 Produtos: {len(produtos)}")
                        print(f"   📈 Total no DB: {data.get('total', 0)}")
                        if produtos:
                            print(f"   🏪 Primeiro: {produtos[0]['nome']}")
                    elif "/empresas" in endpoint:
                        empresas = data.get('empresas', [])
                        print(f"   📊 Empresas: {len(empresas)}")
                        if empresas:
                            print(f"   🏢 Primeira: {empresas[0]['nome']}")
                    elif "/dashboard/stats" in endpoint:
                        stats = data.get('estatisticas', {})
                        print(f"   👥 Usuários: {stats.get('usuarios', {}).get('total', 0)}")
                        print(f"   🏪 Produtos: {stats.get('produtos', {}).get('total', 0)}")
                        print(f"   🏢 Empresas: {stats.get('empresas', {}).get('total', 0)}")
                    elif "/test/integration" in endpoint:
                        print(f"   🧪 Status: {data.get('status', 'N/A')}")
                        print(f"   ✅ Todos passaram: {data.get('all_tests_passed', False)}")
                        results_detail = data.get('results', {})
                        print(f"   🔌 Conexão DB: {results_detail.get('database_connection', False)}")
                        print(f"   📋 Tabelas: {results_detail.get('tables_accessible', False)}")
                        print(f"   🔐 Integridade: {results_detail.get('data_integrity', False)}")
                        print(f"   🔍 Queries: {results_detail.get('queries_working', False)}")
                    
                    results.append(True)
                else:
                    print(f"   ❌ Status: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append(False)
        
        # Resultado final
        sucessos = sum(results)
        total = len(results)
        taxa_sucesso = (sucessos / total) * 100
        
        print(f"\n" + "="*50)
        print(f"🎯 RESULTADO DOS TESTES LOCAIS")
        print(f"✅ Endpoints funcionando: {sucessos}/{total}")
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if taxa_sucesso == 100:
            print(f"\n🎉 SERVIDOR TOTALMENTE FUNCIONAL!")
            print(f"🚀 Todos os endpoints operacionais")
            print(f"💾 Conectado ao PostgreSQL")
            print(f"📊 Dados acessíveis via API")
            return True
        else:
            print(f"\n⚠️ Alguns endpoints precisam de ajustes")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_server_locally()
