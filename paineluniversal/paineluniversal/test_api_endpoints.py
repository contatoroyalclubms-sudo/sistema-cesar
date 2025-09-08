#!/usr/bin/env python3
"""
Teste final dos endpoints da API
"""
import requests
import json

def test_api_endpoints():
    """Testar endpoints da API"""
    base_url = "http://localhost:8001"
    print("🌐 TESTE DOS ENDPOINTS DA API")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/", "Health Check"),
        ("GET", "/users", "Lista de Usuários"),
        ("GET", "/products", "Lista de Produtos"),
        ("GET", "/companies", "Lista de Empresas"),
        ("GET", "/dashboard/stats", "Estatísticas do Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            print(f"\n🔍 Testando: {description}")
            print(f"   📍 {method} {endpoint}")
            
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                if endpoint == "/":
                    print(f"   💾 Database: {data.get('database', 'N/A')}")
                    print(f"   🔗 Status: {data.get('status', 'N/A')}")
                elif endpoint in ["/users", "/products", "/companies"]:
                    print(f"   📊 Registros: {len(data)}")
                    if data:
                        first_item = data[0]
                        if 'nome' in first_item:
                            print(f"   📝 Primeiro: {first_item['nome']}")
                        elif 'name' in first_item:
                            print(f"   📝 Primeiro: {first_item['name']}")
                elif endpoint == "/dashboard/stats":
                    print(f"   👥 Usuários: {data.get('users', 0)}")
                    print(f"   🏪 Produtos: {data.get('products', 0)}")
                    print(f"   🏢 Empresas: {data.get('companies', 0)}")
                
                results.append(True)
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro: Não foi possível conectar ao servidor")
            results.append(False)
        except requests.exceptions.Timeout:
            print(f"   ❌ Erro: Timeout na requisição")
            results.append(False)
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results.append(False)
    
    # Resultado final
    sucessos = sum(results)
    total = len(results)
    taxa_sucesso = (sucessos / total) * 100
    
    print(f"\n" + "="*50)
    print(f"🎯 RESULTADO DOS TESTES DE API")
    print(f"✅ Endpoints funcionando: {sucessos}/{total}")
    print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    if taxa_sucesso == 100:
        print(f"\n🎉 API TOTALMENTE FUNCIONAL!")
        print(f"🚀 Todos os endpoints operacionais")
        print(f"🌐 Servidor rodando em http://localhost:8000")
        print(f"📚 Documentação em http://localhost:8000/docs")
        return True
    else:
        print(f"\n⚠️ Alguns endpoints precisam de ajustes")
        return False

if __name__ == "__main__":
    test_api_endpoints()
