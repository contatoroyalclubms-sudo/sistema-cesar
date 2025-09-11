#!/usr/bin/env python3
"""
🧪 TESTE: Sistema de Login Após Migração
Verificar se login funciona corretamente após correção do schema
"""

import requests
import json
import sys
import os

# Configuração da API
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/auth/login"

def test_login_response_structure():
    """Testar estrutura da resposta de login"""
    print("🧪 TESTE: Estrutura da Resposta de Login")
    print("=" * 50)
    
    # Credenciais de teste (do diagnóstico anterior)
    test_credentials = [
        {"cpf": "12345678901", "senha": "admin123"},  # Admin
        {"cpf": "11111111111", "senha": "promoter123"},  # Promoter  
        {"cpf": "22222222222", "senha": "cliente123"}   # Cliente
    ]
    
    for i, cred in enumerate(test_credentials, 1):
        print(f"\n🔍 Teste {i}: CPF {cred['cpf']}")
        
        try:
            response = requests.post(
                LOGIN_ENDPOINT,
                data=cred,  # Enviar como form data
                timeout=10
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Resposta JSON válida")
                    
                    # Verificar campos obrigatórios
                    has_access_token = 'access_token' in data
                    has_usuario = 'usuario' in data
                    
                    print(f"   🔑 access_token: {'✅' if has_access_token else '❌'}")
                    print(f"   👤 usuario: {'✅' if has_usuario else '❌'}")
                    
                    if has_access_token:
                        print(f"      Token: {str(data['access_token'])[:20]}...")
                    
                    if has_usuario:
                        usuario = data['usuario']
                        print(f"   👤 Dados do usuário:")
                        print(f"      ID: {usuario.get('id', 'N/A')}")
                        print(f"      Nome: {usuario.get('nome', 'N/A')}")
                        print(f"      CPF: {usuario.get('cpf', 'N/A')}")
                        print(f"      Email: {usuario.get('email', 'N/A')}")
                        print(f"      Tipo: {usuario.get('tipo_usuario', 'N/A')}")
                        print(f"      Ativo: {usuario.get('ativo', 'N/A')}")
                        
                        # Verificar se tem todos os campos esperados
                        required_fields = ['id', 'nome', 'cpf', 'email', 'tipo_usuario']
                        missing_fields = [field for field in required_fields if field not in usuario]
                        
                        if missing_fields:
                            print(f"      ⚠️ Campos faltando: {missing_fields}")
                        else:
                            print(f"      ✅ Todos os campos obrigatórios presentes")
                    
                    # Verificar se resposta atende frontend
                    frontend_valid = has_access_token and has_usuario
                    print(f"   🎯 Compatível com frontend: {'✅' if frontend_valid else '❌'}")
                    
                except json.JSONDecodeError:
                    print(f"   ❌ Resposta não é JSON válido")
                    print(f"   📄 Conteúdo: {response.text[:200]}...")
                    
            elif response.status_code == 401:
                print(f"   🔐 Credenciais inválidas (esperado para credenciais de teste)")
                
            elif response.status_code == 422:
                print(f"   📋 Erro de validação")
                try:
                    error_data = response.json()
                    print(f"   ❌ Detalhes: {error_data}")
                except:
                    print(f"   📄 Resposta: {response.text}")
                    
            else:
                print(f"   ❌ Erro inesperado")
                print(f"   📄 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão - backend não está rodando?")
            print(f"   💡 Execute: uvicorn main:app --reload")
            break
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_with_valid_credentials():
    """Testar com credenciais conhecidas do banco"""
    print(f"\n🧪 TESTE: Credenciais Reais do Banco")
    print("=" * 40)
    
    # Vamos tentar com os usuários que sabemos que existem
    real_users = [
        {"cpf": "11756283503", "senha": "123456"},    # Usuário real do banco
        {"cpf": "11756395530", "senha": "123456"},    # Outro usuário real
    ]
    
    for cred in real_users:
        print(f"\n🔍 Testando CPF: {cred['cpf']}")
        
        try:
            response = requests.post(LOGIN_ENDPOINT, data=cred, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ LOGIN FUNCIONANDO!")
                print(f"   🎯 Resposta completa recebida")
                
                if 'usuario' in data:
                    usuario = data['usuario']
                    print(f"   👤 Usuário: {usuario.get('nome')} ({usuario.get('tipo_usuario')})")
                    
            elif response.status_code == 401:
                print(f"   🔐 Credenciais incorretas")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Backend não está rodando")
            return False
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return True

if __name__ == "__main__":
    if test_with_valid_credentials():
        test_login_response_structure()
