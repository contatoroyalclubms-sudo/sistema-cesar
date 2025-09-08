#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_event_creation():
    url = "http://localhost:8000/api/eventos/test"
    
    data = {
        "nome": "Teste Simples 2025",
        "data_evento": "2025-09-04T20:00:00",
        "local": "Local Teste",
        "endereco": "Endereco Teste",
        "limite_idade": 18,
        "capacidade_maxima": 100,
        "descricao": "Teste via script Python"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testando criação de evento...")
        print(f"URL: {url}")
        print(f"Dados: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\nResposta:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Conteúdo: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCESSO: Evento criado!")
            event_data = response.json()
            print(f"ID do evento: {event_data.get('id')}")
            print(f"Nome: {event_data.get('nome')}")
        else:
            print(f"\n❌ ERRO: {response.status_code}")
            print(f"Detalhes: {response.text}")
            
    except Exception as e:
        print(f"\n💥 EXCEÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_event_creation()
