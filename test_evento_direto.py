#!/usr/bin/env python3
"""
Teste direto do endpoint de criação de eventos para diagnosticar erro 500
"""

import requests
import json
from datetime import datetime, timezone

def test_evento_endpoint():
    """Testa o endpoint de criação de eventos"""
    
    url = "http://localhost:8000/api/eventos/test"
    
    # Dados do evento para teste
    data = {
        "nome": "Teste API Direto",
        "local": "Local Teste API",
        "data_evento": "2025-09-04T06:45:00",
        "limite_idade": 18,
        "capacidade_maxima": 100,
        "endereco": "Endereço Teste",
        "descricao": "Evento criado via teste direto da API"
    }
    
    print("🚀 Testando endpoint de criação de eventos...")
    print(f"URL: {url}")
    print(f"Dados: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print("❌ ERRO!")
            print(f"📄 Response Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        print(f"📄 Response Text: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_evento_endpoint_auth():
    """Testa o endpoint principal (com autenticação)"""
    
    # Primeiro fazer login para obter token
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "cpf": "00000000000",
        "senha": "0000"
    }
    
    print("\n🔐 Fazendo login para obter token...")
    
    try:
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"📄 Response: {login_response.text}")
            return False
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ Token não encontrado na resposta do login")
            return False
            
        print(f"✅ Login realizado com sucesso")
        print(f"🔑 Token: {token[:50]}...")
        
        # Agora testar criação de evento com autenticação
        url = "http://localhost:8000/api/eventos/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "nome": "Teste API Autenticado",
            "local": "Local Teste API Auth",
            "data_evento": "2025-09-04T06:45:00",
            "limite_idade": 18,
            "capacidade_maxima": 100,
            "endereco": "Endereço Teste Auth",
            "descricao": "Evento criado via teste autenticado da API"
        }
        
        print(f"\n🚀 Testando endpoint autenticado...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Dados: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print("❌ ERRO!")
            print(f"📄 Response Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste autenticado: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTE DIAGNÓSTICO - CRIAÇÃO DE EVENTOS")
    print("=" * 70)
    
    # Teste 1: Endpoint sem autenticação
    print("\n1️⃣ TESTE SEM AUTENTICAÇÃO")
    success1 = test_evento_endpoint()
    
    # Teste 2: Endpoint com autenticação
    print("\n2️⃣ TESTE COM AUTENTICAÇÃO")
    success2 = test_evento_endpoint_auth()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Teste sem auth: {'✅ PASSOU' if success1 else '❌ FALHOU'}")
    print(f"Teste com auth: {'✅ PASSOU' if success2 else '❌ FALHOU'}")
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram! O problema não é na API.")
    elif success1 and not success2:
        print("\n⚠️ Problema específico com autenticação ou endpoint principal.")
    elif not success1 and not success2:
        print("\n🚨 Problema geral na API de criação de eventos.")
    else:
        print("\n🤔 Resultado inconsistente entre os testes.")
