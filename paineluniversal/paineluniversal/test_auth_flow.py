import requests
import json
import sys
from datetime import datetime

def test_authentication_flow():
    """
    Testa o fluxo completo de autenticação e acesso às APIs
    """
    
    base_url = "https://backend-painel-universal-production.up.railway.app"
    
    print("🔐 Testando fluxo de autenticação completo...")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Headers padrão
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://frontend-painel-universal-production.up.railway.app",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Teste 1: Verificar endpoints públicos
    print("\n📋 FASE 1: Testando endpoints públicos")
    print("-" * 50)
    
    public_endpoints = [
        ("GET", "/"),
        ("GET", "/docs"),
        ("POST", "/api/auth/login"),
        ("POST", "/api/auth/register")
    ]
    
    for method, endpoint in public_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                # Para POST, vamos testar se aceita o método (esperar 400/422, não 405)
                response = requests.post(url, headers=headers, json={}, timeout=10)
            
            status = response.status_code
            print(f"   {method} {endpoint}: {status} ", end="")
            
            if status == 200:
                print("✅ OK")
            elif status == 400 or status == 422:
                print("✅ Aceita requisição (erro de dados esperado)")
            elif status == 405:
                print("❌ Método não permitido")
            elif status == 404:
                print("❓ Não encontrado")
            else:
                print(f"⚠️ Status: {status}")
                
        except Exception as e:
            print(f"   {method} {endpoint}: ❌ Error: {str(e)}")
    
    # Teste 2: Tentar fazer login com dados de teste
    print("\n🔐 FASE 2: Testando login")
    print("-" * 50)
    
    # Dados de teste (vou tentar alguns usuários comuns)
    test_credentials = [
        {"cpf": "11111111111", "senha": "admin123"},
        {"cpf": "12345678901", "senha": "123456"},
        {"cpf": "admin", "senha": "admin"},
        {"cpf": "test@test.com", "senha": "test123"}
    ]
    
    token = None
    for creds in test_credentials:
        print(f"   Tentando login com CPF: {creds['cpf'][:3]}***")
        
        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                headers=headers,
                json=creds,
                timeout=10
            )
            
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == 200:
                data = response.json()
                if "access_token" in data:
                    token = data["access_token"]
                    print(f"   ✅ Login bem-sucedido! Token obtido.")
                    print(f"   👤 Usuário: {data.get('usuario', {}).get('nome', 'N/A')}")
                    break
            elif status == 401:
                print("   ❌ Credenciais inválidas")
            elif status == 202:
                print("   📱 Precisa de verificação 2FA")
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Erro: {error_data}")
                except:
                    print(f"   ❌ Erro {status}: {response.text[:100]}")
                    
        except Exception as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
    
    # Teste 3: Testar APIs protegidas (com e sem token)
    print("\n🔒 FASE 3: Testando APIs protegidas")
    print("-" * 50)
    
    protected_endpoints = [
        ("GET", "/api/auth/me"),
        ("GET", "/api/dashboard/resumo"),
        ("GET", "/api/eventos"),
        ("POST", "/api/eventos"),
        ("GET", "/api/produtos"),
        ("POST", "/api/produtos"),
        ("GET", "/api/pdv"),
        ("POST", "/api/pdv")
    ]
    
    for method, endpoint in protected_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n   🔍 Testando {method} {endpoint}")
        
        # Teste sem token
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, json={}, timeout=10)
            
            status_no_token = response.status_code
            print(f"      Sem token: {status_no_token} ", end="")
            
            if status_no_token == 401 or status_no_token == 403:
                print("✅ Protegido corretamente")
            elif status_no_token == 405:
                print("❌ Método não permitido")
            else:
                print(f"⚠️ Inesperado")
                
        except Exception as e:
            print(f"      Sem token: ❌ {str(e)}")
        
        # Teste com token (se temos)
        if token:
            try:
                auth_headers = headers.copy()
                auth_headers["Authorization"] = f"Bearer {token}"
                
                if method == "GET":
                    response = requests.get(url, headers=auth_headers, timeout=10)
                else:
                    response = requests.post(url, headers=auth_headers, json={}, timeout=10)
                
                status_with_token = response.status_code
                print(f"      Com token: {status_with_token} ", end="")
                
                if status_with_token == 200:
                    print("✅ OK")
                    try:
                        data = response.json()
                        print(f"         📊 Dados retornados: {len(str(data))} chars")
                    except:
                        print(f"         📝 Resposta texto: {len(response.text)} chars")
                elif status_with_token == 400 or status_with_token == 422:
                    print("⚠️ Erro de dados (endpoint funciona)")
                elif status_with_token == 405:
                    print("❌ Método não permitido")
                elif status_with_token == 500:
                    print("❌ Erro interno do servidor")
                    try:
                        error_data = response.json()
                        print(f"         🚨 Erro: {error_data}")
                    except:
                        print(f"         🚨 Erro: {response.text[:200]}")
                else:
                    print(f"⚠️ Status {status_with_token}")
                    
            except Exception as e:
                print(f"      Com token: ❌ {str(e)}")
        else:
            print("      Com token: ❓ Sem token disponível")
    
    # Resumo e recomendações
    print("\n" + "=" * 80)
    print("📊 RESUMO E DIAGNÓSTICO")
    print("=" * 80)
    
    if token:
        print("✅ Autenticação funcionando - token obtido com sucesso")
        print("💡 Recomendação: Verificar se o frontend está enviando tokens corretamente")
    else:
        print("❌ Autenticação falhando - não foi possível obter token")
        print("💡 Recomendação: Verificar credenciais e endpoint de login")
    
    print("\n🔧 Próximos passos:")
    print("1. Verificar configuração de CORS no backend")
    print("2. Verificar se axios interceptors estão funcionando no frontend")
    print("3. Verificar logs detalhados do AuthContext")
    print("4. Testar com credenciais reais de produção")

if __name__ == "__main__":
    test_authentication_flow()
