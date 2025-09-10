#!/usr/bin/env python3
"""
Engenharia Reversa Completa do Sistema MEEP
Captura todas as funcionalidades para implementação no Painel Universal
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
import time

class MEEPReverseEngineering:
    def __init__(self):
        self.base_url = "https://beta.portal.meep.com.br"
        self.credentials = {
            "email": "toretomal@icloud.com",
            "password": "10041210Cl@."
        }
        self.captured_data = {
            "timestamp": datetime.now().isoformat(),
            "pages": {},
            "api_endpoints": [],
            "features": {},
            "ui_components": {},
            "database_schema": {},
            "business_logic": {}
        }
        self.screenshots_dir = Path("meep_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
    async def login(self, page: Page) -> bool:
        """Realiza login no sistema MEEP"""
        try:
            print("[LOGIN] Acessando página de login...")
            await page.goto(f"{self.base_url}/login", wait_until="networkidle")
            
            # Capturar screenshot da tela de login
            await page.screenshot(path=self.screenshots_dir / "01_login_page.png")
            
            # Preencher credenciais
            print("[LOGIN] Preenchendo credenciais...")
            await page.fill('input[type="email"], input[name="email"], input[id="email"]', self.credentials["email"])
            await page.fill('input[type="password"], input[name="password"], input[id="password"]', self.credentials["password"])
            
            # Capturar screenshot com credenciais
            await page.screenshot(path=self.screenshots_dir / "02_login_filled.png")
            
            # Clicar no botão de login
            await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")')
            
            # Aguardar navegação
            await page.wait_for_navigation(wait_until="networkidle", timeout=10000)
            
            # Verificar se login foi bem sucedido
            await page.screenshot(path=self.screenshots_dir / "03_after_login.png")
            
            print("[LOGIN] Login realizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Erro no login: {str(e)}")
            return False
    
    async def capture_dashboard(self, page: Page):
        """Captura estrutura e funcionalidades do dashboard"""
        print("[DASHBOARD] Analisando dashboard...")
        
        dashboard_data = {
            "url": page.url,
            "title": await page.title(),
            "widgets": [],
            "menus": [],
            "stats": []
        }
        
        # Capturar widgets do dashboard
        widgets = await page.query_selector_all('[class*="widget"], [class*="card"], [class*="stat"]')
        for widget in widgets:
            widget_text = await widget.text_content()
            if widget_text:
                dashboard_data["widgets"].append(widget_text.strip())
        
        # Capturar menu lateral
        menu_items = await page.query_selector_all('[class*="menu"] a, nav a, [class*="sidebar"] a')
        for item in menu_items:
            text = await item.text_content()
            href = await item.get_attribute("href")
            if text:
                dashboard_data["menus"].append({
                    "text": text.strip(),
                    "href": href
                })
        
        await page.screenshot(path=self.screenshots_dir / "04_dashboard.png")
        self.captured_data["pages"]["dashboard"] = dashboard_data
        
    async def capture_events_module(self, page: Page):
        """Captura módulo de eventos"""
        print("[EVENTOS] Analisando módulo de eventos...")
        
        try:
            # Navegar para eventos
            await page.click('a:has-text("Eventos"), [href*="evento"]')
            await page.wait_for_load_state("networkidle")
            
            events_data = {
                "url": page.url,
                "features": [],
                "forms": {},
                "tables": {}
            }
            
            # Capturar lista de eventos
            await page.screenshot(path=self.screenshots_dir / "05_events_list.png")
            
            # Tentar criar novo evento
            if await page.query_selector('button:has-text("Novo"), button:has-text("Criar")'):
                await page.click('button:has-text("Novo"), button:has-text("Criar")')
                await page.wait_for_timeout(2000)
                
                # Capturar campos do formulário
                form_fields = await page.query_selector_all('input, select, textarea')
                events_data["forms"]["create_event"] = []
                
                for field in form_fields:
                    field_name = await field.get_attribute("name") or await field.get_attribute("id")
                    field_type = await field.get_attribute("type")
                    field_placeholder = await field.get_attribute("placeholder")
                    
                    if field_name:
                        events_data["forms"]["create_event"].append({
                            "name": field_name,
                            "type": field_type,
                            "placeholder": field_placeholder
                        })
                
                await page.screenshot(path=self.screenshots_dir / "06_create_event_form.png")
            
            self.captured_data["features"]["events"] = events_data
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar eventos: {str(e)}")
    
    async def capture_checkin_module(self, page: Page):
        """Captura módulo de check-in"""
        print("[CHECKIN] Analisando módulo de check-in...")
        
        try:
            # Navegar para check-in
            await page.click('a:has-text("Check"), [href*="checkin"]')
            await page.wait_for_load_state("networkidle")
            
            checkin_data = {
                "url": page.url,
                "features": [],
                "qr_scanner": False,
                "manual_checkin": False
            }
            
            # Verificar se tem scanner QR
            if await page.query_selector('[class*="camera"], [class*="qr"], [class*="scanner"]'):
                checkin_data["qr_scanner"] = True
            
            # Verificar check-in manual
            if await page.query_selector('input[placeholder*="CPF"], input[placeholder*="código"]'):
                checkin_data["manual_checkin"] = True
            
            await page.screenshot(path=self.screenshots_dir / "07_checkin.png")
            self.captured_data["features"]["checkin"] = checkin_data
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar check-in: {str(e)}")
    
    async def capture_pdv_module(self, page: Page):
        """Captura módulo PDV"""
        print("[PDV] Analisando módulo PDV...")
        
        try:
            # Navegar para PDV
            await page.click('a:has-text("PDV"), a:has-text("Vendas"), [href*="pdv"]')
            await page.wait_for_load_state("networkidle")
            
            pdv_data = {
                "url": page.url,
                "products_grid": False,
                "cart": False,
                "payment_methods": [],
                "features": []
            }
            
            # Verificar grid de produtos
            if await page.query_selector('[class*="product"], [class*="produto"]'):
                pdv_data["products_grid"] = True
            
            # Verificar carrinho
            if await page.query_selector('[class*="cart"], [class*="carrinho"]'):
                pdv_data["cart"] = True
            
            # Capturar métodos de pagamento
            payment_buttons = await page.query_selector_all('[class*="payment"] button, [class*="pagamento"] button')
            for btn in payment_buttons:
                text = await btn.text_content()
                if text:
                    pdv_data["payment_methods"].append(text.strip())
            
            await page.screenshot(path=self.screenshots_dir / "08_pdv.png")
            self.captured_data["features"]["pdv"] = pdv_data
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar PDV: {str(e)}")
    
    async def capture_financial_module(self, page: Page):
        """Captura módulo financeiro"""
        print("[FINANCEIRO] Analisando módulo financeiro...")
        
        try:
            # Navegar para financeiro
            await page.click('a:has-text("Financeiro"), a:has-text("Relatórios"), [href*="financ"]')
            await page.wait_for_load_state("networkidle")
            
            financial_data = {
                "url": page.url,
                "reports": [],
                "charts": False,
                "export_options": []
            }
            
            # Verificar gráficos
            if await page.query_selector('canvas, [class*="chart"], svg[class*="graph"]'):
                financial_data["charts"] = True
            
            # Verificar opções de exportação
            export_buttons = await page.query_selector_all('button:has-text("Export"), button:has-text("Download")')
            for btn in export_buttons:
                text = await btn.text_content()
                if text:
                    financial_data["export_options"].append(text.strip())
            
            await page.screenshot(path=self.screenshots_dir / "09_financial.png")
            self.captured_data["features"]["financial"] = financial_data
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar financeiro: {str(e)}")
    
    async def capture_api_calls(self, page: Page):
        """Captura chamadas de API"""
        print("[API] Interceptando chamadas de API...")
        
        api_calls = []
        
        def handle_request(request):
            if "api" in request.url or "graphql" in request.url:
                api_calls.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers)
                })
        
        page.on("request", handle_request)
        
        # Navegar por algumas páginas para capturar APIs
        await page.goto(f"{self.base_url}/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        self.captured_data["api_endpoints"] = api_calls
    
    async def capture_network_requests(self, page: Page):
        """Captura requisições de rede para entender a arquitetura"""
        print("[NETWORK] Analisando requisições de rede...")
        
        requests_data = []
        
        def handle_response(response):
            if response.status == 200:
                requests_data.append({
                    "url": response.url,
                    "status": response.status,
                    "type": response.request.resource_type
                })
        
        page.on("response", handle_response)
        
        # Navegar para capturar requisições
        await page.goto(f"{self.base_url}/dashboard", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        self.captured_data["network_requests"] = requests_data
    
    async def analyze_ui_components(self, page: Page):
        """Analisa componentes UI utilizados"""
        print("[UI] Analisando componentes de interface...")
        
        ui_components = {
            "buttons": [],
            "forms": [],
            "tables": [],
            "modals": [],
            "cards": []
        }
        
        # Analisar botões
        buttons = await page.query_selector_all('button')
        for btn in buttons[:10]:  # Limitar para não demorar muito
            text = await btn.text_content()
            classes = await btn.get_attribute("class")
            if text:
                ui_components["buttons"].append({
                    "text": text.strip(),
                    "classes": classes
                })
        
        # Analisar tabelas
        tables = await page.query_selector_all('table')
        ui_components["tables"] = len(tables)
        
        # Analisar cards
        cards = await page.query_selector_all('[class*="card"]')
        ui_components["cards"] = len(cards)
        
        self.captured_data["ui_components"] = ui_components
    
    async def run_complete_analysis(self):
        """Executa análise completa do sistema MEEP"""
        print("\n" + "="*60)
        print(" INICIANDO ENGENHARIA REVERSA DO SISTEMA MEEP")
        print("="*60)
        
        async with async_playwright() as p:
            # Usar Chrome para melhor compatibilidade
            browser = await p.chromium.launch(
                headless=False,  # Mostrar navegador para debug
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            
            page = await context.new_page()
            
            try:
                # 1. Login
                if not await self.login(page):
                    print("[ERROR] Falha no login. Abortando...")
                    return
                
                # 2. Dashboard
                await self.capture_dashboard(page)
                await page.wait_for_timeout(2000)
                
                # 3. Eventos
                await self.capture_events_module(page)
                await page.wait_for_timeout(2000)
                
                # 4. Check-in
                await self.capture_checkin_module(page)
                await page.wait_for_timeout(2000)
                
                # 5. PDV
                await self.capture_pdv_module(page)
                await page.wait_for_timeout(2000)
                
                # 6. Financeiro
                await self.capture_financial_module(page)
                await page.wait_for_timeout(2000)
                
                # 7. Capturar APIs
                await self.capture_api_calls(page)
                
                # 8. Analisar UI
                await self.analyze_ui_components(page)
                
                # 9. Network
                await self.capture_network_requests(page)
                
                print("\n[SUCCESS] Análise completa realizada!")
                
            except Exception as e:
                print(f"[ERROR] Erro durante análise: {str(e)}")
                
            finally:
                # Salvar dados capturados
                self.save_captured_data()
                
                # Manter navegador aberto por 5 segundos para verificação
                await page.wait_for_timeout(5000)
                await browser.close()
    
    def save_captured_data(self):
        """Salva dados capturados em arquivo JSON"""
        output_file = Path("meep_reverse_engineering_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.captured_data, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Dados salvos em: {output_file}")
        
        # Gerar relatório de implementação
        self.generate_implementation_report()
    
    def generate_implementation_report(self):
        """Gera relatório de funcionalidades para implementar"""
        report = []
        report.append("# FUNCIONALIDADES MEEP PARA IMPLEMENTAR NO PAINEL UNIVERSAL\n")
        report.append(f"Data da Análise: {self.captured_data['timestamp']}\n")
        
        # Dashboard
        if "dashboard" in self.captured_data["pages"]:
            report.append("\n## DASHBOARD")
            dashboard = self.captured_data["pages"]["dashboard"]
            report.append(f"- Widgets encontrados: {len(dashboard.get('widgets', []))}")
            report.append(f"- Itens de menu: {len(dashboard.get('menus', []))}")
        
        # Features
        for feature_name, feature_data in self.captured_data["features"].items():
            report.append(f"\n## {feature_name.upper()}")
            for key, value in feature_data.items():
                if isinstance(value, list):
                    report.append(f"- {key}: {len(value)} items")
                else:
                    report.append(f"- {key}: {value}")
        
        # UI Components
        if self.captured_data["ui_components"]:
            report.append("\n## COMPONENTES UI")
            ui = self.captured_data["ui_components"]
            report.append(f"- Botões únicos: {len(ui.get('buttons', []))}")
            report.append(f"- Tabelas: {ui.get('tables', 0)}")
            report.append(f"- Cards: {ui.get('cards', 0)}")
        
        # Salvar relatório
        report_file = Path("meep_implementation_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        print(f"[REPORT] Relatório salvo em: {report_file}")

async def main():
    """Função principal"""
    analyzer = MEEPReverseEngineering()
    await analyzer.run_complete_analysis()

if __name__ == "__main__":
    print("Iniciando engenharia reversa do MEEP...")
    asyncio.run(main())