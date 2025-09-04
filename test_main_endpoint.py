#!/usr/bin/env python3

import requests
import json

def test_main_endpoint():
    """Testa o endpoint principal de criação de eventos"""
    
    url = "http://localhost:8000/api/eventos/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidXNlcm5hbWUiOiJhZG1pbl90ZXN0ZSIsInRpcG8iOiJhZG1pbiIsImVtcHJlc2FfaWQiOm51bGwsImV4cCI6MTczMzI1OTE5MH0.k6crq0LdH-K98bvqmQdQU3b8AJCvF9qbT-RDOw-l2hY"
    }
    
    data = {
        "nome": "Teste Endpoint Principal",
        "data_evento": "2025-09-05T19:00:00",
        "local": "Local de Teste Principal",
        "endereco": "Endereco Teste Principal",
        "limite_idade": 18,
        "capacidade_maxima": 100,
        "descricao": "Teste do endpoint principal de criação"
    }
    
    print("🔄 Testando endpoint principal de criação de eventos...")
    print(f"URL: {url}")
    print(f"Dados: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\n📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Evento criado com ID: {result['id']}")
            print(f"📝 Resposta: {json.dumps(result, indent=2)}")
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
    test_main_endpoint()
