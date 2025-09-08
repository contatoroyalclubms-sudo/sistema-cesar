# Script para criar usuário de teste e validar autenticação
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.models import Usuario, TipoUsuario, Empresa
    from app.database import get_db, SessionLocal
    from app.auth import gerar_hash_senha
    from sqlalchemy.orm import Session
    print("✅ Imports do backend bem-sucedidos")
except ImportError as e:
    print(f"❌ Erro ao importar do backend: {e}")
    print("Continuando apenas com testes de API...")

import requests
import json
from datetime import datetime

def create_test_user():
    """Criar usuário de teste se necessário"""
    try:
        db = SessionLocal()
        
        # Verificar se usuário teste já existe
        test_user = db.query(Usuario).filter(Usuario.cpf == "11111111111").first()
        if test_user:
            print("✅ Usuário de teste já existe")
            return True
            
        # Criar usuário de teste
        hashed_password = gerar_hash_senha("admin123")
        
        new_user = Usuario(
            cpf="11111111111",
            nome="Admin Teste",
            email="admin@teste.com",
            senha=hashed_password,
            tipo=TipoUsuario.ADMIN,
            ativo=True,
            verificado=True
        )
        
        db.add(new_user)
        db.commit()
        print("✅ Usuário de teste criado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_complete_flow():
    """Testar fluxo completo de autenticação e APIs"""
    
    base_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("🔍 Testando fluxo completo...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://frontend-painel-universal-production.up.railway.app",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # FASE 1: Login
    print("\n🔐 FASE 1: FAZENDO LOGIN")
    print("-" * 50)
    
    login_data = {
        "cpf": "06601206156",  # CPF fornecido pelo usuário
        "senha": "101112"      # Senha fornecida pelo usuário
    }
    
    try:
        print(f"   Fazendo login com CPF: {login_data['cpf'][:3]}***")
        response = requests.post(
            f"{base_url}/api/auth/login",
            headers=headers,
            json=login_data,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            usuario = data.get("usuario")
            
            if token:
                print(f"   ✅ Login bem-sucedido!")
                print(f"   👤 Usuário: {usuario.get('nome') if usuario else 'N/A'}")
                print(f"   🔑 Token: {token[:20]}...")
            else:
                print(f"   ❌ Login falhou - sem token na resposta")
                return False
                
        elif response.status_code == 401:
            print("   ❌ Credenciais inválidas")
            print("   💡 Verifique se o usuário de teste foi criado")
            return False
        else:
            print(f"   ❌ Erro inesperado: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Detalhes: {error_data}")
            except:
                print(f"   📋 Texto: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {str(e)}")
        return False
    
    # FASE 2: Testar APIs específicas do frontend
    print("\n📡 FASE 2: TESTANDO APIs DO FRONTEND")
    print("-" * 50)
    
    auth_headers = headers.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    # Endpoints que o frontend chama (baseado no grep)
    frontend_endpoints = [
        ("GET", "/api/auth/me", "Dados do usuário atual"),
        ("GET", "/api/dashboard/resumo", "Resumo do dashboard"),
        ("GET", "/api/eventos/", "Lista de eventos"),
        ("GET", "/api/produtos/", "Lista de produtos"),
        ("GET", "/api/dashboard/avancado", "Dashboard avançado"),
        ("GET", "/api/produtos/categorias/", "Categorias de produtos"),
    ]
    
    results = {}
    
    for method, endpoint, description in frontend_endpoints:
        print(f"\n   🔍 {method} {endpoint}")
        print(f"       {description}")
        
        try:
            url = f"{base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=auth_headers, timeout=30)
            else:
                response = requests.post(url, headers=auth_headers, json={}, timeout=30)
            
            status = response.status_code
            results[endpoint] = {
                "status": status,
                "success": status == 200,
                "size": len(response.content)
            }
            
            print(f"       Status: {status} ", end="")
            
            if status == 200:
                print("✅ OK")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"         📊 Lista com {len(data)} itens")
                    elif isinstance(data, dict):
                        print(f"         📊 Objeto com {len(data)} campos")
                    else:
                        print(f"         📊 Dados: {str(data)[:50]}...")
                except:
                    print(f"         📝 Texto: {len(response.text)} chars")
                    
            elif status == 403:
                print("❌ Forbidden (problema de permissão)")
            elif status == 404:
                print("❌ Not Found (endpoint não existe)")
            elif status == 405:
                print("❌ Method Not Allowed (método HTTP incorreto)")
            elif status == 500:
                print("❌ Internal Server Error")
                try:
                    error_data = response.json()
                    print(f"         🚨 Erro: {error_data}")
                except:
                    print(f"         🚨 Erro: {response.text[:100]}")
            else:
                print(f"⚠️ Status inesperado")
                
        except requests.exceptions.Timeout:
            print("       ⏱️ Timeout")
            results[endpoint] = {"status": 0, "success": False, "error": "timeout"}
        except Exception as e:
            print(f"       ❌ Erro: {str(e)}")
            results[endpoint] = {"status": 0, "success": False, "error": str(e)}
    
    # FASE 3: Análise e diagnóstico
    print("\n" + "=" * 80)
    print("📊 ANÁLISE DOS RESULTADOS")
    print("=" * 80)
    
    working_endpoints = [k for k, v in results.items() if v["success"]]
    failing_endpoints = [k for k, v in results.items() if not v["success"]]
    
    print(f"\n✅ Endpoints funcionando: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"   • {endpoint}")
    
    print(f"\n❌ Endpoints com problema: {len(failing_endpoints)}")
    for endpoint in failing_endpoints:
        status = results[endpoint]["status"]
        error = results[endpoint].get("error", "")
        print(f"   • {endpoint}: {status} {error}")
    
    # Diagnóstico específico
    print(f"\n🔧 DIAGNÓSTICO ESPECÍFICO")
    print("-" * 50)
    
    if "/api/auth/me" in results:
        if results["/api/auth/me"]["success"]:
            print("✅ Autenticação funcionando - token válido")
        else:
            print("❌ PROBLEMA CRÍTICO: Token inválido ou expirado")
            print("   💡 O problema está na autenticação do frontend")
    
    if "/api/dashboard/resumo" in results:
        if results["/api/dashboard/resumo"]["success"]:
            print("✅ Dashboard funcionando")
        else:
            status = results["/api/dashboard/resumo"]["status"]
            if status == 403:
                print("❌ Dashboard bloqueado por permissão")
            elif status == 500:
                print("❌ Dashboard com erro interno")
            else:
                print(f"❌ Dashboard com erro {status}")
    
    eventos_status = results.get("/api/eventos/", {}).get("status", 0)
    produtos_status = results.get("/api/produtos/", {}).get("status", 0)
    
    if eventos_status == 200 and produtos_status == 200:
        print("✅ APIs principais funcionando")
    elif eventos_status != 200:
        print(f"❌ API de eventos com problema: {eventos_status}")
    elif produtos_status != 200:
        print(f"❌ API de produtos com problema: {produtos_status}")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES")
    print("-" * 50)
    
    success_rate = len(working_endpoints) / len(results) * 100
    
    if success_rate >= 80:
        print("🎉 Sistema funcionando bem!")
        print("   O problema pode estar no frontend (AuthContext ou ProtectedRoute)")
    elif success_rate >= 50:
        print("⚠️ Sistema parcialmente funcional")
        print("   Alguns endpoints precisam de correção")
    else:
        print("🚨 Sistema com muitos problemas")
        print("   Necessário revisão ampla do backend")
    
    if "/api/auth/me" not in working_endpoints:
        print("\n🔑 AÇÃO NECESSÁRIA: Corrigir autenticação")
        print("   1. Verificar se AuthContext está enviando token")
        print("   2. Verificar se token não está expirando")
        print("   3. Verificar configuração de CORS")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Testar login no frontend com essas credenciais")
    print("2. Verificar logs do navegador para erros específicos")
    print("3. Verificar se ProtectedRoute está bloqueando corretamente")
    
    return success_rate >= 50

if __name__ == "__main__":
    print("🚀 Iniciando teste completo do sistema...")
    
    # Tentar criar usuário de teste
    print("\n📝 Criando usuário de teste...")
    create_test_user()
    
    # Testar fluxo completo
    success = test_complete_flow()
    
    if success:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("💡 Use as credenciais CPF: 11111111111, Senha: admin123 para testar o frontend")
    else:
        print("\n❌ TESTE FALHOU!")
        print("🔧 Necessário corrigir os problemas identificados")
