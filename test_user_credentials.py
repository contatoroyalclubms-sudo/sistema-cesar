import requests

url = 'http://localhost:8000/api/auth/login'

# Teste com as credenciais solicitadas pelo usuário
data = {
    'cpf': '06601206154',
    'senha': '101112'
}

print('Testando credenciais solicitadas: CPF 06601206154, Senha 101112')
try:
    response = requests.post(url, json=data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}...' if len(response.text) > 200 else response.text)
    if response.status_code == 200:
        print('✅ LOGIN COM SUCESSO!')
        # Salvar token para testes posteriores
        token_data = response.json()
        with open('auth_token.txt', 'w') as f:
            f.write(token_data['access_token'])
        print('🔑 Token salvo em auth_token.txt')
    else:
        print('❌ LOGIN FALHOU!')
except Exception as e:
    print(f'Erro: {e}')
