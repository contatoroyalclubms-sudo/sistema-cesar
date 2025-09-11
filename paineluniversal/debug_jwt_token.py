import requests
import json
import jwt
import base64

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
    
    # 2. Decodificar o JWT para ver o payload
    print("\n🔍 Decodificando JWT...")
    try:
        # Decodificar sem verificar a assinatura primeiro para ver o payload
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        print(f"JWT Header: {json.dumps(header, indent=2)}")
        print(f"JWT Payload: {json.dumps(payload, indent=2)}")
        
        # Verificar se o payload tem 'sub' (CPF)
        sub = payload.get("sub")
        print(f"Subject (sub): {sub}")
        print(f"CPF Type: {type(sub)}")
        
        # Verificar se tem expiração
        exp = payload.get("exp")
        if exp:
            import datetime
            exp_date = datetime.datetime.fromtimestamp(exp)
            now = datetime.datetime.now()
            print(f"Expira em: {exp_date}")
            print(f"Agora: {now}")
            print(f"Token válido: {exp_date > now}")
        
    except Exception as e:
        print(f"❌ Erro ao decodificar JWT: {e}")
    
    # 3. Testar o endpoint /me novamente
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
        
else:
    print(f"❌ Erro no login: {login_response.text}")
