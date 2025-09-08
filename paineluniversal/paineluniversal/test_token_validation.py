import requests
import json

# 1. Fazer login e obter token
print("🔐 Fazendo login...")
login_response = requests.post("http://localhost:8000/api/auth/login", json={
    "cpf": "06601206154",
    "senha": "101112"
})

print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ Token obtido: {token[:50]}...")
    
    # 2. Testar o endpoint /me com o token
    print("\n🧪 Testando endpoint /me...")
    me_response = requests.get("http://localhost:8000/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    print(f"Endpoint /me status: {me_response.status_code}")
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"✅ Dados do usuário: {json.dumps(me_data, indent=2)}")
    else:
        print(f"❌ Erro no endpoint /me: {me_response.text}")
    
    # 3. Testar o endpoint /dashboard/avancado que está falhando
    print("\n🧪 Testando endpoint /dashboard/avancado...")
    dashboard_response = requests.get("http://localhost:8000/api/dashboard/avancado", headers={
        "Authorization": f"Bearer {token}"
    })
    
    print(f"Endpoint /dashboard/avancado status: {dashboard_response.status_code}")
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"✅ Dados do dashboard: {json.dumps(dashboard_data, indent=2)}")
    else:
        print(f"❌ Erro no endpoint /dashboard/avancado: {dashboard_response.text}")
        
    # 4. Testar endpoint /eventos que também está falhando
    print("\n🧪 Testando endpoint /eventos...")
    eventos_response = requests.get("http://localhost:8000/api/eventos/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    print(f"Endpoint /eventos status: {eventos_response.status_code}")
    if eventos_response.status_code == 200:
        eventos_data = eventos_response.json()
        print(f"✅ Dados dos eventos: {json.dumps(eventos_data, indent=2)}")
    else:
        print(f"❌ Erro no endpoint /eventos: {eventos_response.text}")
        
else:
    print(f"❌ Erro no login: {login_response.text}")
