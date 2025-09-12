#!/usr/bin/env python
"""
Teste da API MEEP Integration
"""

import requests
import json
import time

def print_section(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_meep_api():
    print_section("TESTE DA API MEEP INTEGRATION")
    
    # Base URLs
    AUTH_URL = "http://localhost:8003"
    MEEP_URL = "http://localhost:8004"
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Teste 1: Verificar Auth Server
    print("\n[1] Testando Auth Server...")
    try:
        response = requests.get(f"{AUTH_URL}/api/health")
        if response.status_code == 200:
            print(f"   [OK] Auth Server online: {response.json()}")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Auth Server retornou status {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha ao conectar com Auth Server: {str(e)}")
        results["failed"] += 1
    
    # Teste 2: Login
    print("\n[2] Fazendo login...")
    token = None
    try:
        login_data = {
            "cpf": "00000000000",
            "senha": "0000"
        }
        response = requests.post(f"{AUTH_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"   [OK] Login realizado com sucesso")
            print(f"   Token: {token[:20]}...")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Login falhou: {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha no login: {str(e)}")
        results["failed"] += 1
    
    # Teste 3: MEEP Status
    print("\n[3] Testando MEEP Server Status...")
    try:
        response = requests.get(f"{MEEP_URL}/api/meep/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] MEEP Server: {data['status']}")
            print(f"   Versão: {data['version']}")
            print(f"   Features: {', '.join(data['features'])}")
            results["passed"] += 1
        else:
            print(f"   [ERRO] MEEP Server retornou status {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha ao conectar com MEEP Server: {str(e)}")
        results["failed"] += 1
    
    # Teste 4: Criar Integração MEEP
    print("\n[4] Criando integração MEEP...")
    try:
        params = {
            "evento_id": 1,
            "meep_event_id": f"test-{int(time.time())}",
            "api_key": "test-api-key-123"
        }
        response = requests.post(f"{MEEP_URL}/api/meep/integrate", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Integração criada com ID: {data.get('id')}")
            print(f"   Evento ID: {data.get('evento_id')}")
            print(f"   Status: {data.get('sync_status')}")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Falha ao criar integração: {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Erro ao criar integração: {str(e)}")
        results["failed"] += 1
    
    # Teste 5: Obter Integração
    print("\n[5] Obtendo integração do evento 1...")
    try:
        response = requests.get(f"{MEEP_URL}/api/meep/integration/1")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Integração encontrada")
            print(f"   ID: {data.get('id')}")
            print(f"   MEEP Event ID: {data.get('meep_event_id')}")
            print(f"   Status: {data.get('sync_status')}")
            results["passed"] += 1
        elif response.status_code == 404:
            print(f"   [INFO] Nenhuma integração encontrada para evento 1")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Erro ao obter integração: {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha ao obter integração: {str(e)}")
        results["failed"] += 1
    
    # Teste 6: Criar Analytics
    print("\n[6] Criando analytics MEEP...")
    try:
        params = {
            "evento_id": 1,
            "total_requests": 150,
            "unique_visitors": 75
        }
        response = requests.post(f"{MEEP_URL}/api/meep/analytics/1", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Analytics criado com ID: {data.get('id')}")
            print(f"   Total Requests: {data.get('total_requests')}")
            print(f"   Unique Visitors: {data.get('unique_visitors')}")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Falha ao criar analytics: {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Erro ao criar analytics: {str(e)}")
        results["failed"] += 1
    
    # Teste 7: Obter Analytics
    print("\n[7] Obtendo analytics do evento 1...")
    try:
        response = requests.get(f"{MEEP_URL}/api/meep/analytics/1")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Analytics obtido")
            if data.get('id'):
                print(f"   ID: {data.get('id')}")
                print(f"   Total Requests: {data.get('total_requests')}")
                print(f"   Unique Visitors: {data.get('unique_visitors')}")
                print(f"   Conversion Rate: {data.get('conversion_rate')}")
            else:
                print(f"   [INFO] Nenhum analytics encontrado")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Erro ao obter analytics: {response.status_code}")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha ao obter analytics: {str(e)}")
        results["failed"] += 1
    
    # Teste 8: Verificar Documentação
    print("\n[8] Verificando documentação da API...")
    try:
        response = requests.get(f"{MEEP_URL}/docs")
        if response.status_code == 200:
            print(f"   [OK] Documentação disponível em: {MEEP_URL}/docs")
            results["passed"] += 1
        else:
            print(f"   [ERRO] Documentação não acessível")
            results["failed"] += 1
    except Exception as e:
        print(f"   [ERRO] Falha ao acessar documentação: {str(e)}")
        results["failed"] += 1
    
    # Resumo
    print_section("RESUMO DOS TESTES")
    print(f"\nTestes executados: {results['passed'] + results['failed']}")
    print(f"Sucessos: {results['passed']}")
    print(f"Falhas: {results['failed']}")
    
    if results["failed"] == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
    else:
        print(f"\n⚠️ {results['failed']} teste(s) falharam")
    
    # URLs para acesso manual
    print_section("URLS PARA TESTE MANUAL")
    print(f"\nFrontend:")
    print(f"  Login: http://localhost:5174/login")
    print(f"  Dashboard MEEP: http://localhost:5174/meep/dashboard")
    print(f"  Analytics: http://localhost:5174/meep/analytics")
    print(f"\nBackend:")
    print(f"  Auth Docs: {AUTH_URL}/docs")
    print(f"  MEEP Docs: {MEEP_URL}/docs")
    print(f"\nCredenciais:")
    print(f"  CPF: 00000000000")
    print(f"  Senha: 0000")

if __name__ == "__main__":
    test_meep_api()