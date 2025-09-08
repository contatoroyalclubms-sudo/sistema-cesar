import requests
import json

url = 'http://localhost:8000/api/auth/login'

# Teste 1: CPF sem formatação
data1 = {
    'cpf': '00000000000',
    'senha': '0000'
}

print('Testando CPF sem formatação:')
try:
    response = requests.post(url, json=data1)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    if response.status_code == 200:
        print('✅ LOGIN COM SUCESSO!')
except Exception as e:
    print(f'Erro: {e}')

print('\n' + '='*50 + '\n')

# Teste 2: CPF com formatação
data2 = {
    'cpf': '000.000.000-00',
    'senha': '0000'
}

print('Testando CPF com formatação:')
try:
    response = requests.post(url, json=data2)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    if response.status_code == 200:
        print('✅ LOGIN COM SUCESSO!')
except Exception as e:
    print(f'Erro: {e}')
