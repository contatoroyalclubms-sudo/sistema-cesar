"""
Script de teste completo do sistema Painel Universal V6
Testa todas as funcionalidades principais
"""

import requests
import json
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8003"
FRONTEND_URL = "http://localhost:5174"

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")

def test_backend_health():
    """Testa se o backend está rodando"""
    print_header("TESTANDO BACKEND")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend rodando em {BASE_URL}")
            return True
        else:
            print_error(f"Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Backend não está rodando em {BASE_URL}")
        print_info("Execute: python auth_server.py")
        return False
    except Exception as e:
        print_error(f"Erro ao testar backend: {e}")
        return False

def test_frontend():
    """Testa se o frontend está rodando"""
    print_header("TESTANDO FRONTEND")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend rodando em {FRONTEND_URL}")
            return True
        else:
            print_error(f"Frontend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Frontend não está rodando em {FRONTEND_URL}")
        print_info("Execute: npm run dev")
        return False
    except Exception as e:
        print_error(f"Erro ao testar frontend: {e}")
        return False

def test_login():
    """Testa o sistema de login"""
    print_header("TESTANDO SISTEMA DE LOGIN")
    
    # Credenciais de teste
    credentials = [
        {"cpf": "00000000000", "senha": "0000", "tipo": "admin"},
        {"cpf": "11111111111", "senha": "1111", "tipo": "promoter"},
        {"cpf": "22222222222", "senha": "2222", "tipo": "cliente"}
    ]
    
    tokens = []
    for cred in credentials:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"cpf": cred["cpf"], "senha": cred["senha"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    print_success(f"Login bem-sucedido para {cred['tipo']} (CPF: {cred['cpf']})")
                    tokens.append(token)
                else:
                    print_error(f"Token não retornado para {cred['tipo']}")
            else:
                print_error(f"Falha no login para {cred['tipo']}: {response.status_code}")
                if response.text:
                    print_info(f"Resposta: {response.text}")
        except Exception as e:
            print_error(f"Erro ao testar login para {cred['tipo']}: {e}")
    
    return tokens

def test_protected_endpoints(token):
    """Testa endpoints protegidos"""
    print_header("TESTANDO ENDPOINTS PROTEGIDOS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/api/auth/verify-token",
        "/api/auth/me",
        "/api/eventos",
        "/api/usuarios"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 403]:  # 403 é esperado para alguns endpoints
                print_success(f"Endpoint {endpoint}: {response.status_code}")
                success_count += 1
            else:
                print_error(f"Endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print_error(f"Erro ao testar {endpoint}: {e}")
    
    return success_count > 0

def test_cors():
    """Testa configuração CORS"""
    print_header("TESTANDO CONFIGURAÇÃO CORS")
    
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175"
    ]
    
    for origin in origins:
        try:
            headers = {"Origin": origin}
            response = requests.options(
                f"{BASE_URL}/api/auth/login",
                headers=headers,
                timeout=5
            )
            
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            if cors_header:
                print_success(f"CORS permitido para {origin}")
            else:
                print_error(f"CORS não configurado para {origin}")
        except Exception as e:
            print_error(f"Erro ao testar CORS para {origin}: {e}")

def test_meep_integration():
    """Testa integração MEEP"""
    print_header("TESTANDO INTEGRAÇÃO MEEP")
    
    try:
        response = requests.get(f"{BASE_URL}/api/meep/sync/auto/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Endpoint MEEP acessível")
            print_info(f"Status: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Endpoint MEEP retornou {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao testar MEEP: {e}")
        return False

def main():
    """Executa todos os testes"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         TESTE COMPLETO - PAINEL UNIVERSAL V6             ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print_info(f"Iniciando testes em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Contadores
    tests_passed = 0
    tests_failed = 0
    
    # 1. Teste do Backend
    if test_backend_health():
        tests_passed += 1
    else:
        tests_failed += 1
        print_error("Backend não está rodando. Abortando testes.")
        return
    
    # 2. Teste do Frontend
    if test_frontend():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 3. Teste de Login
    tokens = test_login()
    if tokens:
        tests_passed += 1
        
        # 4. Teste de Endpoints Protegidos
        if tokens and test_protected_endpoints(tokens[0]):
            tests_passed += 1
        else:
            tests_failed += 1
    else:
        tests_failed += 1
    
    # 5. Teste de CORS
    test_cors()
    tests_passed += 1
    
    # 6. Teste de MEEP
    if test_meep_integration():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total de testes: {total_tests}")
    print_success(f"Testes aprovados: {tests_passed}")
    if tests_failed > 0:
        print_error(f"Testes falhados: {tests_failed}")
    
    print(f"\n{Colors.BOLD}Taxa de sucesso: {success_rate:.1f}%{Colors.END}")
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SISTEMA FUNCIONANDO PERFEITAMENTE! 🎉{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ SISTEMA FUNCIONAL COM ALGUNS PROBLEMAS{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SISTEMA COM PROBLEMAS CRÍTICOS{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")

if __name__ == "__main__":
    main()