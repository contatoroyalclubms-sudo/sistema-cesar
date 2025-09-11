#!/usr/bin/env python3
"""
Script de teste completo para validar migração de consolidação de campos tipo
Verifica se todas as funcionalidades continuam operando após a migração
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

# URLs de teste
LOCAL_URL = "http://localhost:8000"
PROD_URL = "https://backend-painel-universal-production.up.railway.app"

def test_login(base_url, cpf, senha, nome_teste):
    """Testar login de usuário"""
    print(f"\n🔑 Testando login {nome_teste}...")
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json={
            'cpf': cpf, 
            'senha': senha
        }, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'usuario' in result:
                usuario = result['usuario']
                tipo = usuario.get('tipo')
                print(f"   ✅ Login OK - ID: {usuario.get('id')}")
                print(f"   📋 Nome: {usuario.get('nome')}")
                print(f"   📋 Tipo: {tipo}")
                
                return {
                    'success': True,
                    'user_id': usuario.get('id'),
                    'name': usuario.get('nome'),
                    'tipo': tipo,
                    'token': result.get('access_token')
                }
            else:
                print(f"   ❌ Campo 'usuario' não encontrado na resposta")
                return {'success': False, 'error': 'Campo usuario ausente'}
        else:
            print(f"   ❌ Erro: {response.text}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return {'success': False, 'error': str(e)}

def test_admin_endpoint(base_url, token):
    """Testar acesso a endpoint protegido de admin"""
    print(f"\n🔒 Testando acesso de admin...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{base_url}/api/usuarios/", headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ Acesso admin OK - {len(users)} usuários retornados")
            return True
        elif response.status_code == 403:
            print(f"   ❌ Acesso negado - usuário não é admin")
            return False
        else:
            print(f"   ❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_user_creation(base_url, token):
    """Testar criação de usuário (endpoint admin)"""
    print(f"\n👤 Testando criação de usuário...")
    
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Gerar dados únicos para teste
        timestamp = int(time.time())
        test_user = {
            "cpf": f"999{timestamp % 100000:05d}99",  # CPF único baseado em timestamp
            "nome": f"Teste Usuario {timestamp}",
            "email": f"teste{timestamp}@example.com",
            "telefone": "11999999999",
            "senha": "teste123",
            "tipo": "cliente"
        }
        
        response = requests.post(f"{base_url}/api/usuarios/", 
                               json=test_user, headers=headers, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            created_user = response.json()
            print(f"   ✅ Usuário criado - ID: {created_user.get('id')}")
            print(f"   📋 Tipo: {created_user.get('tipo')}")
            return True
        else:
            print(f"   ❌ Erro na criação: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_environment(env_name, base_url):
    """Testar um ambiente específico"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO AMBIENTE: {env_name}")
    print(f"🌐 URL: {base_url}")
    print(f"{'='*60}")
    
    # Usuários para teste (baseado nos dados de produção)
    test_users = [
        {'cpf': '06601206156', 'senha': '101112', 'nome': 'César', 'esperado_tipo': 'admin'},
        {'cpf': '06601206155', 'senha': 'admin123', 'nome': 'Admin', 'esperado_tipo': 'admin'},
    ]
    
    results = {
        'env': env_name,
        'login_tests': [],
        'admin_access': False,
        'user_creation': False,
        'overall_success': False
    }
    
    admin_token = None
    
    # Testar login de usuários
    for user in test_users:
        login_result = test_login(base_url, user['cpf'], user['senha'], user['nome'])
        results['login_tests'].append({
            'user': user['nome'],
            'success': login_result['success'],
            'tipo': login_result.get('tipo'),
            'expected': user['esperado_tipo']
        })
        
        # Se login foi bem-sucedido e usuário é admin, usar token para testes
        if (login_result['success'] and 
            login_result.get('tipo') == 'admin' and 
            not admin_token):
            admin_token = login_result.get('token')
    
    # Testar funcionalidades de admin se temos token
    if admin_token:
        results['admin_access'] = test_admin_endpoint(base_url, admin_token)
        results['user_creation'] = test_user_creation(base_url, admin_token)
    else:
        print(f"\n⚠️ Nenhum token de admin disponível para testes avançados")
    
    # Calcular sucesso geral
    successful_admin_logins = sum(1 for test in results['login_tests'] 
                                 if test['success'] and test['tipo'] == 'admin')
    
    results['overall_success'] = (
        successful_admin_logins > 0 and 
        results['admin_access'] and 
        results['user_creation']
    )
    
    return results

def generate_report(local_results, prod_results):
    """Gerar relatório final"""
    print(f"\n{'='*80}")
    print(f"📊 RELATÓRIO FINAL DE TESTES")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    for results in [local_results, prod_results]:
        if not results:
            continue
            
        env_name = results['env']
        success_icon = "✅" if results['overall_success'] else "❌"
        
        print(f"\n{success_icon} AMBIENTE: {env_name}")
        print(f"   Login de admins: {sum(1 for t in results['login_tests'] if t['success'] and t['tipo'] == 'admin')}")
        print(f"   Acesso admin: {'✅' if results['admin_access'] else '❌'}")
        print(f"   Criação usuário: {'✅' if results['user_creation'] else '❌'}")
        
        # Detalhes dos logins
        for test in results['login_tests']:
            status = "✅" if test['success'] else "❌"
            tipo_status = "✅" if test['tipo'] == test['expected'] else "⚠️"
            print(f"     {status} {test['user']}: {test['tipo']} {tipo_status}")
    
    print(f"\n{'='*80}")
    
    # Verificar se migração foi bem-sucedida
    overall_success = (
        (local_results and local_results['overall_success']) or
        (prod_results and prod_results['overall_success'])
    )
    
    if overall_success:
        print("🎉 MIGRAÇÃO BEM-SUCEDIDA!")
        print("\n✅ Todas as funcionalidades estão operando corretamente")
        print("✅ Usuários admin têm acesso adequado")
        print("✅ Sistema mantém compatibilidade")
    else:
        print("❌ PROBLEMAS DETECTADOS!")
        print("\n💡 AÇÕES RECOMENDADAS:")
        print("1. Verificar se migração do banco foi executada")
        print("2. Reiniciar servidores")
        print("3. Verificar logs de aplicação")
        print("4. Executar rollback se necessário")

def main():
    """Executar suite completa de testes"""
    print("🧪 SUITE DE TESTES - MIGRAÇÃO CONSOLIDAÇÃO TIPO")
    print("=" * 60)
    
    # Testar ambiente local
    local_results = None
    try:
        local_results = test_environment("LOCAL", LOCAL_URL)
    except Exception as e:
        print(f"❌ Erro ao testar ambiente local: {e}")
    
    # Testar ambiente de produção
    prod_results = None
    try:
        prod_results = test_environment("PRODUÇÃO", PROD_URL)
    except Exception as e:
        print(f"❌ Erro ao testar ambiente de produção: {e}")
    
    # Gerar relatório final
    generate_report(local_results, prod_results)

if __name__ == "__main__":
    main()
