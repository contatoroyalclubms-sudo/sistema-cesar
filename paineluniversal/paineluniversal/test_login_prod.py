#!/usr/bin/env python3
"""
Script para testar login na produção com credenciais corretas
"""

import requests
import json

def test_production_login():
    """Testa login na produção"""
    
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    frontend_url = "https://frontend-painel-universal-production.up.railway.app"
    
    print("🔐 Testando Login na Produção")
    print("-" * 40)
    
    # Credenciais do setup inicial
    credentials = [
        {"cpf": "00000000000", "senha": "0000", "tipo": "admin"},
        {"cpf": "11111111111", "senha": "promoter123", "tipo": "promoter"}
    ]
    
    for cred in credentials:
        print(f"\n🧪 Testando {cred['tipo']}: {cred['cpf']}")
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Origin': frontend_url
            }
            data = {
                "cpf": cred['cpf'],
                "senha": cred['senha']
            }
            
            response = requests.post(f"{backend_url}/api/auth/login", 
                                   headers=headers, 
                                   json=data, 
                                   timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 202:
                data = response.json()
                print(f"   ✅ Código de verificação solicitado!")
                print(f"   Mensagem: {data['detail'][:100]}...")
            elif response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login bem-sucedido: {data['usuario']['nome']}")
            else:
                print(f"   ❌ Erro: {response.json()}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_production_login()
