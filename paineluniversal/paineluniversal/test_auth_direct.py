#!/usr/bin/env python3
"""
Script para testar autenticação diretamente
"""

import requests
import json

def test_auth_direct():
    """Testa autenticação diretamente no backend"""
    
    url = "http://127.0.0.1:8000/api/auth/login"
    
    # Dados de login
    data = {
        "cpf": "06601206154",
        "senha": "101112"
    }
    
    print(f"🔐 Testando login direto no backend...")
    print(f"📍 URL: {url}")
    print(f"📋 Dados: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login bem-sucedido!")
            print(f"📋 Resposta: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Login falhou!")
            try:
                error = response.json()
                print(f"📋 Erro: {json.dumps(error, indent=2)}")
            except:
                print(f"📋 Erro texto: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_cors():
    """Testa endpoint CORS"""
    
    url = "http://127.0.0.1:8000/api/cors-test"
    
    print(f"\n🌐 Testando CORS...")
    print(f"📍 URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CORS OK: {result}")
        else:
            print(f"❌ CORS falhou: {response.text}")
    except Exception as e:
        print(f"❌ Erro CORS: {e}")

if __name__ == "__main__":
    test_cors()
    test_auth_direct()
