#!/usr/bin/env python3
"""
🔍 TESTE DIRETO DO BACKEND: Verificar resposta de login
"""

import requests
import json

def test_login_response_structure():
    """Testar estrutura da resposta do login"""
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("🔍 TESTE DA ESTRUTURA DE RESPOSTA DO LOGIN")
    print("=" * 60)
    
    # Credenciais para teste
    test_credentials = [
        {"cpf": "00000000000", "senha": "admin123"},
        {"cpf": "11111111111", "senha": "promoter123"},
        {"cpf": "12345678901", "senha": "123456"},
    ]
    
    for i, cred in enumerate(test_credentials, 1):
        print(f"\n{i}. Testando com CPF: {cred['cpf'][:3]}***{cred['cpf'][-3:]}")
        
        try:
            response = requests.post(
                f"{backend_url}/api/auth/login",
                json=cred,
                headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://frontend-painel-universal-production.up.railway.app'
                },
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Resposta JSON válida")
                    print(f"   📋 Keys principais: {list(data.keys())}")
                    
                    # Verificar campos obrigatórios
                    has_token = 'access_token' in data
                    has_usuario = 'usuario' in data
                    has_token_type = 'token_type' in data
                    
                    print(f"   🔑 access_token: {'✅' if has_token else '❌'}")
                    print(f"   👤 usuario: {'✅' if has_usuario else '❌'}")
                    print(f"   🏷️ token_type: {'✅' if has_token_type else '❌'}")
                    
                    if has_token:
                        print(f"   📝 Token (20 chars): {data['access_token'][:20]}...")
                    
                    if has_usuario:
                        usuario = data['usuario']
                        print(f"   👤 Dados do usuário:")
                        print(f"      ID: {usuario.get('id', 'N/A')}")
                        print(f"      Nome: {usuario.get('nome', 'N/A')}")
                        print(f"      Email: {usuario.get('email', 'N/A')}")
                        print(f"      Tipo: {usuario.get('tipo', 'N/A')}")
                        print(f"      Tipo_usuario: {usuario.get('tipo_usuario', 'N/A')}")
                        print(f"      Ativo: {usuario.get('ativo', 'N/A')}")
                        print(f"      Keys completas: {list(usuario.keys())}")
                    else:
                        print(f"   ❌ Campo 'usuario' ausente!")
                        print(f"   📋 Estrutura completa: {json.dumps(data, indent=2)}")
                    
                    # Verificar se atende aos requisitos do frontend
                    frontend_compatible = has_token and has_usuario
                    print(f"   🎯 Compatible com frontend: {'✅' if frontend_compatible else '❌'}")
                    
                    if frontend_compatible:
                        print(f"   🎉 LOGIN FUNCIONARÁ!")
                        return True
                    else:
                        print(f"   💥 LOGIN FALHARÁ - campos obrigatórios ausentes")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Resposta não é JSON válido")
                    print(f"   📝 Raw response: {response.text[:200]}")
                    
            elif response.status_code == 401:
                print(f"   🔐 Credenciais incorretas (esperado)")
                try:
                    error_data = response.json()
                    print(f"   📋 Erro: {error_data}")
                except:
                    print(f"   📝 Raw error: {response.text}")
                    
            elif response.status_code == 500:
                print(f"   💥 ERRO INTERNO DO SERVIDOR!")
                print(f"   📝 Response: {response.text[:300]}")
                
            else:
                print(f"   ⚠️ Status inesperado")
                print(f"   📝 Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout na requisição")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Erro de conexão")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"🔍 ANÁLISE CONCLUÍDA")
    print(f"Verifique os resultados acima para identificar o problema")
    return False

if __name__ == "__main__":
    test_login_response_structure()
