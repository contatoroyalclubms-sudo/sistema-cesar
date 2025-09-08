#!/usr/bin/env python3
"""
Script para debugar problemas de login
"""

import requests
import json

def debug_login():
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("Debugando endpoint de login...")
    print(f"Backend: {backend_url}")
    print("-" * 60)
    
    # Teste 1: Verificar se endpoint existe
    try:
        print("1. Testando OPTIONS do endpoint login...")
        response = requests.options(f"{backend_url}/api/auth/login", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers disponíveis: {dict(response.headers)}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 2: Testar com dados vazios
    try:
        print("2. Testando login com dados vazios...")
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json={},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Response text: {response.text[:500]}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 3: Testar com CPF inválido mas estrutura correta
    try:
        print("3. Testando login com dados inválidos...")
        data = {
            "cpf": "123456789",
            "senha": "teste123"
        }
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response text: {response.text[:500]}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 4: Testar com usuário demo
    try:
        print("4. Testando login com usuário demo...")
        data = {
            "cpf": "00000000000",
            "senha": "0000"
        }
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response text: {response.text[:500]}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    
    # Teste 5: Verificar se database está funcionando
    try:
        print("5. Testando setup inicial (criacao de usuarios demo)...")
        response = requests.post(
            f"{backend_url}/setup-inicial",
            timeout=15
        )
        print(f"   Status: {response.status_code}")
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response text: {response.text[:500]}")
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    debug_login()