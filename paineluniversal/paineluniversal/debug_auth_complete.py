#!/usr/bin/env python3
"""
🔍 DEBUG COMPLETO: Sistema de Autenticação
Testa todos os aspectos da autenticação para identificar problemas do painel lateral
"""

import requests
import json
from datetime import datetime

def test_production_auth():
    """Testar autenticação em produção para identificar problemas"""
    print("🔍 ANÁLISE COMPLETA DO SISTEMA DE AUTENTICAÇÃO")
    print("=" * 60)
    
    backend_url = "https://backend-painel-universal-production.up.railway.app"
    
    # Tentar diferentes credenciais de usuários que podem existir
    test_users = [
        {"cpf": "00000000000", "senha": "admin123", "tipo_esperado": "admin"},
        {"cpf": "11111111111", "senha": "promoter123", "tipo_esperado": "promoter"},
        {"cpf": "12345678901", "senha": "123456", "tipo_esperado": "cliente"},
        # Credenciais que podem estar em produção baseado nos logs
        {"cpf": "06601206156", "senha": "123456", "tipo_esperado": "admin"},
    ]
    
    successful_login = None
    
    for user_data in test_users:
        print(f"\n🔐 Testando usuário: {user_data['cpf'][:3]}***{user_data['cpf'][-3:]}")
        
        try:
            # 1. Tentar login
            login_response = requests.post(
                f"{backend_url}/api/auth/login",
                json={
                    "cpf": user_data["cpf"],
                    "senha": user_data["senha"]
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("access_token")
                usuario = login_data.get("usuario", {})
                
                print(f"✅ Login bem-sucedido!")
                print(f"🎫 Token: {token[:20] if token else 'N/A'}...")
                print(f"👤 Dados do usuário do login:")
                print(f"   ID: {usuario.get('id')}")
                print(f"   Nome: {usuario.get('nome')}")
                print(f"   Email: {usuario.get('email')}")
                print(f"   Tipo: {usuario.get('tipo')}")
                print(f"   Tipo_usuario: {usuario.get('tipo_usuario')}")
                print(f"   Ativo: {usuario.get('ativo')}")
                
                if token:
                    # 2. Testar endpoint /me
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get(
                        f"{backend_url}/api/auth/me",
                        headers=headers,
                        timeout=10
                    )
                    
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        print(f"\n📊 Dados do /api/auth/me:")
                        print(f"   ID: {me_data.get('id')}")
                        print(f"   Nome: {me_data.get('nome')}")
                        print(f"   Email: {me_data.get('email')}")
                        print(f"   Tipo: {me_data.get('tipo')}")
                        print(f"   Tipo_usuario: {me_data.get('tipo_usuario')}")
                        print(f"   Ativo: {me_data.get('ativo')}")
                        
                        # 3. Análise de compatibilidade
                        print(f"\n🔍 ANÁLISE DE COMPATIBILIDADE:")
                        has_tipo = bool(me_data.get('tipo'))
                        has_tipo_usuario = bool(me_data.get('tipo_usuario'))
                        
                        print(f"   ✅ Campo 'tipo': {'✓' if has_tipo else '✗'} ({me_data.get('tipo', 'ausente')})")
                        print(f"   ✅ Campo 'tipo_usuario': {'✓' if has_tipo_usuario else '✗'} ({me_data.get('tipo_usuario', 'ausente')})")
                        
                        if has_tipo and has_tipo_usuario:
                            if me_data.get('tipo') == me_data.get('tipo_usuario'):
                                print(f"   ✅ Compatibilidade: CORRETA - ambos têm o mesmo valor")
                            else:
                                print(f"   ⚠️ Compatibilidade: INCONSISTENTE - valores diferentes")
                        elif has_tipo_usuario and not has_tipo:
                            print(f"   ⚠️ Compatibilidade: PROBLEMA - só tem tipo_usuario, falta tipo")
                        elif has_tipo and not has_tipo_usuario:
                            print(f"   ✅ Compatibilidade: OK - tem tipo (suficiente para frontend)")
                        else:
                            print(f"   ❌ Compatibilidade: CRÍTICO - nenhum campo de tipo disponível")
                        
                        successful_login = {
                            "user_data": user_data,
                            "login_data": login_data,
                            "me_data": me_data,
                            "token": token
                        }
                        break
                    else:
                        print(f"❌ Erro no /me: {me_response.status_code}")
                        print(f"📝 Resposta: {me_response.text[:200]}")
                else:
                    print("❌ Token não encontrado na resposta")
            else:
                print(f"❌ Login falhou: {login_response.status_code}")
                if login_response.text:
                    error_detail = login_response.text[:200]
                    print(f"📝 Erro: {error_detail}")
                    
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
    
    if successful_login:
        print(f"\n🎯 ANÁLISE DO PAINEL LATERAL:")
        me_data = successful_login["me_data"]
        
        # Simular lógica do Layout.tsx
        user_type = None
        if me_data.get('tipo'):
            user_type = me_data.get('tipo')
            print(f"   ✅ Tipo detectado via campo 'tipo': {user_type}")
        elif me_data.get('tipo_usuario'):
            user_type = me_data.get('tipo_usuario')
            print(f"   ✅ Tipo detectado via campo 'tipo_usuario': {user_type}")
        elif me_data.get('email', '').find('admin') != -1:
            user_type = 'admin'
            print(f"   ⚠️ Tipo detectado via fallback email: {user_type}")
        else:
            user_type = 'promoter'
            print(f"   ⚠️ Tipo detectado via fallback padrão: {user_type}")
        
        print(f"\n📋 MENU ITEMS QUE SERIAM EXIBIDOS:")
        
        # Simular filtros do painel lateral baseado no tipo
        menu_items = {
            'admin': ['Dashboard', 'Eventos', 'Vendas', 'Check-in', 'PDV', 'Produtos', 'Usuários', 'Relatórios', 'Configurações'],
            'promoter': ['Dashboard', 'Eventos', 'Vendas', 'Check-in', 'Listas & Convidados', 'Relatórios'],
            'cliente': ['Dashboard', 'Eventos', 'Check-in'],
            'operador': ['Dashboard', 'PDV', 'Produtos', 'Estoque']
        }
        
        available_items = menu_items.get(user_type, menu_items['promoter'])
        for item in available_items:
            print(f"   • {item}")
        
        return True
    else:
        print(f"\n❌ NENHUM LOGIN BEM-SUCEDIDO")
        print(f"   Não foi possível analisar o sistema de autenticação")
        return False

def analyze_frontend_storage():
    """Analisar dados armazenados no frontend (simulação)"""
    print(f"\n📱 ANÁLISE DO FRONTEND:")
    print(f"   Para debug completo, abra o Console do Navegador (F12) e execute:")
    print(f"   console.log('Token:', localStorage.getItem('token'))")
    print(f"   console.log('Usuario:', JSON.parse(localStorage.getItem('usuario') || '{{}}'))")
    print(f"   console.log('AuthContext state:', window.__auth_debug__)")

if __name__ == "__main__":
    success = test_production_auth()
    analyze_frontend_storage()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ ANÁLISE CONCLUÍDA - Dados coletados para debug")
        print("🔍 Verifique os logs acima para identificar problemas de compatibilidade")
    else:
        print("❌ ANÁLISE INCONCLUSIVA - Nenhum login funcionou")
        print("🔧 Pode ser necessário verificar credenciais ou configuração do backend")
    print(f"{'='*60}")
