"""
Teste de Compatibilidade com MEEP
"""
import requests
import json
from typing import Dict, List

class MEEPCompatibilityTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_endpoint(self, method: str, path: str, expected_status: int = 200):
        """Testar um endpoint específico"""
        self.total_tests += 1
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json={})
            else:
                response = requests.request(method, url)
                
            if response.status_code == expected_status:
                self.passed_tests += 1
                status = "PASS"
            else:
                status = "FAIL"
                
            result = {
                "endpoint": f"{method} {path}",
                "status": status,
                "status_code": response.status_code,
                "expected": expected_status
            }
            
        except Exception as e:
            status = "ERROR"
            result = {
                "endpoint": f"{method} {path}",
                "status": status,
                "error": str(e)
            }
            
        self.test_results.append(result)
        print(f"[{status}] {method} {path}")
        return result
        
    def run_all_tests(self):
        """Executar todos os testes de compatibilidade"""
        print("="*60)
        print("TESTE DE COMPATIBILIDADE MEEP - SISTEMA UNICA CLUB")
        print("="*60)
        
        # Testar módulos principais
        modules_to_test = [
            # Dashboard
            ("GET", "/api/dashboard/geral"),
            ("GET", "/api/dashboard/favoritos"),
            ("GET", "/api/dashboard/metricas"),
            
            # Clientes
            ("GET", "/api/clientes"),
            ("GET", "/api/clientes/categorias"),
            ("GET", "/api/clientes/pesquisa-satisfacao"),
            
            # Equipe
            ("GET", "/api/equipe/colaboradores"),
            ("GET", "/api/equipe/cargos"),
            ("GET", "/api/equipe/permissoes"),
            
            # Cardápio
            ("GET", "/api/cardapio"),
            ("GET", "/api/cardapio/items"),
            ("GET", "/api/cardapio/categorias"),
            
            # Financeiro - Módulo completo
            ("GET", "/api/financeiro/conta-digital"),
            ("GET", "/api/financeiro/antecipacao"),
            ("GET", "/api/financeiro/split"),
            ("GET", "/api/financeiro/link-pagamento"),
            ("GET", "/api/financeiro/permutas"),
            ("GET", "/api/financeiro/taxas"),
            ("GET", "/api/financeiro/direcionamento"),
            ("GET", "/api/financeiro/contas-bancarias"),
            ("GET", "/api/financeiro/faturas"),
            ("GET", "/api/financeiro/estornos"),
            ("GET", "/api/financeiro/conciliacao"),
            ("GET", "/api/financeiro/fluxo-caixa?data_inicio=2024-01-01&data_fim=2024-12-31"),
            ("GET", "/api/financeiro/contas-pagar"),
            ("GET", "/api/financeiro/contas-receber"),
            
            # Marketing - Módulo completo
            ("GET", "/api/marketing/fidelidade"),
            ("GET", "/api/marketing/crm"),
            ("GET", "/api/marketing/lista-convidados"),
            ("GET", "/api/marketing/cupons"),
            ("GET", "/api/marketing/campanhas"),
            ("GET", "/api/marketing/promocoes"),
            ("GET", "/api/marketing/email/templates"),
            ("GET", "/api/marketing/automacao"),
            ("GET", "/api/marketing/analytics"),
            
            # PDV
            ("GET", "/api/pdv/terminais"),
            ("GET", "/api/pdv/operadores"),
            ("GET", "/api/pdv/configuracoes"),
            
            # Pedidos
            ("GET", "/api/pedidos"),
            ("GET", "/api/pedidos/fila"),
            
            # Estoque
            ("GET", "/api/estoque/produtos"),
            ("GET", "/api/estoque/inventario"),
            ("GET", "/api/estoque/movimentacoes"),
            
            # Relatórios
            ("GET", "/api/relatorios/vendas"),
            ("GET", "/api/relatorios/financeiro"),
            ("GET", "/api/relatorios/gerencial"),
            
            # BI
            ("GET", "/api/bi/dashboards"),
            ("GET", "/api/bi/metricas"),
            
            # Integrações
            ("GET", "/api/integracao/webhooks"),
            ("GET", "/api/integracao/marketplace"),
            
            # Automação
            ("GET", "/api/automacao/workflows"),
            ("GET", "/api/automacao/triggers")
        ]
        
        print("\nTestando endpoints...")
        print("-"*60)
        
        for method, path in modules_to_test:
            self.test_endpoint(method, path)
            
        # Relatório final
        print("\n" + "="*60)
        print("RELATORIO FINAL")
        print("="*60)
        print(f"Total de testes: {self.total_tests}")
        print(f"Testes aprovados: {self.passed_tests}")
        print(f"Testes falhados: {self.total_tests - self.passed_tests}")
        print(f"Taxa de sucesso: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Salvar relatório
        report = {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.total_tests - self.passed_tests,
            "success_rate": f"{(self.passed_tests/self.total_tests)*100:.1f}%",
            "test_results": self.test_results
        }
        
        with open("meep_compatibility_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print("\nRelatorio detalhado salvo em: meep_compatibility_test_report.json")
        
        # Verificar módulos críticos
        critical_modules = ["financeiro", "marketing", "clientes", "pedidos"]
        critical_status = []
        
        for module in critical_modules:
            module_tests = [r for r in self.test_results if module in r["endpoint"].lower()]
            if module_tests:
                passed = len([t for t in module_tests if t["status"] == "PASS"])
                total = len(module_tests)
                status = "OK" if passed == total else "ATENCAO"
                critical_status.append(f"  - {module.upper()}: {passed}/{total} endpoints funcionando [{status}]")
                
        if critical_status:
            print("\nStatus dos modulos criticos:")
            for status in critical_status:
                print(status)
                
        return report

if __name__ == "__main__":
    tester = MEEPCompatibilityTester()
    tester.run_all_tests()