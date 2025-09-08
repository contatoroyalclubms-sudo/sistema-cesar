"""
Sistema completo de testes para o Sistema de Gestão de Eventos
"""
import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5174"
        self.cpf = "06601206154"
        self.password = "101112"
        self.token = None
        self.errors = []
        self.successes = []
        
    def log_error(self, module: str, error: str, details: Any = None):
        """Log an error"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "error": error,
            "details": details
        }
        self.errors.append(error_entry)
        print(f"[ERROR] {module}: {error}")
        if details:
            print(f"   Details: {details}")
    
    def log_success(self, module: str, message: str):
        """Log a success"""
        self.successes.append({
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "message": message
        })
        print(f"[SUCCESS] {module}: {message}")
    
    def test_api_health(self):
        """Test if API is running"""
        print("\n[TEST] Testing API Health...")
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_success("API", "API is running and docs are accessible")
                return True
            else:
                self.log_error("API", f"API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_error("API", "Cannot connect to API. Is the backend running?")
            return False
        except Exception as e:
            self.log_error("API", f"Unexpected error: {str(e)}")
            return False
    
    def test_login(self):
        """Test login functionality"""
        print("\n[TEST] Testing Login...")
        try:
            # Try login endpoint
            login_data = {
                "cpf": self.cpf,
                "senha": self.password
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.log_success("Login", f"Login successful for CPF {self.cpf}")
                    return True
                else:
                    self.log_error("Login", "Response missing access_token", data)
                    return False
            else:
                self.log_error("Login", f"Login failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_error("Login", "Cannot connect to login endpoint")
            return False
        except Exception as e:
            self.log_error("Login", f"Unexpected error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def test_module(self, module_name: str, endpoint: str, method: str = "GET", data: Dict = None):
        """Generic module tester"""
        print(f"\n[TEST] Testing {module_name}...")
        try:
            headers = self.get_headers()
            
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=10)
            else:
                response = requests.request(method, f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                self.log_success(module_name, f"Module accessible and returned data")
                return True
            elif response.status_code == 401:
                self.log_error(module_name, "Authentication required or token invalid")
                return False
            elif response.status_code == 403:
                self.log_error(module_name, "Access forbidden - insufficient permissions")
                return False
            elif response.status_code == 404:
                self.log_error(module_name, f"Endpoint not found: {endpoint}")
                return False
            else:
                self.log_error(module_name, f"Request failed with status {response.status_code}", response.text[:200])
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_error(module_name, f"Cannot connect to endpoint {endpoint}")
            return False
        except Exception as e:
            self.log_error(module_name, f"Unexpected error: {str(e)}")
            return False
    
    def test_all_modules(self):
        """Test all system modules"""
        modules = [
            ("Dashboard", "/api/dashboard/stats"),
            ("Eventos", "/api/eventos"),
            ("Usuarios", "/api/usuarios"),
            ("PDV", "/api/pdv/eventos"),
            ("Checkin", "/api/checkin/eventos"),
            ("Estoque", "/api/estoque/produtos"),
            ("Financeiro", "/api/financeiro/transacoes"),
            ("Listas", "/api/listas"),
            ("Ranking", "/api/gamificacao/ranking"),
            ("Cashless", "/api/cashless/carteiras"),
            ("KDS", "/api/kds/pedidos"),
            ("Mesas", "/api/mesas"),
            ("Fidelidade", "/api/fidelidade/programas"),
            ("Colaboradores", "/api/colaboradores"),
            ("WhatsApp", "/api/whatsapp/status"),
        ]
        
        for module_name, endpoint in modules:
            self.test_module(module_name, endpoint)
            time.sleep(0.5)  # Small delay between tests
    
    def test_frontend(self):
        """Test if frontend is accessible"""
        print("\n[TEST] Testing Frontend...")
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_success("Frontend", "Frontend is running and accessible")
                return True
            else:
                self.log_error("Frontend", f"Frontend returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_error("Frontend", "Cannot connect to frontend. Is it running?")
            return False
        except Exception as e:
            self.log_error("Frontend", f"Unexpected error: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("TEST REPORT")
        print("="*60)
        
        total_tests = len(self.successes) + len(self.errors)
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Successes: {len(self.successes)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n[ERRORS FOUND]:")
            print("-"*40)
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. {error['module']}")
                print(f"   Error: {error['error']}")
                if error.get('details'):
                    print(f"   Details: {error['details'][:100]}...")
        
        # Save errors to file
        if self.errors:
            with open('test_errors.json', 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVED] Errors saved to test_errors.json")
        
        # Save full report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "successes": len(self.successes),
                "errors": len(self.errors)
            },
            "successes": self.successes,
            "errors": self.errors
        }
        
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] Full report saved to test_report.json")
        
        return len(self.errors) == 0
    
    def run(self):
        """Run all tests"""
        print("[START] Starting System Tests...")
        print(f"   Backend: {self.base_url}")
        print(f"   Frontend: {self.frontend_url}")
        print(f"   CPF: {self.cpf}")
        
        # Test sequence
        if not self.test_api_health():
            print("\n[WARNING] API is not running. Please start the backend first.")
            return False
        
        self.test_frontend()
        
        if self.test_login():
            self.test_all_modules()
        else:
            print("\n[WARNING] Login failed. Skipping authenticated tests.")
        
        # Generate report
        success = self.generate_report()
        
        if success:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[WARNING] Found {len(self.errors)} errors. Please review test_errors.json")
        
        return success

if __name__ == "__main__":
    tester = SystemTester()
    tester.run()