#!/usr/bin/env python3
"""
🔍 DEBUG: Testar resposta do endpoint /me
Verifica se o backend está retornando os dados corretos
"""

import os
import requests
import json

def test_auth_endpoint():
    """Testar endpoint de autenticação"""
    print("🔍 TESTE DO ENDPOINT /auth/me")
    print("=" * 50)
    
    # URLs para testar
    urls = [
        "https://backend-painel-universal-production.up.railway.app",
        "http://localhost:8000"
    ]
    
    for base_url in urls:
        print(f"\n🌐 Testando: {base_url}")
        
        try:
            # 1. Testar health
            health_response = requests.get(f"{base_url}/healthz", timeout=5)
            print(f"   Health: {health_response.status_code}")
            
            # 2. Testar login com usuário demo
            test_users = [
                {"cpf": "00000000000", "senha": "admin123"},  # Admin padrão
                {"cpf": "00000000000", "senha": "0000"},      # Admin alternativo
                {"cpf": "11111111111", "senha": "promoter123"},  # Promoter padrão
                {"cpf": "12345678901", "senha": "123456"},    # Usuário genérico
            ]
            
            success = False
            for user_data in test_users:
                print(f"   🔐 Testando login: {user_data['cpf'][:3]}***{user_data['cpf'][-3:]}")
                login_response = requests.post(
                    f"{base_url}/api/auth/login",
                    json=user_data,
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    success = True
                    break
                else:
                    print(f"     ❌ {login_response.status_code}: {login_response.text[:100]}")
            
            if success:
                login_result = login_response.json()
                token = login_result.get("access_token")
                
                if token:
                    print("   ✅ Login bem-sucedido")
                    print(f"   🔑 Token: {token[:20]}...")
                    
                    # 3. Testar endpoint /me
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get(
                        f"{base_url}/api/auth/me",
                        headers=headers,
                        timeout=10
                    )
                    
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print("   ✅ Endpoint /me funcionando")
                        print("   📊 Dados do usuário:")
                        print(f"     ID: {user_data.get('id')}")
                        print(f"     Nome: {user_data.get('nome')}")
                        print(f"     CPF: {user_data.get('cpf')}")
                        print(f"     Email: {user_data.get('email')}")
                        print(f"     Tipo: {user_data.get('tipo')}")
                        print(f"     Ativo: {user_data.get('ativo')}")
                        
                        # Verificar se tem o campo 'tipo'
                        if user_data.get('tipo'):
                            print(f"   ✅ Campo 'tipo' presente: {user_data.get('tipo')}")
                        else:
                            print(f"   ❌ Campo 'tipo' ausente!")
                            print(f"   📋 Campos disponíveis: {list(user_data.keys())}")
                        
                        return True
                    else:
                        print(f"   ❌ Erro no /me: {me_response.status_code}")
                        print(f"   📝 Resposta: {me_response.text[:200]}")
                else:
                    print("   ❌ Token não encontrado na resposta")
            else:
                print(f"   ❌ Erro no login: {login_response.status_code}")
                if login_response.text:
                    print(f"   📝 Resposta: {login_response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            
    return False

if __name__ == "__main__":
    success = test_auth_endpoint()
    
    if success:
        print("\n✅ Teste concluído com sucesso")
    else:
        print("\n❌ Teste falhou")
