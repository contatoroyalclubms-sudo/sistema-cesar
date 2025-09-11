#!/usr/bin/env python3
"""
Teste de debug para identificar problema no login
"""
import requests
import json

# Testar diferentes URLs e métodos para identificar o problema
backend_urls = [
    "https://backend-painel-universal-production.up.railway.app",
    "http://localhost:8000"
]

# Diferentes combinações de teste
test_cases = [
    {"cpf": "00000000000", "senha": "admin123"},
    {"cpf": "000.000.000-00", "senha": "admin123"}, 
    {"cpf": "11111111111", "senha": "promoter123"},
    {"cpf": "111.111.111-11", "senha": "promoter123"}
]

for base_url in backend_urls:
    print(f"\n{'='*50}")
    print(f"TESTANDO: {base_url}")
    print(f"{'='*50}")
    
    # Primeiro testar se o servidor está rodando
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"OK Servidor UP - Health status: {health_response.status_code}")
    except Exception as e:
        print(f"XX Servidor DOWN - Error: {e}")
        continue
    
    # Testar setup inicial
    print(f"\nTESTANDO SETUP INICIAL...")
    try:
        setup_response = requests.post(f"{base_url}/setup-inicial", timeout=10)
        print(f"Setup status: {setup_response.status_code}")
        if setup_response.status_code == 200:
            setup_data = setup_response.json()
            print(f"Usuarios criados: {len(setup_data.get('usuarios_criados', []))}")
        else:
            print(f"Setup response: {setup_response.text[:200]}")
    except Exception as e:
        print(f"Setup error: {e}")
    
    # Testar cada caso de login
    for i, case in enumerate(test_cases, 1):
        print(f"\nTESTE {i}: CPF={case['cpf'][:3]}***{case['cpf'][-3:]} | Senha={case['senha']}")
        
        headers = {
            'Content-Type': 'application/json', 
            'Origin': 'https://frontend-painel-universal-production.up.railway.app'
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/auth/login", 
                json=case, 
                headers=headers, 
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   LOGIN SUCESSO! Token: {data.get('access_token', '')[:20]}...")
                print(f"   Usuario: {data.get('usuario', {}).get('nome', 'N/A')}")
                break  # Sucesso, não precisa testar outros
            elif response.status_code == 401:
                print(f"   Credenciais invalidas: {response.json()}")
            elif response.status_code == 500:
                print(f"   Erro interno: {response.text[:200]}")
            else:
                print(f"   Status inesperado: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")
            
    break  # Testar só o primeiro servidor que estiver UP