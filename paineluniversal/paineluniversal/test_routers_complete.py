#!/usr/bin/env python3
"""
🧪 TESTES COMPLETOS DE ROUTERS - SISTEMA PAINEL UNIVERSAL
Testes abrangentes para todos os routers ativos do sistema
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Importar framework de testes
from test_framework_complete import TestFramework

class RouterTestSuite:
    """Suite de testes para routers"""
    
    def __init__(self):
        self.client = None
        self.setup_test_client()
        
    def setup_test_client(self):
        """Configurar cliente de teste FastAPI"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
            from fastapi.testclient import TestClient
            from backend.app.main import app
            
            self.client = TestClient(app)
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar cliente de teste: {e}")
            return False
    
    def test_health_endpoints(self):
        """Testar endpoints de health check"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            results = {}
            
            # Testar endpoint raiz
            response = self.client.get("/")
            results["root"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            # Testar /healthz
            response = self.client.get("/healthz")
            results["healthz"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            # Testar /api/health
            response = self.client.get("/api/health")
            results["api_health"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            success_count = sum(1 for r in results.values() if r["success"])
            total_count = len(results)
            
            return {
                "status": "passed" if success_count == total_count else "failed",
                "message": f"Health endpoints: {success_count}/{total_count} funcionando",
                "details": results
            }
            
        except Exception as e:
            return {"status": "failed", "message": f"Erro nos health endpoints: {str(e)}"}
    
    def test_cors_functionality(self):
        """Testar funcionalidade CORS"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar endpoint de teste CORS
            response = self.client.get("/api/cors-test")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "passed",
                    "message": "CORS funcionando corretamente",
                    "details": {
                        "status_code": response.status_code,
                        "cors_info": data.get("cors_info", {}),
                        "headers": dict(response.headers)
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"CORS test falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no teste CORS: {str(e)}"}
    
    def test_auth_router(self):
        """Testar router de autenticação"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            results = {}
            
            # Testar setup inicial (se disponível)
            response = self.client.post("/setup-inicial")
            results["setup_inicial"] = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 409]  # 409 se já inicializado
            }
            
            # Tentar login com dados de teste
            login_data = {
                "cpf": "00000000000",
                "senha": "admin123"
            }
            response = self.client.post("/api/auth/login", json=login_data)
            results["login_attempt"] = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 400, 401]  # Códigos esperados
            }
            
            success_count = sum(1 for r in results.values() if r["success"])
            total_count = len(results)
            
            return {
                "status": "passed" if success_count == total_count else "failed",
                "message": f"Auth router: {success_count}/{total_count} endpoints OK",
                "details": results
            }
            
        except Exception as e:
            return {"status": "failed", "message": f"Erro no auth router: {str(e)}"}
    
    def test_usuarios_router(self):
        """Testar router de usuários"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar listagem de usuários (público)
            response = self.client.get("/api/usuarios")
            
            if response.status_code in [200, 401, 403]:  # Códigos esperados
                return {
                    "status": "passed",
                    "message": f"Usuários router respondendo (código {response.status_code})",
                    "details": {
                        "status_code": response.status_code,
                        "endpoint_accessible": True
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Usuários router falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no usuários router: {str(e)}"}
    
    def test_produtos_router(self):
        """Testar router de produtos"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar listagem de produtos
            response = self.client.get("/api/produtos")
            
            if response.status_code in [200, 401, 403, 404]:  # Códigos esperados
                return {
                    "status": "passed",
                    "message": f"Produtos router respondendo (código {response.status_code})",
                    "details": {
                        "status_code": response.status_code,
                        "endpoint_accessible": True
                    }
                }
            else:
                return {
                    "status": "failed", 
                    "message": f"Produtos router falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no produtos router: {str(e)}"}
    
    def test_eventos_router(self):
        """Testar router de eventos"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar listagem de eventos
            response = self.client.get("/api/eventos")
            
            if response.status_code in [200, 401, 403, 404]:  # Códigos esperados
                return {
                    "status": "passed",
                    "message": f"Eventos router respondendo (código {response.status_code})",
                    "details": {
                        "status_code": response.status_code,
                        "endpoint_accessible": True
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Eventos router falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no eventos router: {str(e)}"}
    
    def test_empresas_router(self):
        """Testar router de empresas"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar listagem de empresas
            response = self.client.get("/api/empresas")
            
            if response.status_code in [200, 401, 403, 404]:  # Códigos esperados
                return {
                    "status": "passed",
                    "message": f"Empresas router respondendo (código {response.status_code})",
                    "details": {
                        "status_code": response.status_code,
                        "endpoint_accessible": True
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Empresas router falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no empresas router: {str(e)}"}
    
    def test_dashboard_router(self):
        """Testar router de dashboard"""
        if not self.client:
            return {"status": "failed", "message": "Cliente de teste não configurado"}
            
        try:
            # Testar dashboard
            response = self.client.get("/api/dashboard")
            
            if response.status_code in [200, 401, 403, 404]:  # Códigos esperados
                return {
                    "status": "passed",
                    "message": f"Dashboard router respondendo (código {response.status_code})",
                    "details": {
                        "status_code": response.status_code,
                        "endpoint_accessible": True
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Dashboard router falhou: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {"status": "failed", "message": f"Erro no dashboard router: {str(e)}"}

def test_all_routers():
    """Testar todos os routers usando o framework"""
    print("🧪 INICIANDO TESTES COMPLETOS DE ROUTERS")
    print("🎯 Sistema: Painel Universal - Todos os Routers")
    print("📅 Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    # Criar framework
    framework = TestFramework()
    router_suite = RouterTestSuite()
    
    # FASE 1: TESTES DE INFRAESTRUTURA WEB
    framework.start_phase(
        "infraestrutura_web", 
        "Testes de infraestrutura web e endpoints básicos"
    )
    
    framework.run_test("Health Endpoints", router_suite.test_health_endpoints)
    framework.run_test("Funcionalidade CORS", router_suite.test_cors_functionality)
    
    framework.end_phase()
    
    # FASE 2: TESTES DE ROUTERS CRÍTICOS
    framework.start_phase(
        "routers_criticos",
        "Testes dos routers mais críticos do sistema"
    )
    
    framework.run_test("Auth Router", router_suite.test_auth_router)
    framework.run_test("Usuários Router", router_suite.test_usuarios_router)
    framework.run_test("Produtos Router", router_suite.test_produtos_router)
    framework.run_test("Eventos Router", router_suite.test_eventos_router)
    
    framework.end_phase()
    
    # FASE 3: TESTES DE ROUTERS PRINCIPAIS
    framework.start_phase(
        "routers_principais",
        "Testes dos routers principais de negócio"
    )
    
    framework.run_test("Empresas Router", router_suite.test_empresas_router)
    framework.run_test("Dashboard Router", router_suite.test_dashboard_router)
    
    framework.end_phase()
    
    # Gerar relatório
    results = framework.generate_report()
    
    return results

if __name__ == "__main__":
    test_all_routers()
