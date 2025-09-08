
#!/usr/bin/env python3
"""
Script para testar CORS em produção
"""

import requests
import json

def test_cors():
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    frontend_origin = "https://frontend-painel-universal-production.up.railway.app"
    
    print("Testando CORS em producao...")
    print(f"Backend: {backend_url}")
    print(f"Frontend Origin: {frontend_origin}")
    print("-" * 50)
    
    # Teste 1: Health check
    try:
        print("1. Testando health check...")
        response = requests.get(f"{backend_url}/healthz", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Environment: {data.get('environment', 'unknown')}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 2: CORS test endpoint  
    try:
        print("2. Testando CORS endpoint...")
        headers = {'Origin': frontend_origin}
        response = requests.get(f"{backend_url}/api/cors-test", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Environment: {data.get('environment')}")
            print(f"   Allowed Origins: {data.get('allowed_origins')}")
        
        # Headers CORS
        cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
        if cors_headers:
            print("   CORS Headers encontrados:")
            for header, value in cors_headers.items():
                print(f"      {header}: {value}")
        else:
            print("   AVISO: Nenhum header CORS encontrado!")
            
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 3: Login preflight
    try:
        print("3. Testando preflight para login...")
        headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        response = requests.options(f"{backend_url}/api/auth/login", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
        if cors_headers:
            print("   CORS Headers:")
            for header, value in cors_headers.items():
                print(f"      {header}: {value}")
        else:
            print("   AVISO: Nenhum header CORS no preflight!")
            
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    test_cors()