#!/usr/bin/env python3
"""
🧪 FRAMEWORK DE TESTES CORRETO V2.0 - Com endpoints exatos
Sistema de testes abrangente usando endpoints reais mapeados
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# Importar framework base
from test_framework_complete import TestFramework

class CorrectEndpointTestSuite:
    """Suite de testes com endpoints corretos"""
    
    def __init__(self):
        self.client = None
        self.endpoint_map = self.load_endpoint_map()
        self.setup_test_client()
        
    def load_endpoint_map(self):
        """Carregar mapeamento de endpoints"""
        try:
            # Procurar arquivo mais recente de endpoint_map
            files = [f for f in os.listdir('.') if f.startswith('endpoint_map_report_')]
            if files:
                latest_file = max(files)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar endpoint map: {e}")
        return {"endpoint_summary": []}
        
    def setup_test_client(self):
        """Configurar cliente de teste FastAPI"""
        try:
            from fastapi.testclient import TestClient
            from app.main import app
            
            self.client = TestClient(app)
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar cliente de teste: {e}")
            return False
    
    def get_endpoints_by_method(self, method: str) -> List[str]:
        """Obter todos os endpoints de um método específico"""
        endpoints = []
        for endpoint in self.endpoint_map.get("endpoint_summary", []):
            if endpoint["method"] == method.upper():
                endpoints.append(endpoint["full_url"])
        return sorted(set(endpoints))
    
    def test_health_endpoints_correct(self):
        """Testar endpoints de health com caminhos corretos"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            results = {}
            
            # Endpoints de health conhecidos
            health_endpoints = ["/", "/healthz", "/api/health"]
            
            for endpoint in health_endpoints:
                try:
                    response = self.client.get(endpoint)
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_size": len(response.content)
                    }
                except Exception as e:
                    results[endpoint] = {
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    }
            
            success_count = sum(1 for r in results.values() if r.get("success", False))
            total_count = len(results)
            
            return {
                "status": "passed" if success_count > 0 else "failed",
                "message": f"Health endpoints: {success_count}/{total_count} funcionando",
                "details": results,
                "success_rate": success_count / total_count if total_count > 0 else 0
            }
            
        except Exception as e:
            return {"status": "failed", "message": f"Erro nos health endpoints: {e}"}
    
    def test_get_endpoints_systematic(self):
        """Testar sistematicamente todos os endpoints GET"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        get_endpoints = self.get_endpoints_by_method("GET")
        results = {}
        
        print(f"🔍 Testando {len(get_endpoints)} endpoints GET...")
        
        for endpoint in get_endpoints:
            try:
                # Pular endpoints que precisam de parâmetros específicos
                if "{" in endpoint:
                    results[endpoint] = {
                        "status_code": 0,
                        "success": False,
                        "skipped": True,
                        "reason": "Endpoint requer parâmetros"
                    }
                    continue
                
                response = self.client.get(endpoint)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 401, 403],  # 401/403 são esperados sem auth
                    "requires_auth": response.status_code in [401, 403],
                    "response_size": len(response.content)
                }
                
            except Exception as e:
                results[endpoint] = {
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Calcular estatísticas
        total = len(results)
        success = sum(1 for r in results.values() if r.get("success", False))
        skipped = sum(1 for r in results.values() if r.get("skipped", False))
        requires_auth = sum(1 for r in results.values() if r.get("requires_auth", False))
        
        return {
            "status": "passed" if success > 0 else "failed",
            "message": f"GET endpoints: {success}/{total} funcionando",
            "details": results,
            "statistics": {
                "total": total,
                "success": success,
                "skipped": skipped,
                "requires_auth": requires_auth,
                "success_rate": success / total if total > 0 else 0
            }
        }
    
    def test_router_specific_endpoints(self):
        """Testar endpoints específicos de cada router"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        # Endpoints específicos para testar (sem parâmetros)
        specific_tests = {
            "usuarios": "/api/usuarios/",
            "produtos": "/api/produtos/",
            "eventos": "/api/eventos/",
            "empresas": "/api/empresas/",
            "dashboard": "/api/dashboard/resumo",
            "listas": "/api/listas/",
            "transacoes": "/api/transacoes/",
            "formas_pagamento": "/api/formas-pagamento/"
        }
        
        results = {}
        
        for router_name, endpoint in specific_tests.items():
            try:
                response = self.client.get(endpoint)
                results[router_name] = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 401, 403],
                    "requires_auth": response.status_code in [401, 403],
                    "method_allowed": response.status_code != 405
                }
                
            except Exception as e:
                results[router_name] = {
                    "endpoint": endpoint,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
        
        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)
        
        return {
            "status": "passed" if success_count > 0 else "failed",
            "message": f"Router endpoints: {success_count}/{total_count} funcionando",
            "details": results,
            "success_rate": success_count / total_count if total_count > 0 else 0
        }

def run_correct_endpoint_tests():
    """Executar testes com endpoints corretos"""
    framework = TestFramework()
    test_suite = CorrectEndpointTestSuite()
    
    print("🧪 INICIANDO TESTES COM ENDPOINTS CORRETOS")
    print("🎯 Sistema: Painel Universal - Endpoints Mapeados")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar se cliente foi configurado
    if not test_suite.client:
        print("❌ Não foi possível configurar cliente de teste")
        return
    
    # FASE 1: Health Endpoints
    framework.start_phase("health_corretos", "Health endpoints com caminhos corretos")
    
    result = test_suite.test_health_endpoints_correct()
    framework.run_test("Health Endpoints Corretos", 
                      lambda *args: result,
                      "Testar endpoints de health com caminhos exatos")
    
    # FASE 2: Endpoints GET Sistemáticos
    framework.start_phase("get_sistematico", "Teste sistemático de todos os endpoints GET")
    
    result = test_suite.test_get_endpoints_systematic()
    framework.run_test("Endpoints GET Sistemáticos", 
                      lambda *args: result,
                      "Testar todos os endpoints GET mapeados")
    
    # FASE 3: Endpoints Específicos de Routers
    framework.start_phase("routers_especificos", "Endpoints específicos de cada router")
    
    result = test_suite.test_router_specific_endpoints()
    framework.run_test("Router Endpoints Específicos", 
                      lambda *args: result,
                      "Testar endpoints principais de cada router")
    
    # Gerar relatório final
    framework.generate_report()

if __name__ == "__main__":
    run_correct_endpoint_tests()
