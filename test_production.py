#!/usr/bin/env python3
"""
Script para testar conectividade entre frontend e backend de produção
"""

import requests
import json
from datetime import datetime

def test_production_cors():
    """Testa CORS e conectividade do backend de produção"""
    
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    frontend_url = "https://frontend-painel-universal-production.up.railway.app"
    
    print("🚀 Testando Backend de Produção")
    print(f"Backend URL: {backend_url}")
    print(f"Frontend URL: {frontend_url}")
    print("-" * 60)
    
    # Teste 1: Health check
    try:
        response = requests.get(f"{backend_url}/healthz", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check falhou: {e}")
    
    # Teste 2: API Health
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=10)
        print(f"✅ API Health: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ API Health falhou: {e}")
    
    # Teste 3: CORS Preflight
    try:
        headers = {
            'Origin': frontend_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        response = requests.options(f"{backend_url}/api/auth/login", headers=headers, timeout=10)
        print(f"✅ CORS Preflight: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS Preflight falhou: {e}")
    
    # Teste 4: Login request
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': frontend_url
        }
        data = {
            "cpf": "00000000000",
            "senha": "0000"
        }
        response = requests.post(f"{backend_url}/api/auth/login", 
                               headers=headers, 
                               json=data, 
                               timeout=10)
        print(f"✅ Login Request: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Login Request falhou: {e}")
    
    print("-" * 60)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    test_production_cors()
