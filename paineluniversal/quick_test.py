#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO DE FUNCIONALIDADES
================================

Testa rapidamente todas as funcionalidades sem interferir com o servidor.

Autor: Agente de Desenvolvimento
Data: 2024
"""

import requests
import json
import sys
from datetime import datetime

class QuickFunctionalTest:
    """Teste rápido de funcionalidades"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 5
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_failures": [],
            "warnings": [],
            "backend_functional": False,
            "endpoints_tested": []
        }
        
        print("=== TESTE RAPIDO DE FUNCIONALIDADES ===")
        print(f"Horario: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def test_health(self):
        """Testar saúde do sistema"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=3)
            
            if response.status_code == 200:
                print("✅ Backend: FUNCIONANDO")
                self.results["backend_functional"] = True
                self.results["tests_passed"] += 1
                return True
            else:
                print(f"❌ Backend: PROBLEMA (Status {response.status_code})")
                self.results["tests_failed"] += 1
                self.results["critical_failures"].append("Backend não responde corretamente")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Backend: OFFLINE")
            self.results["tests_failed"] += 1
            self.results["critical_failures"].append("Backend offline")
            return False
        except Exception as e:
            print(f"❌ Backend: ERRO - {str(e)}")
            self.results["tests_failed"] += 1
            self.results["critical_failures"].append(f"Erro de conectividade: {str(e)}")
            return False
    
    def test_key_endpoints(self):
        """Testar endpoints principais"""
        if not self.results["backend_functional"]:
            print("⏭️  Pulando testes de endpoints (backend offline)")
            return
        
        endpoints = [
            {"url": "/api/usuarios", "name": "Usuários", "expect_auth": True},
            {"url": "/api/eventos", "name": "Eventos", "expect_auth": True},
            {"url": "/api/produtos", "name": "Produtos", "expect_auth": True},
            {"url": "/docs", "name": "Documentação", "expect_auth": False},
            {"url": "/api/dashboard/stats", "name": "Dashboard", "expect_auth": True}
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint['url']}", timeout=3)
                
                # Aceitar 401 para endpoints que precisam autenticação
                if endpoint['expect_auth'] and response.status_code == 401:
                    print(f"✅ {endpoint['name']}: REQUER AUTENTICAÇÃO (OK)")
                    self.results["tests_passed"] += 1
                    self.results["endpoints_tested"].append(endpoint['name'])
                elif not endpoint['expect_auth'] and response.status_code == 200:
                    print(f"✅ {endpoint['name']}: FUNCIONANDO")
                    self.results["tests_passed"] += 1
                    self.results["endpoints_tested"].append(endpoint['name'])
                elif response.status_code < 500:
                    print(f"⚠️  {endpoint['name']}: PARCIAL (Status {response.status_code})")
                    self.results["tests_passed"] += 1
                    self.results["warnings"].append(f"{endpoint['name']} retornou {response.status_code}")
                    self.results["endpoints_tested"].append(endpoint['name'])
                else:
                    print(f"❌ {endpoint['name']}: ERRO (Status {response.status_code})")
                    self.results["tests_failed"] += 1
                    self.results["critical_failures"].append(f"{endpoint['name']} falhou com {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint['name']}: FALHOU - {str(e)[:50]}")
                self.results["tests_failed"] += 1
                self.results["critical_failures"].append(f"{endpoint['name']} exception: {str(e)[:50]}")
    
    def test_authentication_flow(self):
        """Testar fluxo de autenticação"""
        if not self.results["backend_functional"]:
            print("⏭️  Pulando teste de autenticação (backend offline)")
            return
        
        try:
            # Tentar login
            login_data = {"username": "admin", "password": "admin123"}
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("✅ Autenticação: JWT FUNCIONANDO")
                    self.results["tests_passed"] += 1
                    
                    # Testar acesso autenticado
                    headers = {"Authorization": f"Bearer {data['access_token']}"}
                    auth_response = self.session.get(f"{self.base_url}/api/usuarios", headers=headers, timeout=3)
                    
                    if auth_response.status_code == 200:
                        print("✅ Acesso Autenticado: FUNCIONANDO")
                        self.results["tests_passed"] += 1
                    else:
                        print(f"⚠️  Acesso Autenticado: PROBLEMA (Status {auth_response.status_code})")
                        self.results["warnings"].append("Token válido mas acesso com problema")
                else:
                    print("❌ Autenticação: TOKEN NÃO RETORNADO")
                    self.results["tests_failed"] += 1
                    self.results["critical_failures"].append("Token JWT não retornado no login")
            else:
                print(f"❌ Autenticação: FALHA (Status {response.status_code})")
                self.results["tests_failed"] += 1
                if response.status_code == 401:
                    self.results["critical_failures"].append("Credenciais admin incorretas")
                else:
                    self.results["critical_failures"].append(f"Login falhou com status {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Autenticação: ERRO - {str(e)[:50]}")
            self.results["tests_failed"] += 1
            self.results["critical_failures"].append(f"Erro na autenticação: {str(e)[:50]}")
    
    def check_migrations_needed(self):
        """Verificar se há migrações pendentes"""
        try:
            from pathlib import Path
            migration_files = list(Path(".").glob("*migration*.py"))
            
            if migration_files:
                print(f"⚠️  Migrações: {len(migration_files)} SCRIPTS PENDENTES")
                self.results["warnings"].append(f"{len(migration_files)} scripts de migração encontrados")
                
                # Listar alguns arquivos
                for i, file in enumerate(migration_files[:3]):
                    print(f"   - {file.name}")
                    
                if len(migration_files) > 3:
                    print(f"   ... e mais {len(migration_files) - 3}")
            else:
                print("✅ Migrações: NENHUMA PENDENTE")
                self.results["tests_passed"] += 1
                
        except Exception as e:
            print(f"⚠️  Migrações: ERRO AO VERIFICAR - {str(e)[:50]}")
            self.results["warnings"].append("Não foi possível verificar migrações")
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("Executando testes...\n")
        
        # Testes principais
        self.test_health()
        self.test_key_endpoints()
        self.test_authentication_flow()
        self.check_migrations_needed()
        
        # Relatório final
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Gerar resumo final"""
        print("\n" + "="*50)
        print("RESUMO DOS TESTES")
        print("="*50)
        
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Testes passaram: {self.results['tests_passed']}")
        print(f"❌ Testes falharam: {self.results['tests_failed']}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.results["backend_functional"]:
            print("🟢 Backend: FUNCIONANDO")
        else:
            print("🔴 Backend: PROBLEMA")
        
        if self.results["endpoints_tested"]:
            print(f"🔗 Endpoints testados: {len(self.results['endpoints_tested'])}")
        
        # Problemas críticos
        if self.results["critical_failures"]:
            print(f"\n🚨 PROBLEMAS CRÍTICOS ({len(self.results['critical_failures'])}):")
            for i, failure in enumerate(self.results["critical_failures"], 1):
                print(f"   {i}. {failure}")
        
        # Avisos
        if self.results["warnings"]:
            print(f"\n⚠️  AVISOS ({len(self.results['warnings'])}):")
            for i, warning in enumerate(self.results["warnings"], 1):
                print(f"   {i}. {warning}")
        
        # Veredito
        if len(self.results["critical_failures"]) == 0:
            print("\n🎉 VEREDITO: Sistema funcionando corretamente!")
            print("="*50)
            return 0
        elif len(self.results["critical_failures"]) <= 2:
            print("\n⚠️  VEREDITO: Sistema funcional com pequenos problemas")
            print("="*50)
            return 1
        else:
            print("\n🚨 VEREDITO: Sistema com problemas graves")
            print("="*50)
            return 2

def main():
    """Função principal"""
    tester = QuickFunctionalTest()
    
    try:
        results = tester.run_all_tests()
        
        # Salvar resultado
        filename = f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {filename}")
        
        # Retornar código de saída
        if len(results["critical_failures"]) == 0:
            return 0
        elif len(results["critical_failures"]) <= 2:
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"\n🚨 ERRO DURANTE TESTES: {str(e)}")
        return 3

if __name__ == "__main__":
    exit(main())
