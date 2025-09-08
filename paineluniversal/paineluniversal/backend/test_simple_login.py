#!/usr/bin/env python3
import requests
import json

backend_url = "https://backend-painel-universal-production.up.railway.app"

print("Testando login com usuario admin...")
data = {"cpf": "00000000000", "senha": "0000"}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(f"{backend_url}/api/auth/login", json=data, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    # Headers CORS
    cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
    print(f"CORS Headers: {cors_headers}")
    
    if response.status_code == 500:
        print("ERRO 500 - Servidor interno")
        print(f"Raw response: {response.text}")
        
        # Testar se middleware CORS está funcionando
        print("\nTestando CORS test endpoint...")
        cors_response = requests.get(f"{backend_url}/api/cors-test", headers={'Origin': 'test'})
        print(f"CORS test status: {cors_response.status_code}")
        if cors_response.status_code == 200:
            print("CORS middleware funcionando!")
            print(f"Response: {cors_response.json()}")
        
    else:
        print(f"Response: {response.json()}")
        
except Exception as e:
    print(f"Erro: {e}")

print("\nTestando com dados invalidos para comparar...")
try:
    invalid_response = requests.post(f"{backend_url}/api/auth/login", 
                                   json={"cpf": "invalid", "senha": "wrong"}, 
                                   headers=headers, timeout=10)
    print(f"Status dados invalidos: {invalid_response.status_code}")
    if invalid_response.status_code != 500:
        print(f"Response: {invalid_response.json()}")
except Exception as e:
    print(f"Erro dados invalidos: {e}")