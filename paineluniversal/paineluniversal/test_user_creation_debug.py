#!/usr/bin/env python3
"""
Teste detalhado de criação de usuário com debug
"""

import requests
import json

def test_detailed_user_creation():
    base_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("🔐 1. Fazendo login do César...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        'cpf': '06601206156', 
        'senha': '101112'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Falha no login: {login_response.status_code} - {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data.get('access_token')
    usuario = login_data.get('usuario')
    
    print(f"✅ Login OK!")
    print(f"   Token: {token[:20]}...")
    print(f"   Usuário: {usuario.get('nome')}")
    print(f"   Tipo: {usuario.get('tipo')}")
    print(f"   ID: {usuario.get('id')}")
    
    print("\n👤 2. Testando criação de usuário...")
    
    headers = {
        'Authorization': f'Bearer {token}', 
        'Content-Type': 'application/json'
    }
    
    test_user = {
        "cpf": "99999999901",
        "nome": "Teste Usuario Debug",
        "email": "debug@teste.com",
        "telefone": "11999999999",
        "senha": "teste123",
        "tipo": "cliente"
    }
    
    print(f"   Enviando dados: {json.dumps(test_user, indent=2)}")
    print(f"   Headers: Authorization: Bearer {token[:20]}...")
    
    create_response = requests.post(f"{base_url}/api/usuarios/", 
                                  json=test_user, 
                                  headers=headers)
    
    print(f"\n📊 3. Resultado da criação:")
    print(f"   Status: {create_response.status_code}")
    print(f"   Headers: {dict(create_response.headers)}")
    print(f"   Resposta: {create_response.text}")
    
    if create_response.status_code == 200:
        created_user = create_response.json()
        print(f"   ✅ Usuário criado com sucesso!")
        print(f"   ID: {created_user.get('id')}")
        print(f"   Nome: {created_user.get('nome')}")
        print(f"   Tipo: {created_user.get('tipo')}")
    else:
        print(f"   ❌ Falha na criação!")
        
        # Testar se o problema é no endpoint /me
        print(f"\n🔍 4. Testando endpoint /me para verificar token...")
        me_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        print(f"   Status /me: {me_response.status_code}")
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"   ✅ Token válido - Usuário: {me_data.get('nome')}")
            print(f"   Tipo: {me_data.get('tipo')}")
        else:
            print(f"   ❌ Token inválido: {me_response.text}")

if __name__ == "__main__":
    test_detailed_user_creation()
