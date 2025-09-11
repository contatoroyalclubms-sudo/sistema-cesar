#!/usr/bin/env python3
import requests

backend_url = "https://backend-painel-universal-production.up.railway.app"

# Testar com senha correta agora
print("Testando login com senha correta (admin123)...")
data = {"cpf": "00000000000", "senha": "admin123"}
headers = {'Content-Type': 'application/json', 'Origin': 'https://frontend-painel-universal-production.up.railway.app'}

try:
    response = requests.post(f"{backend_url}/api/auth/login", json=data, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    # Verificar CORS headers
    cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
    if cors_headers:
        print(f"CORS Headers presentes: {cors_headers}")
    else:
        print("AVISO: Sem CORS headers")
    
    if response.status_code == 500:
        print("Ainda erro 500 - problema interno")
        print(f"Raw: {response.text}")
    elif response.status_code == 202:
        print("Sucesso! Codigo de verificacao solicitado")
        print(f"Response: {response.json()}")
    elif response.status_code == 401:
        print("Erro 401 - credenciais invalidas")  
        print(f"Response: {response.json()}")
    else:
        print(f"Status inesperado: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Raw: {response.text}")

except Exception as e:
    print(f"Erro: {e}")

# Testar também com a senha antiga para confirmar
print("\nTestando com senha antiga (0000) para confirmar erro...")
try:
    response2 = requests.post(f"{backend_url}/api/auth/login", 
                             json={"cpf": "00000000000", "senha": "0000"}, 
                             headers=headers, timeout=10)
    print(f"Status com senha antiga: {response2.status_code}")
    if response2.status_code != 500:
        print(f"Response: {response2.json()}")
except Exception as e:
    print(f"Erro: {e}")