#!/usr/bin/env python3
"""
Teste específico para login - debug detalhado
"""

import requests
import json

def test_login_detailed():
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("=== TESTE DETALHADO DE LOGIN ===")
    print(f"Backend: {backend_url}")
    print()
    
    # Dados de teste do usuário admin criado no setup
    test_data = {
        "cpf": "00000000000", 
        "senha": "0000"
    }
    
    # Headers necessários
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://frontend-painel-universal-production.up.railway.app'
    }
    
    try:
        print("1. Fazendo POST para /api/auth/login...")
        print(f"   Dados: {test_data}")
        print(f"   Headers: {headers}")
        
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json=test_data,
            headers=headers,
            timeout=15
        )
        
        print(f"\n2. Resposta recebida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Tentar decodificar resposta
        try:
            response_json = response.json()
            print(f"   JSON Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"   Raw Response: {response.text}")
        
        # Verificar headers CORS específicos
        cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
        if cors_headers:
            print(f"\n3. Headers CORS encontrados:")
            for header, value in cors_headers.items():
                print(f"   {header}: {value}")
        else:
            print(f"\n3. ❌ NENHUM header CORS encontrado!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    print("\n" + "="*50)
    
    # Teste com dados inválidos para comparar
    try:
        print("\n4. TESTE COMPARATIVO - Dados inválidos:")
        invalid_data = {"cpf": "99999999999", "senha": "wrong"}
        
        response2 = requests.post(
            f"{backend_url}/api/auth/login",
            json=invalid_data,
            headers=headers,
            timeout=15
        )
        
        print(f"   Status: {response2.status_code}")
        try:
            print(f"   Response: {response2.json()}")
        except:
            print(f"   Raw: {response2.text}")
            
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    test_login_detailed()