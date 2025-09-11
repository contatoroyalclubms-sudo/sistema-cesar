#!/usr/bin/env python3
"""
Teste simples usando requests para verificar o endpoint de registro
"""
import requests
import json
import time

def test_simple():
    url = "http://localhost:8003/api/auth/register"
    
    test_time = int(time.time())
    data = {
        "nome": f"Teste API {test_time}",
        "email": f"api{test_time}@teste.com", 
        "cpf": f"111{test_time}"[-11:],
        "senha": "123456",  # Corrigido para senha
        "tipo": "CLIENTE"
    }
    
    print(f"🧪 Testando registro: {data['email']}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    if test_simple():
        print("✅ Sucesso!")
    else:
        print("❌ Falha!")
