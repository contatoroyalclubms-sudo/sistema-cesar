import asyncio
import json
from playwright.async_api import async_playwright
import time
from datetime import datetime

class MEEPMapper:
    def __init__(self):
        self.base_url = "https://beta.portal.meep.com.br"
        self.username = "toretomal@icloud.com"
        self.password = "10041210Cl@"
        self.mapped_routes = {}
        self.api_endpoints = []
        
    async def login(self, page):
        """Fazer login no sistema MEEP"""
        print("🔐 Fazendo login no MEEP...")
        await page.goto(self.base_url)
        await page.wait_for_load_state("networkidle")
        
        # Procurar campos de login
        await page.fill('input[type="email"], input[name="email"], input[name="username"], #email', self.username)
        await page.fill('input[type="password"], input[name="password"], #password', self.password)
        
        # Clicar no botão de login
        await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")')
        
        # Aguardar redirecionamento
        await page.wait_for_load_state("networkidle")
        print("✅ Login realizado com sucesso!")
        
    async def capture_api_calls(self, page):
        """Capturar chamadas de API"""
        async def handle_response(response):
            if "/api/" in response.url or "graphql" in response.url:
                endpoint_info = {
                    "url": response.url,
                    "method": response.request.method,
                    "status": response.status,
                    "timestamp": datetime.now().isoformat()
                }
                self.api_endpoints.append(endpoint_info)
                print(f"📡 API capturada: {response.request.method} {response.url}")
        
        page.on("response", handle_response)
        
    async def map_menu_structure(self, page):
        """Mapear estrutura completa do menu"""
        print("\n🗺️ Mapeando estrutura do menu...")
        
        menu_structure = {
            "Dashboard": {
                "Geral": [],
                "Favoritos": [],
                "Evento/Caixa": {
                    "Geral": [],
                    "IA": []
                }
            },
            "Clientes": {
                "Informações dos clientes": [],
                "Categoria de clientes": [],
                "Listagem de clientes": [],
                "Pesquisa de satisfação": []
            },
            "Equipe": {
                "Colaboradores": [],
                "Cargos": []
            },
            "Cardápio": {
                "Cardápios": []
            },
            "Gestão de venda": {
                "Soluções Online": [],
                "Ingressos": []
            },
            "Relatórios": {
                "Venda": [],
                "Cartões": [],
                "Caixa": [],
                "Ficha": [],
                "Gerencial": [],
                "Financeiro": []
            },
            "Gestão de estoque": {
                "Cadastros": [],
                "Central de lançamento": [],
                "Estoque": {
                    "Inventário": [],
                    "Posição": [],
                    "Entrada": [],
                    "Saída": [],
                    "Motivo": []
                }
            },
            "PDV": {
                "Perfil": [],
                "Impressoras": [],
                "Impressoras inteligentes": [],
                "Equipamentos": [],
                "Operador": []
            },
            "Pedidos": {
                "Gestor de pedidos": []
            },
            "Financeiro": {
                "Conta digital": [],
                "Permutas": [],
                "Antecipação de Recebíveis": [],
                "Taxas": [],
                "Direcionamento de transações": [],
                "Contas bancárias": [],
                "Link de pagamento": [],
                "Forma de pagamento": [],
                "Fatura": [],
                "Split": [],
                "Estorno de transações": []
            },
            "Mapa da operação": {
                "Contas e bloqueios": [],
                "Cadastro de mesas": [],
                "Pré-ativação de cartões": [],
                "Mapa de comandas": [],
                "Grupo de cartões": [],
                "Cadastro de loja": []
            },
            "Marketing": {
                "Fidelidade": [],
                "CRM": [],
                "Desconto - Lista de convidados": [],
                "Cupons de desconto": [],
                "Campanhas": [],
                "Promoção": []
            },
            "BI": [],
            "Sistema ERP": [],
            "Automação": [],
            "Integração": []
        }
        
        # Navegar por cada seção
        for main_menu, submenus in menu_structure.items():
            try:
                print(f"\n📂 Analisando módulo: {main_menu}")
                
                # Tentar clicar no menu principal
                menu_selector = f'text={main_menu}, :text("{main_menu}"), [aria-label="{main_menu}"]'
                if await page.locator(menu_selector).count() > 0:
                    await page.click(menu_selector, timeout=5000)
                    await page.wait_for_load_state("networkidle")
                    
                    # Capturar URL e estrutura
                    current_url = page.url
                    self.mapped_routes[main_menu] = {
                        "url": current_url,
                        "submenus": {}
                    }
                    
                    # Processar submenus
                    if isinstance(submenus, dict):
                        for submenu, items in submenus.items():
                            submenu_selector = f'text={submenu}'
                            if await page.locator(submenu_selector).count() > 0:
                                await page.click(submenu_selector, timeout=3000)
                                await page.wait_for_load_state("networkidle")
                                
                                sub_url = page.url
                                self.mapped_routes[main_menu]["submenus"][submenu] = {
                                    "url": sub_url
                                }
                                print(f"  ✓ {submenu}: {sub_url}")
                                
            except Exception as e:
                print(f"  ⚠️ Erro ao mapear {main_menu}: {str(e)}")
                continue
                
        return menu_structure
        
    async def analyze_page_structure(self, page):
        """Analisar estrutura de uma página"""
        # Capturar formulários
        forms = await page.locator("form").all()
        
        # Capturar tabelas
        tables = await page.locator("table").all()
        
        # Capturar botões de ação
        buttons = await page.locator("button").all()
        
        return {
            "forms_count": len(forms),
            "tables_count": len(tables),
            "buttons_count": len(buttons)
        }
        
    async def run(self):
        """Executar mapeamento completo"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            # Configurar captura de API
            await self.capture_api_calls(page)
            
            try:
                # Fazer login
                await self.login(page)
                
                # Aguardar dashboard carregar
                await asyncio.sleep(3)
                
                # Mapear estrutura do menu
                menu_structure = await self.map_menu_structure(page)
                
                # Salvar resultados
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "base_url": self.base_url,
                    "menu_structure": menu_structure,
                    "mapped_routes": self.mapped_routes,
                    "api_endpoints": self.api_endpoints
                }
                
                with open("meep_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                    
                print("\n✅ Análise completa salva em meep_analysis.json")
                
            except Exception as e:
                print(f"❌ Erro durante análise: {str(e)}")
                
            finally:
                await browser.close()

if __name__ == "__main__":
    mapper = MEEPMapper()
    asyncio.run(mapper.run())