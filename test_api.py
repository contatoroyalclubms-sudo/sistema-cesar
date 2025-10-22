#!/usr/bin/env python3
"""
Script de teste rápido para validar os endpoints principais
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Testa o endpoint de health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_auth():
    """Testa o endpoint de autenticação"""
    try:
        data = {
            "email": "admin@meep.com.br",
            "senha": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=5)
        print(f"✅ Auth Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"   Token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get('access_token')
        return None
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        return None

def test_empresas(token=None):
    """Testa os endpoints de empresas"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        # Testar GET /api/empresas
        response = requests.get(f"{BASE_URL}/api/empresas", headers=headers, timeout=5)
        print(f"✅ GET Empresas: {response.status_code}")
        
        # Testar rota deprecated /api/empresas/listar
        response = requests.get(f"{BASE_URL}/api/empresas/listar", timeout=5)
        print(f"✅ GET Empresas (deprecated): {response.status_code}")
        
    except Exception as e:
        print(f"❌ Empresas Failed: {e}")

def test_openapi():
    """Testa se a documentação OpenAPI está acessível"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"✅ OpenAPI Spec: {response.status_code}")
        
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ Docs UI: {response.status_code}")
        
    except Exception as e:
        print(f"❌ OpenAPI Failed: {e}")

def main():
    print("🧪 Executando testes de validação da API NIP")
    print("=" * 50)
    
    # Testar health
    if not test_health():
        print("❌ Servidor não está respondendo. Verifique se está rodando na porta 8000.")
        sys.exit(1)
    
    # Testar autenticação
    token = test_auth()
    
    # Testar empresas
    test_empresas(token)
    
    # Testar documentação
    test_openapi()
    
    print("=" * 50)
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main()