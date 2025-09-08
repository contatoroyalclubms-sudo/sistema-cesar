#!/usr/bin/env python3
"""
Teste direto do endpoint de produtos para identificar o erro 500
"""
import requests
import json
import sys

def test_produtos_endpoint():
    """Testa o endpoint de produtos"""
    
    base_url = "https://backend-painel-univ-app-production.up.railway.app"
    endpoint = f"{base_url}/api/produtos/"
    
    print("🔍 Testando endpoint de produtos...")
    print(f"URL: {endpoint}")
    
    try:
        # Fazer requisição GET
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            data = response.json()
            print(f"📋 Dados retornados: {json.dumps(data, indent=2, default=str)}")
            
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            
            try:
                error_data = response.json()
                print(f"📋 Error JSON: {json.dumps(error_data, indent=2, default=str)}")
            except:
                print("❌ Resposta não é JSON válido")
                
    except requests.exceptions.Timeout:
        print("⏱️ Timeout na requisição")
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def test_produtos_local():
    """Testa o endpoint local se estiver rodando"""
    
    local_url = "http://localhost:8000"
    endpoint = f"{local_url}/api/produtos/"
    
    print("\n🔍 Testando endpoint local...")
    print(f"URL: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso no local!")
            data = response.json()
            print(f"📋 Dados: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Erro local {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Servidor local não está rodando")
    except Exception as e:
        print(f"❌ Erro local: {str(e)}")

if __name__ == "__main__":
    print("🧪 TESTE DO ENDPOINT DE PRODUTOS")
    print("=" * 50)
    
    # Testar produção
    test_produtos_endpoint()
    
    # Testar local
    test_produtos_local()
    
    print("\n" + "=" * 50)
    print("🎯 Teste concluído!")
