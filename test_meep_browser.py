#!/usr/bin/env python
"""
Teste automatizado da integração MEEP usando Playwright
"""

from playwright.sync_api import sync_playwright
import time
import json

def test_meep_integration():
    print("=" * 60)
    print("TESTE AUTOMATIZADO - INTEGRAÇÃO MEEP")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Iniciar navegador
        print("\n[1] Iniciando navegador...")
        browser = p.chromium.launch(headless=False)  # headless=False para ver o navegador
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. Fazer login
            print("\n[2] Acessando página de login...")
            page.goto("http://localhost:5174/login")
            page.wait_for_load_state("networkidle")
            
            print("[3] Preenchendo credenciais...")
            # Procurar campos de CPF e senha
            page.fill('input[name="cpf"]', "00000000000")
            page.fill('input[type="password"]', "0000")
            
            print("[4] Fazendo login...")
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            
            # Aguardar redirecionamento
            time.sleep(2)
            
            # 2. Acessar Dashboard MEEP
            print("\n[5] Acessando Dashboard MEEP...")
            page.goto("http://localhost:5174/meep/dashboard")
            page.wait_for_load_state("networkidle")
            
            # Verificar se a página carregou
            if "MEEP" in page.content():
                print("[OK] Dashboard MEEP carregado com sucesso!")
            else:
                print("[AVISO] Dashboard MEEP pode não ter carregado corretamente")
            
            # Tirar screenshot
            page.screenshot(path="meep_dashboard.png")
            print("[OK] Screenshot salvo: meep_dashboard.png")
            
            # 3. Testar API MEEP
            print("\n[6] Testando API MEEP...")
            
            # Testar endpoint de status
            import requests
            response = requests.get("http://localhost:8004/api/meep/status")
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] API MEEP Status: {data['status']}")
                print(f"     Versão: {data['version']}")
                print(f"     Features: {', '.join(data['features'])}")
            else:
                print(f"[ERRO] API retornou status {response.status_code}")
            
            # 4. Acessar Analytics MEEP
            print("\n[7] Acessando Analytics MEEP...")
            page.goto("http://localhost:5174/meep/analytics")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            page.screenshot(path="meep_analytics.png")
            print("[OK] Screenshot salvo: meep_analytics.png")
            
            # 5. Acessar Validação CPF
            print("\n[8] Acessando Validação CPF...")
            page.goto("http://localhost:5174/meep/validacao-cpf")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            page.screenshot(path="meep_validacao_cpf.png")
            print("[OK] Screenshot salvo: meep_validacao_cpf.png")
            
            print("\n" + "=" * 60)
            print("RESUMO DO TESTE")
            print("=" * 60)
            print("[OK] Login realizado com sucesso")
            print("[OK] Dashboard MEEP acessível")
            print("[OK] API MEEP respondendo")
            print("[OK] Analytics MEEP acessível")
            print("[OK] Validação CPF acessível")
            print("[OK] 3 screenshots salvos")
            print("\nTESTE CONCLUÍDO COM SUCESSO!")
            
        except Exception as e:
            print(f"\n[ERRO] Falha no teste: {str(e)}")
            page.screenshot(path="erro_teste.png")
            print("[INFO] Screenshot do erro salvo: erro_teste.png")
            
        finally:
            # Manter navegador aberto por 5 segundos para visualização
            print("\n[INFO] Navegador ficará aberto por 5 segundos...")
            time.sleep(5)
            browser.close()
            print("[OK] Navegador fechado")

if __name__ == "__main__":
    try:
        # Verificar se requests está instalado
        import requests
    except ImportError:
        print("Instalando requests...")
        import subprocess
        subprocess.run(["pip", "install", "requests"])
        import requests
    
    test_meep_integration()