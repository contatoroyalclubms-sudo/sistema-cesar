#!/usr/bin/env python3
"""
Teste do endpoint correto baseado na imagem do browser
"""
import requests
import json

def test_correct_endpoint():
    """Testa o endpoint correto baseado na URL da imagem"""
    
    # Da imagem, vejo que a URL do frontend é:
    # frontend-painel-universal-production.up.railway.app
    # Então o backend provavelmente é algo similar
    
    possible_backends = [
        "https://backend-painel-universal-production.up.railway.app",
        "https://api-painel-universal-production.up.railway.app", 
        "https://paineluniversal-backend-production.up.railway.app",
        "https://painel-universal-backend-production.up.railway.app"
    ]
    
    for backend_url in possible_backends:
        endpoint = f"{backend_url}/api/produtos/"
        print(f"🔍 Testando: {endpoint}")
        
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCESSO! Backend encontrado!")
                data = response.json()
                print(f"   📋 Produtos encontrados: {len(data.get('produtos', []))}")
                return backend_url
            elif response.status_code == 404:
                print("   ❌ Endpoint não encontrado")
            else:
                print(f"   ⚠️ Erro {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print("   🔌 Não conseguiu conectar")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    return None

def test_root_endpoints():
    """Testa os endpoints raiz para ver se estão online"""
    
    possible_backends = [
        "https://backend-painel-universal-production.up.railway.app",
        "https://api-painel-universal-production.up.railway.app"
    ]
    
    for backend_url in possible_backends:
        print(f"🔍 Testando root: {backend_url}")
        
        try:
            response = requests.get(backend_url, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

if __name__ == "__main__":
    print("🧪 TESTE DE DESCOBERTA DO BACKEND CORRETO")
    print("=" * 60)
    
    # Testar endpoints
    backend_found = test_correct_endpoint()
    
    if not backend_found:
        print("\n🔍 Testando endpoints raiz...")
        test_root_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 Teste concluído!")
