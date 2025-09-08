#!/usr/bin/env python3

import requests
import json

def get_new_token():
    """Faz login e obtém um novo token"""
    
    login_url = "http://localhost:8000/api/auth/login"
    
    data = {
        "cpf": "06601206154",
        "senha": "101112"
    }
    
    print("🔄 Fazendo login para obter novo token...")
    
    try:
        response = requests.post(login_url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print(f"✅ Login realizado! Token obtido.")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📝 Detalhes: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Erro na requisição de login: {e}")
        return None

def test_main_endpoint_with_new_token():
    """Testa o endpoint principal de criação de eventos com token novo"""
    
    # Obter novo token
    token = get_new_token()
    if not token:
        print("❌ Não foi possível obter token. Saindo.")
        return
    
    url = "http://localhost:8000/api/eventos/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "nome": "Teste Endpoint Principal Com Token Novo",
        "data_evento": "2025-09-05T19:00:00",
        "local": "Local de Teste Principal",
        "endereco": "Endereco Teste Principal",
        "limite_idade": 18,
        "capacidade_maxima": 100,
        "descricao": "Teste do endpoint principal de criação com token novo"
    }
    
    print(f"\n🔄 Testando endpoint principal de criação de eventos...")
    print(f"URL: {url}")
    print(f"Token: {token[:50]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\n📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Evento criado com ID: {result['id']}")
            print(f"📝 Nome: {result['nome']}")
        else:
            print(f"❌ Erro {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Detalhes: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta texto: {response.text}")
                
    except Exception as e:
        print(f"💥 Erro na requisição: {e}")

if __name__ == "__main__":
    test_main_endpoint_with_new_token()
