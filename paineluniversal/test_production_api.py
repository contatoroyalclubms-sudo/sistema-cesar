#!/usr/bin/env python3

"""
Script para testar criação de evento em produção
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações de produção
API_BASE = "https://backend-painel-universal-production.up.railway.app"
FRONTEND_BASE = "https://frontend-painel-universal-production.up.railway.app"

def test_login():
    """Testa login e obtém token"""
    login_url = f"{API_BASE}/api/auth/login"
    
    # Dados de teste (substitua pelos dados reais)
    login_data = {
        "cpf": "12345678901",  # Substitua pelo CPF real
        "senha": "senha123"    # Substitua pela senha real
    }
    
    print(f"🔐 Tentando login em: {login_url}")
    print(f"📤 Dados: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            print(f"❌ Login falhou: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 Erro na requisição de login: {e}")
        return None

def test_create_evento(token):
    """Testa criação de evento"""
    if not token:
        print("❌ Token não disponível")
        return
    
    eventos_url = f"{API_BASE}/api/eventos/"
    
    # Data 1 hora no futuro
    data_evento = datetime.now() + timedelta(hours=1)
    data_iso = data_evento.isoformat()
    
    evento_data = {
        "nome": "Teste Evento API",
        "descricao": "Teste de criação via API",
        "data_evento": data_iso,
        "local": "Local Teste",
        "endereco": "Endereço Teste",
        "limite_idade": 18,
        "capacidade_maxima": 100
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"🎫 Criando evento em: {eventos_url}")
    print(f"📤 Headers: {json.dumps(dict(headers), indent=2)}")
    print(f"📤 Dados: {json.dumps(evento_data, indent=2)}")
    
    try:
        response = requests.post(eventos_url, json=evento_data, headers=headers)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Evento criado com sucesso!")
            return response.json()
        else:
            print(f"❌ Falha na criação: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📋 Detalhes do erro: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📋 Resposta não-JSON: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Erro na requisição de criação: {e}")
        return None

def test_different_date_formats(token):
    """Testa diferentes formatos de data"""
    if not token:
        print("❌ Token não disponível")
        return
    
    eventos_url = f"{API_BASE}/api/eventos/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Diferentes formatos de data para testar
    data_base = datetime.now() + timedelta(hours=2)
    
    formatos = [
        ("ISO com Z", data_base.isoformat() + "Z"),
        ("ISO sem Z", data_base.isoformat()),
        ("ISO com timezone", data_base.isoformat() + "+00:00"),
        ("ISO datetime", data_base.strftime("%Y-%m-%dT%H:%M:%S")),
    ]
    
    for nome_formato, data_str in formatos:
        print(f"\n🧪 Testando formato: {nome_formato}")
        print(f"📅 Data: {data_str}")
        
        evento_data = {
            "nome": f"Teste {nome_formato}",
            "data_evento": data_str,
            "local": "Local Teste"
        }
        
        try:
            response = requests.post(eventos_url, json=evento_data, headers=headers)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code not in [200, 201]:
                print(f"❌ Erro: {response.text[:200]}")
            else:
                print(f"✅ Sucesso com formato: {nome_formato}")
                
        except Exception as e:
            print(f"💥 Erro: {e}")

if __name__ == "__main__":
    print("🚀 Testando API de produção...")
    print("="*50)
    
    # Passo 1: Login
    token = test_login()
    
    if token:
        print(f"\n✅ Token obtido: {token[:20]}...")
        
        # Passo 2: Teste criação básica
        print("\n" + "="*50)
        print("📝 Testando criação de evento...")
        test_create_evento(token)
        
        # Passo 3: Teste diferentes formatos de data
        print("\n" + "="*50)
        print("📅 Testando formatos de data...")
        test_different_date_formats(token)
    else:
        print("\n❌ Não foi possível obter token - verifique credenciais")
    
    print("\n🏁 Teste concluído!")
