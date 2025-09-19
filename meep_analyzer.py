"""
MEEP System Analyzer - Captura completa da estrutura do sistema MEEP
Usa Playwright para navegar e analisar o sistema real
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import os

class MEEPAnalyzer:
    def __init__(self):
        self.base_url = "https://beta.portal.meep.com.br"
        self.email = "TORETOMAL@ICLOUD.COM"
        self.password = "10041210Cl@."
        self.modules_to_analyze = [
            # Módulos já confirmados ✅
            {"path": "/private/dashboard/general", "name": "Dashboard Geral"},
            {"path": "/private/cardapio/cardapios", "name": "Cardápios"},
            {"path": "/private/relatorios/venda", "name": "Relatórios de Venda"},
            {"path": "/private/cadastros/clientes", "name": "Cadastro de Clientes"},
            {"path": "/private/financeiro/conta-digital", "name": "Conta Digital"},
            {"path": "/private/pdv", "name": "PDV"},
            {"path": "/private/meeperp", "name": "MEEP ERP"},

            # Módulos a investigar 🔍
            {"path": "/private/gestao-venda", "name": "Gestão de Vendas"},
            {"path": "/private/solucoes-online", "name": "Soluções Online"},
            {"path": "/private/ingressos", "name": "Ingressos"},
            {"path": "/private/equipe", "name": "Equipe"},
            {"path": "/private/pedidos", "name": "Pedidos"},
            {"path": "/private/mapa-operacao", "name": "Mapa de Operação"},
            {"path": "/private/marketing", "name": "Marketing"},
            {"path": "/private/bi", "name": "Business Intelligence"},
            {"path": "/private/automacao", "name": "Automação"},
            {"path": "/private/integracao", "name": "Integração"},
        ]
        self.captured_data = {
            "timestamp": datetime.now().isoformat(),
            "modules": [],
            "api_endpoints": [],
            "forms": [],
            "tables": [],
            "navigation": []
        }

    async def analyze(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Interceptar requisições de API
            page.on("request", self.capture_api_request)
            page.on("response", self.capture_api_response)

            try:
                # 1. Login
                print("🔐 Fazendo login no MEEP...")
                await self.login(page)

                # 2. Analisar cada módulo
                for module in self.modules_to_analyze:
                    print(f"📊 Analisando módulo: {module['name']}...")
                    await self.analyze_module(page, module)

                # 3. Capturar menu lateral completo
                print("🗂️ Capturando estrutura de navegação...")
                await self.capture_navigation(page)

                # 4. Salvar resultados
                await self.save_results()

            except Exception as e:
                print(f"❌ Erro: {e}")
            finally:
                await browser.close()

    async def login(self, page):
        """Realiza login no sistema MEEP"""
        await page.goto(self.base_url + "/login")
        await page.wait_for_load_state("networkidle")

        # Preencher formulário
        await page.fill('input[type="email"]', self.email)
        await page.fill('input[type="password"]', self.password)

        # Clicar no botão de login
        await page.click('button[type="submit"]')

        # Aguardar redirecionamento
        await page.wait_for_url("**/private/**", timeout=10000)
        print("✅ Login realizado com sucesso!")

    async def analyze_module(self, page, module):
        """Analisa um módulo específico"""
        try:
            await page.goto(self.base_url + module["path"])
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)  # Aguardar carregamento completo

            module_data = {
                "name": module["name"],
                "path": module["path"],
                "elements": {
                    "forms": [],
                    "tables": [],
                    "buttons": [],
                    "filters": [],
                    "charts": []
                }
            }

            # Capturar formulários
            forms = await page.query_selector_all('form')
            for form in forms:
                form_data = await self.extract_form_data(form)
                if form_data:
                    module_data["elements"]["forms"].append(form_data)

            # Capturar tabelas
            tables = await page.query_selector_all('table')
            for table in tables:
                table_data = await self.extract_table_structure(table)
                if table_data:
                    module_data["elements"]["tables"].append(table_data)

            # Capturar botões de ação
            buttons = await page.query_selector_all('button')
            for button in buttons:
                button_text = await button.text_content()
                if button_text:
                    module_data["elements"]["buttons"].append(button_text.strip())

            # Capturar filtros
            filters = await page.query_selector_all('[class*="filter"], [class*="search"]')
            for filter_el in filters:
                filter_type = await filter_el.get_attribute("type")
                module_data["elements"]["filters"].append(filter_type)

            # Capturar gráficos (canvas, svg com charts)
            charts = await page.query_selector_all('canvas, svg[class*="chart"]')
            module_data["elements"]["charts"] = len(charts)

            self.captured_data["modules"].append(module_data)
            print(f"  ✅ Módulo {module['name']} analisado")

        except Exception as e:
            print(f"  ⚠️ Erro ao analisar {module['name']}: {e}")

    async def extract_form_data(self, form):
        """Extrai estrutura de um formulário"""
        try:
            inputs = await form.query_selector_all('input, select, textarea')
            fields = []
            for input_el in inputs:
                field = {
                    "name": await input_el.get_attribute("name"),
                    "type": await input_el.get_attribute("type"),
                    "required": await input_el.get_attribute("required"),
                }
                fields.append(field)
            return {"fields": fields, "count": len(fields)}
        except:
            return None

    async def extract_table_structure(self, table):
        """Extrai estrutura de uma tabela"""
        try:
            headers = await table.query_selector_all('th')
            columns = []
            for header in headers:
                text = await header.text_content()
                if text:
                    columns.append(text.strip())

            rows = await table.query_selector_all('tbody tr')
            return {
                "columns": columns,
                "row_count": len(rows)
            }
        except:
            return None

    async def capture_navigation(self, page):
        """Captura estrutura completa do menu de navegação"""
        try:
            # Procurar menu lateral
            menu_items = await page.query_selector_all('[class*="menu-item"], [class*="nav-item"], aside a')

            for item in menu_items:
                text = await item.text_content()
                href = await item.get_attribute("href")
                if text and href:
                    self.captured_data["navigation"].append({
                        "text": text.strip(),
                        "href": href
                    })
        except Exception as e:
            print(f"  ⚠️ Erro ao capturar navegação: {e}")

    def capture_api_request(self, request):
        """Captura requisições de API"""
        if "/api/" in request.url or "/private/api/" in request.url:
            self.captured_data["api_endpoints"].append({
                "url": request.url,
                "method": request.method,
                "timestamp": datetime.now().isoformat()
            })

    def capture_api_response(self, response):
        """Captura respostas de API"""
        # Podemos adicionar análise de respostas se necessário
        pass

    async def save_results(self):
        """Salva resultados da análise"""
        filename = f"meep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.captured_data, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Análise salva em: {filename}")
        print(f"📊 Módulos analisados: {len(self.captured_data['modules'])}")
        print(f"🔗 Endpoints capturados: {len(self.captured_data['api_endpoints'])}")
        print(f"🧭 Items de navegação: {len(self.captured_data['navigation'])}")

async def main():
    print("🚀 Iniciando análise do sistema MEEP...")
    analyzer = MEEPAnalyzer()
    await analyzer.analyze()
    print("✅ Análise completa!")

if __name__ == "__main__":
    # Instalar playwright se necessário
    os.system("pip install playwright")
    os.system("playwright install chromium")

    # Executar análise
    asyncio.run(main())