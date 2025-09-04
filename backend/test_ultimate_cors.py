#!/usr/bin/env python3
"""
Teste Definitivo CORS - Valida todas as funcionalidades e cenários
"""

import requests
import json
import time
import sys

class CORSUltimateTest:
    def __init__(self):
        self.backend_url = "https://backend-painel-universal-production.up.railway.app"
        self.frontend_origin = "https://frontend-painel-universal-production.up.railway.app"
        self.test_results = []
        self.success_count = 0
        self.total_tests = 0
    
    def log_result(self, test_name, success, details=""):
        """Registra resultado do teste"""
        self.total_tests += 1
        if success:
            self.success_count += 1
            status = "PASS"
        else:
            status = "FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def test_basic_cors_headers(self):
        """Teste 1: Headers CORS básicos"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", 
                                  headers={'Origin': self.frontend_origin},
                                  timeout=10)
            
            cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
            required_headers = ['access-control-allow-origin']
            
            has_required = all(any(h.lower() == rh for h in cors_headers) for rh in required_headers)
            
            if has_required and response.status_code == 200:
                self.log_result("Basic CORS Headers", True, f"Found: {cors_headers}")
            else:
                self.log_result("Basic CORS Headers", False, f"Missing headers or bad status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Basic CORS Headers", False, f"Exception: {str(e)}")
    
    def test_preflight_options(self):
        """Teste 2: Preflight OPTIONS"""
        try:
            headers = {
                'Origin': self.frontend_origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            response = requests.options(f"{self.backend_url}/api/auth/login", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
                self.log_result("Preflight OPTIONS", True, f"Status: {response.status_code}, Headers: {len(cors_headers)}")
            else:
                self.log_result("Preflight OPTIONS", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Preflight OPTIONS", False, f"Exception: {str(e)}")
    
    def test_post_with_cors(self):
        """Teste 3: POST com CORS"""
        try:
            headers = {
                'Origin': self.frontend_origin,
                'Content-Type': 'application/json'
            }
            data = {"cpf": "test", "senha": "test"}  # Dados inválidos propositalmente
            
            response = requests.post(f"{self.backend_url}/api/auth/login",
                                   json=data, headers=headers, timeout=10)
            
            cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
            
            # Esperamos 401 (credenciais inválidas) com headers CORS
            if response.status_code == 401 and len(cors_headers) > 0:
                self.log_result("POST with CORS", True, f"Status: {response.status_code}, CORS: {len(cors_headers)} headers")
            else:
                self.log_result("POST with CORS", False, f"Status: {response.status_code}, CORS headers: {len(cors_headers)}")
                
        except Exception as e:
            self.log_result("POST with CORS", False, f"Exception: {str(e)}")
    
    def test_cors_test_endpoint(self):
        """Teste 4: Endpoint de teste CORS avançado"""
        try:
            response = requests.get(f"{self.backend_url}/api/cors-test", 
                                  headers={'Origin': self.frontend_origin}, 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "Ultimate Protection" in data.get("message", ""):
                    self.log_result("CORS Test Endpoint", True, f"Ultimate protection active")
                else:
                    self.log_result("CORS Test Endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_result("CORS Test Endpoint", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("CORS Test Endpoint", False, f"Exception: {str(e)}")
    
    def test_different_methods(self):
        """Teste 5: Diferentes métodos HTTP"""
        methods = [
            ("GET", f"{self.backend_url}/api/health"),
            ("POST", f"{self.backend_url}/api/cors-test"),
            ("PUT", f"{self.backend_url}/api/cors-test"),
            ("DELETE", f"{self.backend_url}/api/cors-test"),
        ]
        
        for method, url in methods:
            try:
                headers = {'Origin': self.frontend_origin}
                if method == "POST":
                    headers['Content-Type'] = 'application/json'
                
                response = requests.request(method, url, headers=headers, 
                                          json={} if method in ["POST", "PUT"] else None,
                                          timeout=10)
                
                cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
                
                if len(cors_headers) > 0:
                    self.log_result(f"Method {method}", True, f"Status: {response.status_code}, CORS: OK")
                else:
                    self.log_result(f"Method {method}", False, f"Status: {response.status_code}, No CORS headers")
                    
            except Exception as e:
                self.log_result(f"Method {method}", False, f"Exception: {str(e)}")
    
    def test_error_handling_with_cors(self):
        """Teste 6: Tratamento de erro com CORS"""
        try:
            response = requests.get(f"{self.backend_url}/api/nonexistent-endpoint", 
                                  headers={'Origin': self.frontend_origin}, 
                                  timeout=10)
            
            cors_headers = [h for h in response.headers.keys() if h.lower().startswith('access-control')]
            
            # Esperamos 404 com headers CORS
            if response.status_code == 404 and len(cors_headers) > 0:
                self.log_result("Error Handling CORS", True, f"404 with CORS headers")
            else:
                self.log_result("Error Handling CORS", False, f"Status: {response.status_code}, CORS: {len(cors_headers)}")
                
        except Exception as e:
            self.log_result("Error Handling CORS", False, f"Exception: {str(e)}")
    
    def test_catch_all_options(self):
        """Teste 7: Catch-all OPTIONS"""
        try:
            headers = {
                'Origin': self.frontend_origin,
                'Access-Control-Request-Method': 'POST'
            }
            response = requests.options(f"{self.backend_url}/some/random/path", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
                self.log_result("Catch-all OPTIONS", True, f"Handled with {len(cors_headers)} CORS headers")
            else:
                self.log_result("Catch-all OPTIONS", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Catch-all OPTIONS", False, f"Exception: {str(e)}")
    
    def test_multiple_origins(self):
        """Teste 8: Múltiplas origens"""
        origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://frontend-painel-universal-production.up.railway.app",
            "https://test-origin.com"
        ]
        
        for origin in origins:
            try:
                response = requests.get(f"{self.backend_url}/api/health", 
                                      headers={'Origin': origin}, timeout=10)
                
                cors_origin = response.headers.get('access-control-allow-origin', '')
                
                if cors_origin == origin or cors_origin == "*":
                    self.log_result(f"Origin {origin}", True, f"Allowed: {cors_origin}")
                else:
                    self.log_result(f"Origin {origin}", False, f"Not allowed: {cors_origin}")
                    
            except Exception as e:
                self.log_result(f"Origin {origin}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 60)
        print("CORS ULTIMATE TEST - Sistema Universal")
        print(f"Backend: {self.backend_url}")
        print("=" * 60)
        
        print("\n1. Testando headers CORS básicos...")
        self.test_basic_cors_headers()
        
        print("\n2. Testando preflight OPTIONS...")
        self.test_preflight_options()
        
        print("\n3. Testando POST com CORS...")
        self.test_post_with_cors()
        
        print("\n4. Testando endpoint CORS avançado...")
        self.test_cors_test_endpoint()
        
        print("\n5. Testando diferentes métodos HTTP...")
        self.test_different_methods()
        
        print("\n6. Testando tratamento de erro com CORS...")
        self.test_error_handling_with_cors()
        
        print("\n7. Testando catch-all OPTIONS...")
        self.test_catch_all_options()
        
        print("\n8. Testando múltiplas origens...")
        self.test_multiple_origins()
        
        # Resultado final
        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"Testes executados: {self.total_tests}")
        print(f"Sucessos: {self.success_count}")
        print(f"Falhas: {self.total_tests - self.success_count}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n✅ CORS ULTIMATE PROTECTION: FUNCIONANDO PERFEITAMENTE!")
        elif success_rate >= 70:
            print("\n⚠️  CORS: Funcionando com algumas limitações")
        else:
            print("\n❌ CORS: Problemas identificados que precisam ser resolvidos")
        
        print("\n" + "=" * 60)
        
        # Detalhar falhas se houver
        failures = [r for r in self.test_results if r["status"] == "FAIL"]
        if failures:
            print("FALHAS IDENTIFICADAS:")
            for failure in failures:
                print(f"- {failure['test']}: {failure['details']}")

if __name__ == "__main__":
    tester = CORSUltimateTest()
    tester.run_all_tests()