#!/usr/bin/env python3
"""
Teste de login do usuário César no servidor local
"""

import requests
import json

def test_cesar_login():
    """Testar login do César no servidor local e produção"""
    
    # URLs de teste
    urls = {
        'LOCAL': 'http://localhost:8000/api/auth/login',
        'PRODUÇÃO': 'https://backend-painel-universal-production.up.railway.app/api/auth/login'
    }
    
    data = {'cpf': '06601206156', 'senha': '101112'}

    for env, url in urls.items():
        print(f'\n🔑 Testando login {env} com usuário César admin...')
        try:
            response = requests.post(url, json=data, timeout=15)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                result = response.json()
                print(f'✅ LOGIN SUCESSO em {env}!')
                print('📋 Dados do usuário:')
                if 'usuario' in result:
                    usuario = result['usuario']
                    print(f'   ID: {usuario.get("id")}')
                    print(f'   Nome: {usuario.get("nome")}')
                    print(f'   CPF: {usuario.get("cpf")}')
                    print(f'   Tipo: {usuario.get("tipo")}')
                    print(f'   Tipo_usuario: {usuario.get("tipo_usuario")}')
                    
                    # Verificar se é admin
                    tipo = usuario.get("tipo") or usuario.get("tipo_usuario")
                    if tipo == "admin":
                        print(f'🎉 CONFIRMADO: Usuário é ADMIN em {env}!')
                    else:
                        print(f'⚠️ Usuário não é admin em {env}: {tipo}')
                else:
                    print('❌ Campo usuario não encontrado na resposta')
                    print(f'Resposta completa: {result}')
            else:
                print(f'❌ Erro no login {env}: {response.text}')
                
        except requests.exceptions.ConnectionError:
            print(f'❌ Servidor {env} não está acessível.')
            if env == 'LOCAL':
                print('💡 Para iniciar: cd backend && python -m uvicorn app.main:app --reload --port 8000')
        except Exception as e:
            print(f'❌ Erro {env}: {e}')

if __name__ == "__main__":
    test_cesar_login()
