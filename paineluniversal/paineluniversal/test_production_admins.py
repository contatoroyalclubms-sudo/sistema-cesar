#!/usr/bin/env python3
"""
Script para testar e validar se o problema foi resolvido
Testa login com usuários que deveriam ser admin
"""

import requests
import json

def test_production_login():
    """Testar login dos usuários admin na produção"""
    
    url = 'https://backend-painel-universal-production.up.railway.app/api/auth/login'
    
    # Usuários para testar (baseado na tabela fornecida)
    usuarios_teste = [
        {'cpf': '06601206156', 'senha': '101112', 'nome': 'César', 'esperado': 'admin'},
        {'cpf': '06601206155', 'senha': 'admin123', 'nome': 'Admin', 'esperado': 'admin'},
        {'cpf': '11111111111', 'senha': 'admin123', 'nome': 'Admin Teste Lower', 'esperado': 'admin'},
        {'cpf': '33333333333', 'senha': 'admin123', 'nome': 'Teste Final Admin', 'esperado': 'admin'},
    ]
    
    print("🔑 TESTE DE LOGIN DE USUÁRIOS ADMIN NA PRODUÇÃO")
    print("=" * 60)
    
    for i, user_data in enumerate(usuarios_teste, 1):
        print(f"\n{i}. Testando {user_data['nome']} (CPF: {user_data['cpf'][:3]}***{user_data['cpf'][-3:]})...")
        
        try:
            response = requests.post(url, json={
                'cpf': user_data['cpf'], 
                'senha': user_data['senha']
            }, timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'usuario' in result:
                    usuario = result['usuario']
                    tipo_atual = usuario.get('tipo') or usuario.get('tipo_usuario')
                    
                    print(f"   ✅ Login OK - ID: {usuario.get('id')}")
                    print(f"   📋 Tipo atual: '{tipo_atual}'")
                    print(f"   📋 Tipo esperado: '{user_data['esperado']}'")
                    
                    if tipo_atual == user_data['esperado']:
                        print(f"   🎉 CORRETO: Tipo está como esperado!")
                    else:
                        print(f"   ⚠️ PROBLEMA: Tipo deveria ser '{user_data['esperado']}' mas é '{tipo_atual}'")
                else:
                    print(f"   ❌ Campo 'usuario' não encontrado na resposta")
            elif response.status_code == 401:
                print(f"   ❌ Credenciais incorretas")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}")
    
    print(f"\n{'='*60}")
    print("💡 PRÓXIMOS PASSOS:")
    print("   Se algum usuário não está como 'admin':")
    print("   1. Verificar se a migração do banco foi aplicada")
    print("   2. Atualizar campo 'tipo_usuario' para ser igual ao campo 'tipo'")
    print("   3. Reiniciar o servidor de produção")

if __name__ == "__main__":
    test_production_login()
