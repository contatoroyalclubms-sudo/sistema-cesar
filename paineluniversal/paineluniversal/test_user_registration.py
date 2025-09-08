#!/usr/bin/env python3
"""
Teste de registro de usuário para debug
"""

import requests
import json

# URL do backend - testar produção após push
API_BASE = "https://backend-painel-universal-production.up.railway.app"

def test_register():
    """Testar registro de usuário"""
    
    print("🧪 Testando registro de usuário...")
    
    # Dados de teste com CPF único
    import time
    timestamp = str(int(time.time()))[-4:]  # Últimos 4 dígitos do timestamp
    
    user_data = {
        "cpf": f"123456789{timestamp[-2:]}",  # CPF único
        "nome": "Usuário Teste",
        "email": f"teste{timestamp}@example.com",  # Email único
        "telefone": "11999999999",
        "senha": "senha123",
        "tipo": "cliente"
    }
    
    try:
        # Fazer requisição com timeout maior
        response = requests.post(
            f"{API_BASE}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60 segundos
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Registro bem-sucedido!")
            print(f"📱 Resposta: {response.json()}")
        else:
            print(f"❌ Erro no registro: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📱 Erro detalhado: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📱 Resposta texto: {response.text}")
                
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Verifique se o backend está rodando em localhost:8000")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def test_health():
    """Testar se o backend está funcionando"""
    
    print("🔍 Testando saúde do backend...")
    
    try:
        response = requests.get(f"{API_BASE}/healthz", timeout=5)
        print(f"✅ Backend OK: {response.status_code}")
        return True
    except:
        print("❌ Backend não está respondendo")
        return False

if __name__ == "__main__":
    print("🚀 Teste de Registro de Usuário")
    print("=" * 50)
    
    # Testar saúde primeiro
    if test_health():
        print()
        test_register()
    else:
        print("💡 Inicie o backend primeiro com: cd backend && python main.py")
