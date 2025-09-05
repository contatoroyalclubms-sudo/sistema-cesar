#!/usr/bin/env python3
"""
Script para fazer engenharia reversa do sistema MEEP
Analisa todas as funcionalidades e gera documentação completa
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Instalando dependências...")
    os.system("pip install selenium webdriver-manager pillow")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    os.system("pip install webdriver-manager")
    from webdriver_manager.chrome import ChromeDriverManager

from PIL import Image
import base64
from io import BytesIO

class MEEPAnalyzer:
    def __init__(self):
        self.base_url = "https://beta.portal.meep.com.br"
        self.username = "toretomal@icloud.com"
        self.password = "352162Cl@"
        self.driver = None
        self.wait = None
        self.screenshots_dir = Path("meep_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "pages": {},
            "features": {},
            "api_endpoints": [],
            "ui_components": [],
            "workflows": [],
            "data_models": {}
        }
    
    def setup_driver(self):
        """Configura o driver do Selenium"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        # Habilitar captura de network
        options.add_experimental_option('perfLogsEnabled', True)
        options.add_experimental_option('w3c', False)
        options.set_capability('browserName', 'chrome')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def login(self):
        """Faz login no sistema MEEP"""
        print(f"Acessando {self.base_url}...")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        # Aguardar carregamento da página
        try:
            # Tentar encontrar campo de email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[id*='email']"))
            )
            email_field.clear()
            email_field.send_keys(self.username)
            
            # Campo de senha
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Botão de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Entrar'), button:contains('Login')")
            login_button.click()
            
            print("Login realizado com sucesso!")
            time.sleep(5)
            
            # Capturar screenshot após login
            self.take_screenshot("01_dashboard")
            
        except TimeoutException:
            print("Não foi possível fazer login automaticamente. Tentando método alternativo...")
            self.manual_navigation()
    
    def take_screenshot(self, name: str):
        """Captura screenshot da página atual"""
        screenshot_path = self.screenshots_dir / f"{name}.png"
        self.driver.save_screenshot(str(screenshot_path))
        print(f"Screenshot salvo: {screenshot_path}")
        return str(screenshot_path)
    
    def analyze_page(self, page_name: str):
        """Analisa uma página específica"""
        current_url = self.driver.current_url
        page_title = self.driver.title
        
        # Capturar elementos da página
        elements = {
            "buttons": len(self.driver.find_elements(By.TAG_NAME, "button")),
            "inputs": len(self.driver.find_elements(By.TAG_NAME, "input")),
            "selects": len(self.driver.find_elements(By.TAG_NAME, "select")),
            "tables": len(self.driver.find_elements(By.TAG_NAME, "table")),
            "forms": len(self.driver.find_elements(By.TAG_NAME, "form"))
        }
        
        # Capturar textos importantes
        headers = [h.text for h in self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")]
        
        # Capturar links de navegação
        nav_links = []
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href], nav a, aside a")
            for link in links[:20]:  # Limitar para não sobrecarregar
                try:
                    nav_links.append({
                        "text": link.text,
                        "href": link.get_attribute("href")
                    })
                except:
                    pass
        except:
            pass
        
        self.analysis["pages"][page_name] = {
            "url": current_url,
            "title": page_title,
            "elements": elements,
            "headers": headers,
            "navigation": nav_links,
            "screenshot": f"{page_name}.png"
        }
        
        return elements
    
    def analyze_network_requests(self):
        """Analisa requisições de rede para identificar APIs"""
        logs = self.driver.get_log('performance')
        
        api_calls = []
        for log in logs:
            message = json.loads(log['message'])
            if 'Network.requestWillBeSent' in message['message']['method']:
                params = message['message']['params']
                if 'request' in params:
                    url = params['request']['url']
                    if 'api' in url.lower() or 'graphql' in url.lower():
                        api_calls.append({
                            "url": url,
                            "method": params['request']['method']
                        })
        
        # Remover duplicatas
        unique_apis = []
        seen = set()
        for api in api_calls:
            key = f"{api['method']}:{api['url']}"
            if key not in seen:
                seen.add(key)
                unique_apis.append(api)
        
        self.analysis["api_endpoints"] = unique_apis
    
    def navigate_all_pages(self):
        """Navega por todas as páginas disponíveis do sistema"""
        pages_to_visit = [
            ("Dashboard", "/dashboard"),
            ("Eventos", "/eventos"),
            ("Criar Evento", "/eventos/novo"),
            ("Participantes", "/participantes"),
            ("Check-in", "/checkin"),
            ("PDV", "/pdv"),
            ("Financeiro", "/financeiro"),
            ("Relatórios", "/relatorios"),
            ("Configurações", "/configuracoes"),
            ("Estoque", "/estoque"),
            ("Produtos", "/produtos"),
            ("Comandas", "/comandas"),
            ("Mesas", "/mesas"),
            ("KDS", "/kds"),
            ("Promoters", "/promoters"),
            ("Rankings", "/rankings"),
            ("Cupons", "/cupons"),
            ("Fidelidade", "/fidelidade"),
            ("Integrações", "/integracoes"),
            ("Automação", "/automacao"),
            ("WhatsApp", "/whatsapp"),
            ("Impressoras", "/impressoras"),
            ("Colaboradores", "/colaboradores"),
            ("Permissões", "/permissoes"),
            ("Business Intelligence", "/bi"),
            ("Pesquisas", "/pesquisas"),
            ("Multi-Cardápio", "/multicardapio"),
            ("Cashless", "/cashless"),
            ("Tickets", "/tickets")
        ]
        
        for page_name, path in pages_to_visit:
            try:
                print(f"\nAnalisando página: {page_name}")
                
                # Tentar navegar pela URL
                self.driver.get(self.base_url + path)
                time.sleep(2)
                
                # Se falhar, tentar encontrar link na página
                if "404" in self.driver.title.lower() or "not found" in self.driver.page_source.lower():
                    self.driver.get(self.base_url)
                    time.sleep(1)
                    
                    # Procurar link no menu
                    try:
                        link = self.driver.find_element(By.PARTIAL_LINK_TEXT, page_name)
                        link.click()
                        time.sleep(2)
                    except:
                        print(f"  Página {page_name} não encontrada")
                        continue
                
                # Analisar página
                self.analyze_page(page_name.lower().replace(" ", "_"))
                
                # Capturar screenshot
                screenshot_name = f"{len(self.analysis['pages']):02d}_{page_name.lower().replace(' ', '_')}"
                self.take_screenshot(screenshot_name)
                
                # Analisar network requests
                self.analyze_network_requests()
                
            except Exception as e:
                print(f"  Erro ao analisar {page_name}: {str(e)}")
    
    def extract_ui_components(self):
        """Extrai componentes UI utilizados"""
        components = set()
        
        # Procurar por classes CSS comuns de frameworks
        elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
        
        for element in elements[:500]:  # Limitar análise
            try:
                classes = element.get_attribute("class") or ""
                
                # Identificar componentes por padrões de classe
                if "modal" in classes.lower():
                    components.add("Modal")
                if "dropdown" in classes.lower():
                    components.add("Dropdown")
                if "tab" in classes.lower():
                    components.add("Tabs")
                if "card" in classes.lower():
                    components.add("Card")
                if "table" in classes.lower():
                    components.add("Table")
                if "form" in classes.lower():
                    components.add("Form")
                if "chart" in classes.lower():
                    components.add("Chart")
                if "sidebar" in classes.lower():
                    components.add("Sidebar")
                if "navbar" in classes.lower():
                    components.add("Navbar")
            except:
                pass
        
        self.analysis["ui_components"] = list(components)
    
    def manual_navigation(self):
        """Navegação manual para análise visual"""
        print("\nIniciando navegação manual...")
        print("Por favor, faça login manualmente no navegador que foi aberto.")
        print("Pressione Enter quando estiver logado...")
        input()
        
        print("\nContinuando análise...")
        self.navigate_all_pages()
    
    def generate_report(self):
        """Gera relatório completo da análise"""
        report_path = Path("meep_engenharia_reversa_COMPLETA.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# MEEP - Engenharia Reversa Completa\n\n")
            f.write(f"**Data da Análise:** {self.analysis['timestamp']}\n\n")
            
            # Páginas analisadas
            f.write("## 📄 Páginas Analisadas\n\n")
            for page_name, page_data in self.analysis["pages"].items():
                f.write(f"### {page_name.replace('_', ' ').title()}\n")
                f.write(f"- **URL:** {page_data.get('url', 'N/A')}\n")
                f.write(f"- **Título:** {page_data.get('title', 'N/A')}\n")
                f.write(f"- **Screenshot:** ![{page_name}](meep_screenshots/{page_data.get('screenshot', '')})\n")
                
                if page_data.get('elements'):
                    f.write("- **Elementos:**\n")
                    for elem_type, count in page_data['elements'].items():
                        if count > 0:
                            f.write(f"  - {elem_type}: {count}\n")
                f.write("\n")
            
            # APIs identificadas
            f.write("## 🔌 APIs Identificadas\n\n")
            if self.analysis["api_endpoints"]:
                for api in self.analysis["api_endpoints"][:50]:  # Limitar para não ficar muito grande
                    f.write(f"- **{api.get('method', 'GET')}** `{api.get('url', '')}`\n")
            f.write("\n")
            
            # Componentes UI
            f.write("## 🎨 Componentes UI Identificados\n\n")
            for component in self.analysis["ui_components"]:
                f.write(f"- {component}\n")
            f.write("\n")
            
            # Funcionalidades identificadas
            f.write("## ⚡ Funcionalidades Principais\n\n")
            f.write(self.identify_features())
            
        print(f"\n✅ Relatório gerado: {report_path}")
        
        # Salvar análise em JSON
        json_path = Path("meep_analysis.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        print(f"✅ Análise JSON salva: {json_path}")
    
    def identify_features(self) -> str:
        """Identifica funcionalidades baseado nas páginas analisadas"""
        features = []
        
        page_names = list(self.analysis["pages"].keys())
        
        if any("dashboard" in p for p in page_names):
            features.append("- **Dashboard:** Visão geral e métricas do sistema")
        
        if any("evento" in p for p in page_names):
            features.append("- **Gestão de Eventos:** Criar, editar e gerenciar eventos")
        
        if any("checkin" in p or "check-in" in p for p in page_names):
            features.append("- **Check-in:** Sistema de entrada de participantes")
        
        if any("pdv" in p for p in page_names):
            features.append("- **PDV (Ponto de Venda):** Sistema de vendas integrado")
        
        if any("financeiro" in p for p in page_names):
            features.append("- **Financeiro:** Controle de receitas e despesas")
        
        if any("estoque" in p or "produto" in p for p in page_names):
            features.append("- **Estoque/Produtos:** Gestão de inventário")
        
        if any("comanda" in p for p in page_names):
            features.append("- **Comandas:** Sistema de comandas eletrônicas")
        
        if any("mesa" in p for p in page_names):
            features.append("- **Mesas:** Gestão de mesas e pedidos")
        
        if any("kds" in p for p in page_names):
            features.append("- **KDS:** Kitchen Display System para cozinha")
        
        if any("cashless" in p for p in page_names):
            features.append("- **Cashless:** Sistema de pagamento sem dinheiro")
        
        if any("relatorio" in p or "bi" in p for p in page_names):
            features.append("- **Relatórios/BI:** Analytics e Business Intelligence")
        
        return "\n".join(features) + "\n"
    
    def run(self):
        """Executa análise completa"""
        try:
            print("🚀 Iniciando análise do sistema MEEP...")
            self.setup_driver()
            self.login()
            self.navigate_all_pages()
            self.extract_ui_components()
            self.generate_report()
            print("\n✅ Análise completa finalizada!")
            
        except Exception as e:
            print(f"\n❌ Erro durante análise: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.driver:
                print("\nFechando navegador...")
                self.driver.quit()

if __name__ == "__main__":
    analyzer = MEEPAnalyzer()
    analyzer.run()