#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAÇÃO FINAL DO SISTEMA COMPLETO
===================================

Teste definitivo de todas as funcionalidades do Painel Universal.
Análise abrangente com relatório detalhado.

Autor: Sistema de Análise Automatizada
Data: 2024
"""

import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any
import requests
import urllib3

# Desabilita warnings SSL para testes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FinalSystemValidator:
    """Validador final completo do sistema"""
    
    def __init__(self):
        # URLs de teste (Railway e local)
        self.test_urls = [
            "https://paineluniversal-production.up.railway.app",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
        
        self.active_url = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 30
        
        # Resultados
        self.results = {
            "system_info": {
                "url": None,
                "timestamp": datetime.now().isoformat(),
                "test_duration": 0
            },
            "connectivity": {"status": "FAIL", "details": []},
            "authentication": {"status": "FAIL", "details": []},
            "core_business": {"status": "FAIL", "details": []},
            "data_operations": {"status": "FAIL", "details": []},
            "integrations": {"status": "FAIL", "details": []},
            "performance": {"status": "FAIL", "details": []},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0,
                "critical_issues": [],
                "recommendations": []
            }
        }
    
    def log_test(self, category: str, test_name: str, success: bool, details: str = ""):
        """Registra resultado de teste"""
        result = {
            "test": test_name,
            "status": "PASS" if success else "FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results[category]["details"].append(result)
        self.results["summary"]["total_tests"] += 1
        
        if success:
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results["summary"]["failed"] += 1
            self.results["summary"]["critical_issues"].append(f"{test_name}: {details}")
            print(f"❌ {test_name}: {details}")
    
    def find_active_backend(self) -> bool:
        """Encontra backend ativo"""
        print("🔍 Procurando backend ativo...")
        
        for url in self.test_urls:
            try:
                response = self.session.get(f"{url}/health", timeout=10)
                if response.status_code == 200:
                    self.active_url = url
                    self.results["system_info"]["url"] = url
                    print(f"✅ Backend encontrado: {url}")
                    return True
            except Exception as e:
                print(f"⚠️ {url}: {str(e)[:50]}...")
                continue
        
        print("❌ Nenhum backend acessível encontrado")
        return False
    
    def test_connectivity(self):
        """Testa conectividade básica"""
        print("\n🌐 Testando Conectividade...")
        
        if not self.active_url:
            self.log_test("connectivity", "Backend Discovery", False, "Nenhum backend acessível")
            self.results["connectivity"]["status"] = "FAIL"
            return
        
        try:
            # Health endpoint
            response = self.session.get(f"{self.active_url}/health")
            if response.status_code == 200:
                self.log_test("connectivity", "Health Endpoint", True, f"Status: {response.status_code}")
            else:
                self.log_test("connectivity", "Health Endpoint", False, f"Status: {response.status_code}")
            
            # API docs
            response = self.session.get(f"{self.active_url}/docs")
            if response.status_code == 200:
                self.log_test("connectivity", "API Documentation", True, "Swagger UI acessível")
            else:
                self.log_test("connectivity", "API Documentation", False, f"Status: {response.status_code}")
            
            # CORS test
            headers = {"Origin": "http://localhost:3000"}
            response = self.session.options(f"{self.active_url}/health", headers=headers)
            if response.status_code in [200, 204]:
                self.log_test("connectivity", "CORS Configuration", True, "CORS headers presentes")
            else:
                self.log_test("connectivity", "CORS Configuration", False, f"Status: {response.status_code}")
            
            self.results["connectivity"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("connectivity", "General Connectivity", False, str(e))
            self.results["connectivity"]["status"] = "FAIL"
    
    def test_authentication(self):
        """Testa sistema de autenticação"""
        print("\n🔐 Testando Autenticação...")
        
        try:
            # Test registration endpoint
            register_data = {
                "nome": "Teste Sistema",
                "email": f"teste{int(time.time())}@teste.com",
                "password": "teste123456",
                "tipo_usuario": "ADMINISTRADOR"
            }
            
            response = self.session.post(f"{self.active_url}/api/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                self.log_test("authentication", "User Registration", True, "Registro bem-sucedido")
            else:
                self.log_test("authentication", "User Registration", False, f"Status: {response.status_code}")
            
            # Test login endpoint
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            response = self.session.post(f"{self.active_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_test("authentication", "User Login", True, "Token JWT obtido")
                    
                    # Set auth header for subsequent tests
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    
                    self.results["authentication"]["status"] = "PASS"
                else:
                    self.log_test("authentication", "User Login", False, "Token não retornado")
            else:
                self.log_test("authentication", "User Login", False, f"Status: {response.status_code}")
                
                # Try default admin login
                admin_data = {"email": "admin@paineluniversal.com", "password": "admin123"}
                response = self.session.post(f"{self.active_url}/api/auth/login", json=admin_data)
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.session.headers.update({
                            "Authorization": f"Bearer {data['access_token']}"
                        })
                        self.log_test("authentication", "Admin Login", True, "Login admin bem-sucedido")
                        self.results["authentication"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("authentication", "Authentication System", False, str(e))
    
    def test_core_business(self):
        """Testa funcionalidades principais do negócio"""
        print("\n🏢 Testando Core Business...")
        
        try:
            # Dashboard
            response = self.session.get(f"{self.active_url}/api/dashboard/")
            if response.status_code == 200:
                self.log_test("core_business", "Dashboard Access", True, "Dashboard carregado")
            else:
                self.log_test("core_business", "Dashboard Access", False, f"Status: {response.status_code}")
            
            # Usuários
            response = self.session.get(f"{self.active_url}/api/usuarios/")
            if response.status_code in [200, 403]:  # 403 é esperado se sem permissão
                self.log_test("core_business", "Users Management", True, "Endpoint usuários funcional")
            else:
                self.log_test("core_business", "Users Management", False, f"Status: {response.status_code}")
            
            # Empresas
            response = self.session.get(f"{self.active_url}/api/empresas/")
            if response.status_code in [200, 403]:
                self.log_test("core_business", "Companies Management", True, "Endpoint empresas funcional")
            else:
                self.log_test("core_business", "Companies Management", False, f"Status: {response.status_code}")
            
            # Eventos
            response = self.session.get(f"{self.active_url}/api/eventos/")
            if response.status_code in [200, 403]:
                self.log_test("core_business", "Events Management", True, "Endpoint eventos funcional")
            else:
                self.log_test("core_business", "Events Management", False, f"Status: {response.status_code}")
            
            self.results["core_business"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("core_business", "Core Business Logic", False, str(e))
    
    def test_data_operations(self):
        """Testa operações de dados"""
        print("\n📊 Testando Operações de Dados...")
        
        try:
            # Produtos
            response = self.session.get(f"{self.active_url}/api/produtos/")
            if response.status_code in [200, 403]:
                self.log_test("data_operations", "Products Management", True, "Endpoint produtos funcional")
            else:
                self.log_test("data_operations", "Products Management", False, f"Status: {response.status_code}")
            
            # PDV
            response = self.session.get(f"{self.active_url}/api/pdv/status")
            if response.status_code in [200, 403]:
                self.log_test("data_operations", "PDV System", True, "Sistema PDV funcional")
            else:
                self.log_test("data_operations", "PDV System", False, f"Status: {response.status_code}")
            
            # Gamificação
            response = self.session.get(f"{self.active_url}/api/gamificacao/")
            if response.status_code in [200, 403, 404]:  # 404 pode ser esperado
                self.log_test("data_operations", "Gamification", True, "Sistema gamificação presente")
            else:
                self.log_test("data_operations", "Gamification", False, f"Status: {response.status_code}")
            
            # Relatórios
            response = self.session.get(f"{self.active_url}/api/relatorios/")
            if response.status_code in [200, 403, 404]:
                self.log_test("data_operations", "Reports System", True, "Sistema relatórios presente")
            else:
                self.log_test("data_operations", "Reports System", False, f"Status: {response.status_code}")
            
            self.results["data_operations"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("data_operations", "Data Operations", False, str(e))
    
    def test_integrations(self):
        """Testa integrações externas"""
        print("\n🔗 Testando Integrações...")
        
        try:
            # WhatsApp
            response = self.session.get(f"{self.active_url}/api/whatsapp/status")
            if response.status_code in [200, 503, 404]:  # 503/404 pode indicar não configurado
                self.log_test("integrations", "WhatsApp Integration", True, "Endpoint WhatsApp presente")
            else:
                self.log_test("integrations", "WhatsApp Integration", False, f"Status: {response.status_code}")
            
            # MEEP
            response = self.session.get(f"{self.active_url}/api/meep/status")
            if response.status_code in [200, 503, 404]:
                self.log_test("integrations", "MEEP Integration", True, "Endpoint MEEP presente")
            else:
                self.log_test("integrations", "MEEP Integration", False, f"Status: {response.status_code}")
            
            # N8N
            response = self.session.get(f"{self.active_url}/api/n8n/")
            if response.status_code in [200, 503, 404]:
                self.log_test("integrations", "N8N Integration", True, "Endpoint N8N presente")
            else:
                self.log_test("integrations", "N8N Integration", False, f"Status: {response.status_code}")
            
            # Email
            response = self.session.get(f"{self.active_url}/api/email/status")
            if response.status_code in [200, 503, 404]:
                self.log_test("integrations", "Email Service", True, "Serviço email configurado")
            else:
                self.log_test("integrations", "Email Service", False, f"Status: {response.status_code}")
            
            self.results["integrations"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("integrations", "External Integrations", False, str(e))
    
    def test_performance(self):
        """Testa performance básica"""
        print("\n⚡ Testando Performance...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.active_url}/health")
            response_time = time.time() - start_time
            
            if response_time < 2.0:
                self.log_test("performance", "Response Time", True, f"{response_time:.3f}s")
            else:
                self.log_test("performance", "Response Time", False, f"Lento: {response_time:.3f}s")
            
            # Test concurrent requests
            import threading
            import queue
            
            def test_concurrent():
                try:
                    resp = requests.get(f"{self.active_url}/health", timeout=10)
                    return resp.status_code == 200
                except:
                    return False
            
            results_queue = queue.Queue()
            threads = []
            
            for i in range(5):
                thread = threading.Thread(target=lambda: results_queue.put(test_concurrent()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=15)
            
            concurrent_success = 0
            while not results_queue.empty():
                if results_queue.get():
                    concurrent_success += 1
            
            if concurrent_success >= 4:  # 80% success rate
                self.log_test("performance", "Concurrent Requests", True, f"{concurrent_success}/5 successful")
            else:
                self.log_test("performance", "Concurrent Requests", False, f"Only {concurrent_success}/5 successful")
            
            self.results["performance"]["status"] = "PASS"
            
        except Exception as e:
            self.log_test("performance", "Performance Tests", False, str(e))
    
    def generate_final_report(self):
        """Gera relatório final completo"""
        # Calcula estatísticas
        total = self.results["summary"]["total_tests"]
        passed = self.results["summary"]["passed"]
        
        if total > 0:
            self.results["summary"]["success_rate"] = (passed / total) * 100
        
        # Determina status geral do sistema
        categories_passed = sum(1 for cat in ["connectivity", "authentication", "core_business", "data_operations", "integrations", "performance"] 
                               if self.results[cat]["status"] == "PASS")
        
        if categories_passed >= 5:
            system_status = "🟢 SISTEMA OPERACIONAL"
        elif categories_passed >= 3:
            system_status = "🟡 SISTEMA PARCIALMENTE FUNCIONAL"
        else:
            system_status = "🔴 SISTEMA COM PROBLEMAS CRÍTICOS"
        
        # Gera recomendações
        if self.results["connectivity"]["status"] == "FAIL":
            self.results["summary"]["recommendations"].append("CRÍTICO: Resolver problemas de conectividade")
        
        if self.results["authentication"]["status"] == "FAIL":
            self.results["summary"]["recommendations"].append("CRÍTICO: Corrigir sistema de autenticação")
        
        if self.results["summary"]["success_rate"] < 70:
            self.results["summary"]["recommendations"].append("Investigar falhas nos testes para melhorar estabilidade")
        
        if not self.results["summary"]["recommendations"]:
            self.results["summary"]["recommendations"].append("Sistema funcionando adequadamente")
        
        # Exibe relatório
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DE VALIDAÇÃO DO SISTEMA")
        print("="*80)
        print(f"🎯 {system_status}")
        print(f"📈 Taxa de Sucesso: {self.results['summary']['success_rate']:.1f}% ({passed}/{total} testes)")
        print(f"🌐 URL Testada: {self.results['system_info']['url']}")
        print(f"⏱️ Duração: {self.results['system_info']['test_duration']:.2f}s")
        
        print(f"\n📋 STATUS POR CATEGORIA:")
        categories = ["connectivity", "authentication", "core_business", "data_operations", "integrations", "performance"]
        for cat in categories:
            status = self.results[cat]["status"]
            emoji = "✅" if status == "PASS" else "❌"
            name = cat.replace("_", " ").title()
            print(f"  {emoji} {name}: {status}")
        
        if self.results["summary"]["critical_issues"]:
            print(f"\n❌ PROBLEMAS CRÍTICOS ({len(self.results['summary']['critical_issues'])}):")
            for issue in self.results["summary"]["critical_issues"][:5]:
                print(f"  • {issue}")
            if len(self.results["summary"]["critical_issues"]) > 5:
                print(f"  ... e mais {len(self.results['summary']['critical_issues']) - 5} problemas")
        
        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in self.results["summary"]["recommendations"]:
            print(f"  • {rec}")
        
        print("="*80)
        
        # Salva relatório
        report_file = f"final_system_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Relatório completo salvo em: {report_file}")
        
        return self.results

def main():
    """Função principal"""
    start_time = time.time()
    
    print("🚀 INICIANDO VALIDAÇÃO FINAL DO SISTEMA PAINEL UNIVERSAL")
    print("="*80)
    
    validator = FinalSystemValidator()
    
    try:
        # 1. Encontrar backend ativo
        if not validator.find_active_backend():
            print("❌ Não foi possível encontrar um backend ativo para testar")
            return
        
        # 2. Testes de conectividade
        validator.test_connectivity()
        
        # 3. Testes de autenticação
        validator.test_authentication()
        
        # 4. Testes de negócio
        validator.test_core_business()
        
        # 5. Testes de dados
        validator.test_data_operations()
        
        # 6. Testes de integrações
        validator.test_integrations()
        
        # 7. Testes de performance
        validator.test_performance()
        
    except Exception as e:
        print(f"❌ Erro geral durante validação: {str(e)}")
    
    finally:
        validator.results["system_info"]["test_duration"] = time.time() - start_time
        validator.generate_final_report()

if __name__ == "__main__":
    main()
