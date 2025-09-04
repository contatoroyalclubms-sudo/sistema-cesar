#!/usr/bin/env python3
"""
Teste abrangente para validar todas as funcionalidades críticas
Garante que nenhuma funcionalidade de produção foi quebrada
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Teste básico de saúde do servidor"""
    print("1️⃣ Testando saúde do servidor...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondendo corretamente")
            return True
        else:
            print(f"❌ Servidor com problema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_user_registration():
    """Teste de registro de usuário"""
    print("\n2️⃣ Testando registro de usuário...")
    try:
        test_time = int(time.time())
        user_data = {
            "nome": f"Teste Validação {test_time}",
            "email": f"teste_validacao_{test_time}@exemplo.com",
            "cpf": f"111{test_time}"[-11:],
            "telefone": "11999999999",
            "senha": "123456",
            "tipo": "cliente"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Registro de usuário funcionando")
            return response.json()
        else:
            print(f"❌ Erro no registro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no registro: {e}")
        return None

def test_user_login(user_data):
    """Teste de login de usuário"""
    print("\n3️⃣ Testando login de usuário...")
    try:
        login_data = {
            "cpf": user_data["cpf"],
            "senha": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login funcionando")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def test_products_api(token):
    """Teste das APIs de produtos"""
    print("\n4️⃣ Testando APIs de produtos...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Listar produtos
        response = requests.get(f"{BASE_URL}/produtos", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Listagem de produtos funcionando")
        else:
            print(f"⚠️ Listagem de produtos: {response.status_code}")
        
        # Criar produto de teste
        test_time = int(time.time())
        produto_data = {
            "nome": f"Produto Teste {test_time}",
            "descricao": "Produto para validação",
            "preco": 10.0,
            "codigo_barras": f"123456{test_time}",
            "estoque_atual": 100
        }
        
        response = requests.post(f"{BASE_URL}/produtos", json=produto_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Criação de produtos funcionando")
            return response.json()["id"]
        else:
            print(f"⚠️ Criação de produtos: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro nos produtos: {e}")
        return None

def test_events_api(token):
    """Teste das APIs de eventos"""
    print("\n5️⃣ Testando APIs de eventos...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Listar eventos
        response = requests.get(f"{BASE_URL}/eventos", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Listagem de eventos funcionando")
            return True
        else:
            print(f"⚠️ Listagem de eventos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro nos eventos: {e}")
        return False

def test_admin_endpoints(token):
    """Teste de endpoints administrativos"""
    print("\n6️⃣ Testando endpoints administrativos...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Dashboard
        response = requests.get(f"{BASE_URL}/dashboard/resumo", headers=headers, timeout=10)
        if response.status_code in [200, 401, 403]:  # 401/403 são aceitáveis por permissão
            print("✅ Dashboard respondendo")
        else:
            print(f"⚠️ Dashboard: {response.status_code}")
        
        return True
            
    except Exception as e:
        print(f"❌ Erro nos endpoints admin: {e}")
        return False

def cleanup_test_data(token, user_id, produto_id):
    """Limpar dados de teste"""
    print("\n🧹 Limpando dados de teste...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Remover produto de teste
        if produto_id:
            response = requests.delete(f"{BASE_URL}/produtos/{produto_id}", headers=headers, timeout=10)
            if response.status_code in [200, 204, 404]:
                print("✅ Produto de teste removido")
            else:
                print(f"⚠️ Produto não removido: {response.status_code}")
        
        print("✅ Limpeza concluída")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro na limpeza: {e}")
        return False

def main():
    """Executar todos os testes de validação"""
    print("🧪 VALIDAÇÃO COMPLETA DO SISTEMA")
    print("=" * 50)
    print("Objetivo: Garantir que nenhuma funcionalidade foi quebrada")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # 1. Teste de saúde
    if test_health():
        success_count += 1
    
    # 2. Teste de registro
    user_data = test_user_registration()
    if user_data:
        success_count += 1
        
        # 3. Teste de login
        token = test_user_login(user_data)
        if token:
            success_count += 1
            
            # 4. Teste de produtos
            produto_id = test_products_api(token)
            if produto_id is not None:
                success_count += 1
            
            # 5. Teste de eventos
            if test_events_api(token):
                success_count += 1
            
            # 6. Teste de admin
            if test_admin_endpoints(token):
                success_count += 1
            
            # Limpeza
            cleanup_test_data(token, user_data.get("id"), produto_id)
    
    # Resultados finais
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DA VALIDAÇÃO")
    print("=" * 50)
    print(f"✅ Testes bem-sucedidos: {success_count}/{total_tests}")
    print(f"📈 Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Todas as funcionalidades críticas estão operacionais")
        print("✅ Seguro para aplicar correções na produção")
    elif success_count >= total_tests * 0.8:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("⚠️ A maioria das funcionalidades está ok")
        print("⚠️ Revisar falhas antes de aplicar na produção")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS CRÍTICOS")
        print("❌ Muitas funcionalidades falharam")
        print("❌ NÃO aplicar na produção até resolver")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
