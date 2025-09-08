#!/usr/bin/env python3

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_frontend_login():
    """Testa o login completo no frontend"""
    
    print("🚀 Iniciando teste de login no frontend...")
    
    # Configurar Chrome headless
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,720')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        print("🌐 Navegando para página de login...")
        driver.get("http://localhost:5173/login")
        
        # Aguardar página carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("📋 Página carregada, procurando campos...")
        
        # Aguardar elementos carregarem
        time.sleep(2)
        
        # Encontrar campo CPF
        try:
            cpf_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder*="000.000.000-00"]'))
            )
            print("✅ Campo CPF encontrado")
        except TimeoutException:
            # Tentar outras seletores
            try:
                cpf_input = driver.find_element(By.CSS_SELECTOR, 'input[id="cpf"]')
                print("✅ Campo CPF encontrado (por ID)")
            except NoSuchElementException:
                cpf_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
                print("✅ Campo CPF encontrado (por type)")
        
        # Encontrar campo senha
        try:
            senha_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder*="Digite sua senha"]'))
            )
            print("✅ Campo senha encontrado")
        except TimeoutException:
            try:
                senha_input = driver.find_element(By.CSS_SELECTOR, 'input[id="senha"]')
                print("✅ Campo senha encontrado (por ID)")
            except NoSuchElementException:
                senha_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
                print("✅ Campo senha encontrado (por type)")
        
        # Preencher formulário
        print("✍️ Preenchendo CPF...")
        cpf_input.clear()
        cpf_input.send_keys("066.012.061-54")
        
        print("✍️ Preenchendo senha...")
        senha_input.clear()
        senha_input.send_keys("101112")
        
        # Aguardar um pouco
        time.sleep(1)
        
        # Capturar estado inicial
        initial_url = driver.current_url
        initial_local_storage = driver.execute_script("return JSON.stringify({token: localStorage.getItem('token'), usuario: localStorage.getItem('usuario')});")
        
        print(f"📍 URL inicial: {initial_url}")
        print(f"💾 Local storage inicial: {initial_local_storage}")
        
        # Encontrar e clicar no botão de login
        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
            )
            print("✅ Botão de login encontrado")
        except TimeoutException:
            login_button = driver.find_element(By.CSS_SELECTOR, 'button:contains("Entrar")')
            print("✅ Botão de login encontrado (alternativo)")
        
        print("🔐 Clicando no botão de login...")
        login_button.click()
        
        # Aguardar processo de login
        print("⏱️ Aguardando resultado do login...")
        time.sleep(5)
        
        # Capturar estado final
        final_url = driver.current_url
        final_local_storage = driver.execute_script("return JSON.stringify({token: localStorage.getItem('token'), usuario: localStorage.getItem('usuario')});")
        
        print(f"📍 URL final: {final_url}")
        print(f"💾 Local storage final: {final_local_storage}")
        
        # Analisar resultado
        final_storage_data = json.loads(final_local_storage)
        
        print("\n📊 ANÁLISE DO RESULTADO:")
        print(f"  - URL mudou: {initial_url != final_url}")
        print(f"  - Token presente: {bool(final_storage_data.get('token'))}")
        print(f"  - Usuário presente: {bool(final_storage_data.get('usuario'))}")
        
        if final_storage_data.get('usuario'):
            try:
                user_data = json.loads(final_storage_data['usuario'])
                print(f"  - Nome do usuário: {user_data.get('nome', 'N/A')}")
                print(f"  - Tipo do usuário: {user_data.get('tipo', 'N/A')}")
            except json.JSONDecodeError:
                print("  - Erro ao decodificar dados do usuário")
        
        # Verificar se login foi bem-sucedido
        if final_url.endswith('/login'):
            print("\n❌ PROBLEMA IDENTIFICADO: Usuário permanece na página de login!")
            
            # Verificar mensagens de erro
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, '[role="alert"], .error, .text-red-500, .text-destructive')
                if error_elements:
                    print("🚨 Mensagens de erro encontradas:")
                    for error in error_elements:
                        if error.text.strip():
                            print(f"    - {error.text.strip()}")
                else:
                    print("❓ Nenhuma mensagem de erro visível")
            except:
                print("❓ Não foi possível verificar mensagens de erro")
            
            # Verificar console do navegador
            try:
                logs = driver.get_log('browser')
                if logs:
                    print("📝 Logs do console:")
                    for log in logs[-10:]:  # Últimos 10 logs
                        print(f"    [{log['level']}] {log['message']}")
                else:
                    print("📝 Nenhum log do console")
            except:
                print("❓ Não foi possível acessar logs do console")
                
        elif '/app' in final_url:
            print("\n✅ SUCESSO: Login realizado e usuário redirecionado para área autenticada!")
            
        else:
            print(f"\n⚠️ RESULTADO INESPERADO: URL final não é nem login nem app: {final_url}")
        
        return {
            'success': '/app' in final_url,
            'initial_url': initial_url,
            'final_url': final_url,
            'token_present': bool(final_storage_data.get('token')),
            'user_present': bool(final_storage_data.get('usuario')),
            'stayed_in_login': final_url.endswith('/login')
        }
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    result = test_frontend_login()
    print(f"\n🏁 Resultado final: {result}")
