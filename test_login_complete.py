#!/usr/bin/env python3
"""
Teste Completo do Sistema de Login
Usando Playwright para navegação automatizada
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

class LoginSystemTester:
    def __init__(self):
        self.frontend_url = "http://localhost:5174"
        self.backend_url = "http://localhost:8003"
        self.errors = []
        self.successes = []
        
    def log(self, message, type="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{type}] {message}")
        
    def test_backend_health(self):
        """Testa se o backend está respondendo"""
        import requests
        try:
            response = requests.get(f"{self.backend_url}/api/health")
            if response.status_code == 200:
                self.log("✅ Backend está saudável", "SUCCESS")
                self.successes.append("Backend Health Check")
                return True
            else:
                self.log(f"❌ Backend retornou status {response.status_code}", "ERROR")
                self.errors.append(f"Backend status: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao conectar no backend: {e}", "ERROR")
            self.errors.append(f"Backend connection: {str(e)}")
            return False
    
    def test_api_login(self):
        """Testa login direto via API"""
        import requests
        try:
            # Teste com credenciais corretas
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"cpf": "00000000000", "senha": "0000"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log("✅ API Login funcionando corretamente", "SUCCESS")
                    self.successes.append("API Login")
                    return data["access_token"]
                else:
                    self.log("❌ API Login não retornou token", "ERROR")
                    self.errors.append("API Login: no token")
                    return None
            else:
                self.log(f"❌ API Login falhou: {response.status_code}", "ERROR")
                self.errors.append(f"API Login: status {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro no teste de API: {e}", "ERROR")
            self.errors.append(f"API test: {str(e)}")
            return None
    
    def test_frontend_navigation(self):
        """Testa navegação no frontend com Playwright"""
        with sync_playwright() as p:
            # Inicia navegador
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # 1. Acessa página inicial
                self.log("🔍 Acessando página inicial...")
                page.goto(self.frontend_url, wait_until="networkidle")
                
                # 2. Verifica se foi redirecionado para login
                current_url = page.url
                if "/login" in current_url:
                    self.log("✅ Redirecionado para login corretamente", "SUCCESS")
                    self.successes.append("Login redirect")
                else:
                    self.log(f"⚠️ URL atual: {current_url}", "WARNING")
                
                # 3. Verifica elementos do formulário
                self.log("🔍 Verificando elementos do formulário...")
                
                # Aguarda o formulário carregar
                page.wait_for_selector('input[name="cpf"]', timeout=5000)
                page.wait_for_selector('input[name="senha"]', timeout=5000)
                
                cpf_field = page.locator('input[name="cpf"]')
                senha_field = page.locator('input[name="senha"]')
                login_button = page.locator('button[type="submit"]')
                
                if cpf_field.is_visible() and senha_field.is_visible():
                    self.log("✅ Campos de formulário encontrados", "SUCCESS")
                    self.successes.append("Form fields visible")
                else:
                    self.log("❌ Campos de formulário não visíveis", "ERROR")
                    self.errors.append("Form fields not visible")
                
                # 4. Tenta fazer login
                self.log("🔍 Tentando fazer login...")
                
                # Preenche formulário
                cpf_field.fill("00000000000")
                senha_field.fill("0000")
                
                # Captura requests de rede
                responses = []
                def handle_response(response):
                    if "/api/auth/login" in response.url:
                        responses.append(response)
                
                page.on("response", handle_response)
                
                # Clica no botão de login
                login_button.click()
                
                # Aguarda resposta
                page.wait_for_timeout(3000)
                
                # Verifica resposta da API
                if responses:
                    login_response = responses[0]
                    if login_response.status == 200:
                        self.log("✅ Login bem-sucedido via frontend", "SUCCESS")
                        self.successes.append("Frontend login")
                        
                        # Verifica redirecionamento
                        page.wait_for_timeout(2000)
                        if "/dashboard" in page.url or "/home" in page.url:
                            self.log("✅ Redirecionado para dashboard", "SUCCESS")
                            self.successes.append("Dashboard redirect")
                        else:
                            self.log(f"⚠️ Não redirecionado. URL: {page.url}", "WARNING")
                    else:
                        self.log(f"❌ Login falhou: status {login_response.status}", "ERROR")
                        self.errors.append(f"Frontend login: status {login_response.status}")
                else:
                    self.log("❌ Nenhuma resposta de login capturada", "ERROR")
                    self.errors.append("No login response captured")
                
                # 5. Verifica localStorage
                storage = page.evaluate("() => Object.keys(localStorage)")
                if "token" in storage or "auth-storage" in storage:
                    self.log("✅ Token salvo no localStorage", "SUCCESS")
                    self.successes.append("Token storage")
                else:
                    self.log("⚠️ Token não encontrado no localStorage", "WARNING")
                
                # Captura screenshot
                page.screenshot(path="login_test_screenshot.png")
                self.log("📸 Screenshot salvo: login_test_screenshot.png", "INFO")
                
            except Exception as e:
                self.log(f"❌ Erro durante teste de frontend: {e}", "ERROR")
                self.errors.append(f"Frontend test: {str(e)}")
                page.screenshot(path="error_screenshot.png")
                
            finally:
                browser.close()
    
    def test_database_compatibility(self):
        """Verifica compatibilidade do banco de dados"""
        import sqlite3
        import os
        
        db_path = "C:\\Users\\User\\OneDrive\\Desktop\\sistema-v6-novo\\paineluniversal\\paineluniversal\\backend\\eventos.db"
        
        if not os.path.exists(db_path):
            self.log("⚠️ Banco de dados não encontrado", "WARNING")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica tabela de usuários
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            if cursor.fetchone():
                self.log("✅ Tabela 'usuarios' existe", "SUCCESS")
                self.successes.append("Users table exists")
                
                # Verifica estrutura
                cursor.execute("PRAGMA table_info(usuarios)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_fields = ['id', 'cpf', 'senha_hash']
                missing = [f for f in required_fields if f not in column_names]
                
                if not missing:
                    self.log("✅ Estrutura da tabela correta", "SUCCESS")
                    self.successes.append("Table structure")
                else:
                    self.log(f"❌ Campos faltando: {missing}", "ERROR")
                    self.errors.append(f"Missing fields: {missing}")
                
                # Verifica se há usuários
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                count = cursor.fetchone()[0]
                self.log(f"📊 Total de usuários no banco: {count}", "INFO")
                
            else:
                self.log("❌ Tabela 'usuarios' não existe", "ERROR")
                self.errors.append("Users table missing")
            
            conn.close()
            
        except Exception as e:
            self.log(f"❌ Erro ao acessar banco: {e}", "ERROR")
            self.errors.append(f"Database: {str(e)}")
    
    def generate_report(self):
        """Gera relatório completo"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE COMPATIBILIDADE DO SISTEMA DE LOGIN")
        print("="*60)
        
        print(f"\n✅ SUCESSOS ({len(self.successes)}):")
        for success in self.successes:
            print(f"  • {success}")
        
        print(f"\n❌ ERROS ({len(self.errors)}):")
        for error in self.errors:
            print(f"  • {error}")
        
        print("\n📈 ESTATÍSTICAS:")
        total = len(self.successes) + len(self.errors)
        if total > 0:
            success_rate = (len(self.successes) / total) * 100
            print(f"  Taxa de sucesso: {success_rate:.1f}%")
        
        print("\n🔧 RECOMENDAÇÕES:")
        if self.errors:
            if any("Backend" in e for e in self.errors):
                print("  • Verificar se o backend está rodando na porta correta")
            if any("Frontend" in e for e in self.errors):
                print("  • Verificar configuração do frontend e rotas")
            if any("Database" in e for e in self.errors):
                print("  • Verificar integridade do banco de dados")
        else:
            print("  • Sistema funcionando corretamente!")
        
        print("="*60)
        
        # Salva relatório em arquivo
        report = {
            "timestamp": datetime.now().isoformat(),
            "successes": self.successes,
            "errors": self.errors,
            "success_rate": (len(self.successes) / total * 100) if total > 0 else 0
        }
        
        with open("login_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n📁 Relatório salvo em: login_test_report.json")

def main():
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA DE LOGIN")
    print("="*60)
    
    tester = LoginSystemTester()
    
    # Executa testes
    print("\n1️⃣ TESTANDO BACKEND...")
    tester.test_backend_health()
    
    print("\n2️⃣ TESTANDO API DE LOGIN...")
    tester.test_api_login()
    
    print("\n3️⃣ TESTANDO BANCO DE DADOS...")
    tester.test_database_compatibility()
    
    print("\n4️⃣ TESTANDO FRONTEND COM PLAYWRIGHT...")
    tester.test_frontend_navigation()
    
    # Gera relatório
    tester.generate_report()

if __name__ == "__main__":
    main()