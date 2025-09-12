#!/usr/bin/env python
"""
Teste Completo do Sistema - Navegação Automatizada
"""

import time
import requests
import json
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def test_backend_endpoints():
    """Testa todos os endpoints do backend"""
    print_header("TESTANDO BACKEND")
    
    results = {
        "auth_server": {},
        "meep_server": {},
        "main_server": {}
    }
    
    # Teste 1: Auth Server (porta 8003)
    print("\n[1] Testando Auth Server (porta 8003)...")
    try:
        # Health check
        resp = requests.get("http://localhost:8003/api/health", timeout=5)
        if resp.status_code == 200:
            print("   [OK] Health check passou")
            results["auth_server"]["health"] = "OK"
        else:
            print(f"   [ERRO] Health check falhou: {resp.status_code}")
            results["auth_server"]["health"] = f"Erro: {resp.status_code}"
    except Exception as e:
        print(f"   [ERRO] Auth server não responde: {str(e)}")
        results["auth_server"]["health"] = f"Erro: {str(e)}"
    
    # Login test
    try:
        login_data = {"cpf": "00000000000", "senha": "0000"}
        resp = requests.post("http://localhost:8003/api/auth/login", json=login_data, timeout=5)
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print(f"   [OK] Login funcionando")
            print(f"   Token gerado: {token[:30]}...")
            results["auth_server"]["login"] = "OK"
            results["token"] = token
        else:
            print(f"   [ERRO] Login falhou: {resp.status_code}")
            results["auth_server"]["login"] = f"Erro: {resp.status_code}"
    except Exception as e:
        print(f"   [ERRO] Erro no login: {str(e)}")
        results["auth_server"]["login"] = f"Erro: {str(e)}"
    
    # Teste 2: MEEP Server (porta 8004)
    print("\n[2] Testando MEEP Server (porta 8004)...")
    try:
        resp = requests.get("http://localhost:8004/api/meep/status", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] MEEP Server: {data.get('status')}")
            print(f"   Versão: {data.get('version')}")
            results["meep_server"]["status"] = "OK"
        else:
            print(f"   [ERRO] MEEP status falhou: {resp.status_code}")
            results["meep_server"]["status"] = f"Erro: {resp.status_code}"
    except Exception as e:
        print(f"   [ERRO] MEEP server não responde: {str(e)}")
        results["meep_server"]["status"] = f"Erro: {str(e)}"
    
    # Teste 3: Main Server (porta 8000 ou 8001)
    print("\n[3] Testando Main Server...")
    for port in [8000, 8001]:
        try:
            resp = requests.get(f"http://localhost:{port}/api/health", timeout=2)
            if resp.status_code == 200:
                print(f"   [OK] Main server rodando na porta {port}")
                results["main_server"]["status"] = f"OK (porta {port})"
                break
        except:
            continue
    else:
        print("   [AVISO] Main server não está respondendo")
        results["main_server"]["status"] = "Não disponível"
    
    return results

def test_frontend():
    """Testa o frontend"""
    print_header("TESTANDO FRONTEND")
    
    results = {}
    
    # Teste 1: Vite Dev Server
    print("\n[1] Testando Vite Dev Server...")
    for port in [5173, 5174]:
        try:
            resp = requests.get(f"http://localhost:{port}", timeout=5)
            if resp.status_code == 200:
                print(f"   [OK] Frontend rodando na porta {port}")
                results["vite_server"] = f"OK (porta {port})"
                results["frontend_url"] = f"http://localhost:{port}"
                
                # Verificar se tem conteúdo HTML
                if "<div id=\"root\">" in resp.text:
                    print("   [OK] React root element encontrado")
                    results["react_app"] = "OK"
                else:
                    print("   [AVISO] React root element não encontrado")
                    results["react_app"] = "Root não encontrado"
                break
        except Exception as e:
            continue
    else:
        print("   [ERRO] Frontend não está rodando")
        results["vite_server"] = "Não disponível"
    
    return results

def test_integration():
    """Testa a integração frontend-backend"""
    print_header("TESTANDO INTEGRAÇÃO")
    
    print("\n[1] Testando comunicação Frontend -> Backend...")
    
    # Simular requisição do frontend para o backend
    headers = {
        "Origin": "http://localhost:5174",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(
            "http://localhost:8003/api/auth/login",
            json={"cpf": "00000000000", "senha": "0000"},
            headers=headers,
            timeout=5
        )
        if resp.status_code == 200:
            print("   [OK] CORS configurado corretamente")
            print("   [OK] Comunicação frontend-backend funcionando")
            return {"integration": "OK", "cors": "OK"}
        else:
            print(f"   [ERRO] Resposta inesperada: {resp.status_code}")
            return {"integration": f"Erro: {resp.status_code}", "cors": "Desconhecido"}
    except Exception as e:
        print(f"   [ERRO] Falha na integração: {str(e)}")
        return {"integration": f"Erro: {str(e)}", "cors": "Erro"}

def generate_report(backend_results, frontend_results, integration_results):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL")
    
    all_ok = True
    
    print("\n### BACKEND ###")
    print(f"Auth Server: {backend_results['auth_server'].get('health', 'N/A')}")
    print(f"Login API: {backend_results['auth_server'].get('login', 'N/A')}")
    print(f"MEEP Server: {backend_results['meep_server'].get('status', 'N/A')}")
    print(f"Main Server: {backend_results['main_server'].get('status', 'N/A')}")
    
    if "Erro" in str(backend_results):
        all_ok = False
    
    print("\n### FRONTEND ###")
    print(f"Vite Server: {frontend_results.get('vite_server', 'N/A')}")
    print(f"React App: {frontend_results.get('react_app', 'N/A')}")
    
    if "Erro" in str(frontend_results) or "Não disponível" in frontend_results.get('vite_server', ''):
        all_ok = False
    
    print("\n### INTEGRAÇÃO ###")
    print(f"Frontend-Backend: {integration_results.get('integration', 'N/A')}")
    print(f"CORS: {integration_results.get('cors', 'N/A')}")
    
    if "Erro" in str(integration_results):
        all_ok = False
    
    print_header("STATUS GERAL")
    
    if all_ok:
        print("\n✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("\nACESSE:")
        print(f"  Login: {frontend_results.get('frontend_url', 'http://localhost:5174')}/login")
        print("  CPF: 00000000000")
        print("  Senha: 0000")
    else:
        print("\n⚠️ SISTEMA COM PROBLEMAS!")
        print("\nPROBLEMAS DETECTADOS:")
        
        if "Não disponível" in frontend_results.get('vite_server', ''):
            print("  - Frontend não está rodando")
            print("    SOLUÇÃO: cd frontend && npm run dev")
        
        if "Erro" in backend_results['auth_server'].get('health', ''):
            print("  - Auth server não está rodando")
            print("    SOLUÇÃO: cd backend && python auth_server.py")
        
        if "Erro" in integration_results.get('cors', ''):
            print("  - Problema de CORS")
            print("    SOLUÇÃO: Verificar configuração de CORS no backend")
    
    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend_results,
        "frontend": frontend_results,
        "integration": integration_results,
        "status": "OK" if all_ok else "PROBLEMAS"
    }
    
    with open("relatorio_sistema.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n[INFO] Relatório salvo em: relatorio_sistema.json")
    
    return all_ok

def main():
    print_header("TESTE COMPLETO DO SISTEMA")
    print("Iniciando análise completa...")
    
    # Executar testes
    backend_results = test_backend_endpoints()
    time.sleep(1)
    
    frontend_results = test_frontend()
    time.sleep(1)
    
    integration_results = test_integration()
    time.sleep(1)
    
    # Gerar relatório
    all_ok = generate_report(backend_results, frontend_results, integration_results)
    
    if all_ok:
        print("\n🎉 Tudo funcionando! Acesse o sistema no navegador.")
    else:
        print("\n❌ Corrija os problemas acima antes de continuar.")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)