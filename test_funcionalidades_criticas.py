#!/usr/bin/env python3
"""
BATERIA COMPLETA DE TESTES - FUNCIONALIDADES CRÍTICAS
Testa todas as funcionalidades essenciais do sistema
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprimir seção formatada"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name, success, details=""):
    """Imprimir resultado do teste"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   💬 {details}")

def test_basic_endpoints():
    """Teste 1: Endpoints básicos"""
    print_section("TESTE 1: ENDPOINTS BÁSICOS")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 1.1: Root endpoint
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        success = response.status_code == 200 and "Painel Universal" in response.text
        print_test("Root endpoint (/)", success, f"Status: {response.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Root endpoint (/)", False, f"Erro: {e}")
    
    # Teste 1.2: Health check
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            details = f"Status: {data.get('status')}, Registros: {data.get('data', {}).get('total_registros', 0)}"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Health check (/health)", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Health check (/health)", False, f"Erro: {e}")
    
    # Teste 1.3: Documentação
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        success = response.status_code == 200
        print_test("Documentação (/docs)", success, f"Status: {response.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Documentação (/docs)", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def test_database_operations():
    """Teste 2: Operações de banco de dados"""
    print_section("TESTE 2: OPERAÇÕES DE BANCO DE DADOS")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 2.1: Listar usuários
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/usuarios", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            total_usuarios = data.get('total', 0)
            details = f"Total: {total_usuarios} usuários encontrados"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Listar usuários", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Listar usuários", False, f"Erro: {e}")
    
    # Teste 2.2: Listar produtos
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/produtos", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            total_produtos = data.get('total', 0)
            details = f"Total: {total_produtos} produtos encontrados"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Listar produtos", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Listar produtos", False, f"Erro: {e}")
    
    # Teste 2.3: Listar empresas
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/empresas", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            total_empresas = data.get('total', 0)
            details = f"Total: {total_empresas} empresas encontradas"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Listar empresas", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Listar empresas", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def test_data_integrity():
    """Teste 3: Integridade dos dados"""
    print_section("TESTE 3: INTEGRIDADE DOS DADOS")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 3.1: Verificar usuário específico
    total_tests += 1
    try:
        # Primeiro, obter lista de usuários para pegar um ID válido
        users_response = requests.get(f"{BASE_URL}/api/usuarios?limit=1", timeout=10)
        if users_response.status_code == 200:
            users_data = users_response.json()
            if users_data.get('usuarios'):
                user_id = users_data['usuarios'][0]['id']
                
                # Agora testar o endpoint específico
                response = requests.get(f"{BASE_URL}/api/usuarios/{user_id}", timeout=10)
                success = response.status_code == 200
                if success:
                    data = response.json()
                    details = f"Usuário ID {user_id}: {data.get('nome')} ({data.get('email')})"
                else:
                    details = f"Status HTTP: {response.status_code}"
                print_test("Obter usuário específico", success, details)
                if success:
                    tests_passed += 1
            else:
                print_test("Obter usuário específico", False, "Nenhum usuário encontrado para testar")
        else:
            print_test("Obter usuário específico", False, "Falha ao obter lista de usuários")
    except Exception as e:
        print_test("Obter usuário específico", False, f"Erro: {e}")
    
    # Teste 3.2: Filtros de produtos
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/produtos?tipo_usuario=cliente", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            total_filtrado = data.get('total', 0)
            details = f"Produtos para cliente: {total_filtrado}"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Filtro de produtos por tipo", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Filtro de produtos por tipo", False, f"Erro: {e}")
    
    # Teste 3.3: Paginação
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/usuarios?skip=0&limit=2", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            usuarios_retornados = len(data.get('usuarios', []))
            details = f"Paginação funcionando: {usuarios_retornados} usuários retornados"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Paginação de resultados", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Paginação de resultados", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def test_dashboard_functionality():
    """Teste 4: Funcionalidades do dashboard"""
    print_section("TESTE 4: FUNCIONALIDADES DO DASHBOARD")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 4.1: Estatísticas do dashboard
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            stats = data.get('estatisticas', {})
            usuarios_total = stats.get('usuarios', {}).get('total', 0)
            empresas_total = stats.get('empresas', {}).get('total', 0)
            produtos_total = stats.get('produtos', {}).get('total', 0)
            details = f"Usuários: {usuarios_total}, Empresas: {empresas_total}, Produtos: {produtos_total}"
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Estatísticas do dashboard", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Estatísticas do dashboard", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def test_integration():
    """Teste 5: Teste de integração completo"""
    print_section("TESTE 5: INTEGRAÇÃO COMPLETA")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 5.1: Teste de integração do sistema
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/test/integration", timeout=15)
        success = response.status_code == 200
        if success:
            data = response.json()
            all_passed = data.get('all_tests_passed', False)
            results = data.get('results', {})
            details = f"Todos os testes: {'✅' if all_passed else '❌'}"
            
            # Mostrar detalhes dos subtestes
            for test_name, result in results.items():
                if test_name != 'errors':
                    status = "✅" if result else "❌"
                    print(f"      {status} {test_name.replace('_', ' ').title()}")
            
            if results.get('errors'):
                print("      ⚠️ Erros encontrados:")
                for error in results['errors']:
                    print(f"         - {error}")
                    
        else:
            details = f"Status HTTP: {response.status_code}"
        print_test("Teste de integração completo", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Teste de integração completo", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def test_performance():
    """Teste 6: Performance básica"""
    print_section("TESTE 6: PERFORMANCE BÁSICA")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 6.1: Tempo de resposta
    total_tests += 1
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # em ms
        success = response.status_code == 200 and response_time < 2000  # menos de 2 segundos
        
        details = f"Tempo de resposta: {response_time:.2f}ms"
        print_test("Tempo de resposta aceitável", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Tempo de resposta aceitável", False, f"Erro: {e}")
    
    # Teste 6.2: Múltiplas requisições
    total_tests += 1
    try:
        start_time = time.time()
        responses = []
        
        for i in range(5):
            response = requests.get(f"{BASE_URL}/api/usuarios?limit=10", timeout=10)
            responses.append(response.status_code == 200)
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        
        success = all(responses) and total_time < 5000  # todas bem-sucedidas em menos de 5s
        details = f"5 requisições em {total_time:.2f}ms"
        print_test("Múltiplas requisições", success, details)
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Múltiplas requisições", False, f"Erro: {e}")
    
    return tests_passed, total_tests

def run_all_tests():
    """Executar todos os testes"""
    print(f"🚀 INICIANDO BATERIA COMPLETA DE TESTES")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 URL Base: {BASE_URL}")
    
    # Aguardar servidor inicializar
    print(f"\n⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    total_passed = 0
    total_tests = 0
    
    # Executar todos os grupos de teste
    test_groups = [
        ("Endpoints Básicos", test_basic_endpoints),
        ("Operações de Banco", test_database_operations),
        ("Integridade dos Dados", test_data_integrity),
        ("Dashboard", test_dashboard_functionality),
        ("Integração", test_integration),
        ("Performance", test_performance)
    ]
    
    results = {}
    
    for group_name, test_func in test_groups:
        try:
            passed, total = test_func()
            total_passed += passed
            total_tests += total
            results[group_name] = {"passed": passed, "total": total}
        except Exception as e:
            print(f"❌ Erro no grupo {group_name}: {e}")
            results[group_name] = {"passed": 0, "total": 1, "error": str(e)}
            total_tests += 1
    
    # Relatório final
    print_section("RELATÓRIO FINAL DOS TESTES")
    
    print(f"📊 RESUMO GERAL:")
    print(f"   ✅ Testes aprovados: {total_passed}")
    print(f"   📝 Total de testes: {total_tests}")
    print(f"   📈 Taxa de sucesso: {(total_passed/total_tests*100):.1f}%")
    
    print(f"\n📋 DETALHES POR GRUPO:")
    for group_name, result in results.items():
        passed = result["passed"]
        total = result["total"]
        percentage = (passed/total*100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
        print(f"   {status} {group_name}: {passed}/{total} ({percentage:.1f}%)")
        
        if "error" in result:
            print(f"      💥 Erro: {result['error']}")
    
    # Veredito final
    success_rate = (total_passed/total_tests*100) if total_tests > 0 else 0
    
    if success_rate >= 90:
        print(f"\n🎉 RESULTADO: SISTEMA APROVADO!")
        print(f"✅ O sistema está funcionando corretamente!")
    elif success_rate >= 70:
        print(f"\n⚠️ RESULTADO: SISTEMA PARCIALMENTE FUNCIONAL")
        print(f"⚠️ Algumas funcionalidades precisam de atenção.")
    else:
        print(f"\n❌ RESULTADO: SISTEMA COM PROBLEMAS")
        print(f"❌ Várias funcionalidades não estão funcionando.")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Testes interrompidos pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro fatal nos testes: {e}")
        exit(1)
