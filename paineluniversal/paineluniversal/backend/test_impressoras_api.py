#!/usr/bin/env python3
"""
Script para testar os endpoints da API de impressoras
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def login(self):
        """Fazer login para obter token"""
        # Primeiro, criar um usuário admin se não existir
        try:
            # Tentar fazer login com admin padrão
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                data={
                    "username": "admin",
                    "password": "admin123"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                logger.info("✅ Login realizado com sucesso")
                return True
            else:
                logger.warning(f"⚠️ Login falhou: {response.status_code}")
                # Tentar sem autenticação para testes básicos
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data=None, expected_status=[200, 201]):
        """Testar um endpoint específico"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Método não suportado: {method}")
            
            success = response.status_code in expected_status
            
            self.test_results.append({
                "endpoint": f"{method} {endpoint}",
                "status": response.status_code,
                "success": success,
                "response": response.text[:200] if not success else "OK"
            })
            
            if success:
                logger.info(f"✅ {method} {endpoint} - Status: {response.status_code}")
                return response.json() if response.text else None
            else:
                logger.error(f"❌ {method} {endpoint} - Status: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"❌ {method} {endpoint} - Erro: {e}")
            self.test_results.append({
                "endpoint": f"{method} {endpoint}",
                "error": str(e),
                "success": False
            })
            return None
    
    def run_tests(self):
        """Executar todos os testes"""
        logger.info("\n" + "="*50)
        logger.info("🧪 TESTANDO API DE IMPRESSORAS")
        logger.info("="*50)
        
        # Fazer login
        self.login()
        
        # 1. Testar listagem de impressoras (tabela já existente)
        logger.info("\n📋 Testando listagem...")
        self.test_endpoint("GET", "/api/impressoras/", expected_status=[200, 401])
        
        # 2. Testar templates
        logger.info("\n📝 Testando templates...")
        self.test_endpoint("GET", "/api/impressoras/templates/", expected_status=[200, 401])
        
        # Criar um template
        template_data = {
            "nome": "Template API Test",
            "tipo": "cupom",
            "cabecalho": "TESTE API",
            "corpo": "{{conteudo}}",
            "rodape": "Obrigado!",
            "ativo": True
        }
        result = self.test_endpoint("POST", "/api/impressoras/templates/", 
                                   template_data, expected_status=[200, 201, 401])
        
        # 3. Testar operadores
        logger.info("\n👤 Testando operadores...")
        self.test_endpoint("GET", "/api/impressoras/operadores/", expected_status=[200, 401])
        
        # Criar um operador
        operador_data = {
            "nome": "Operador API Test",
            "cpf": "222.222.222-22",
            "codigo_acesso": "1234",
            "comissao_percentual": 10,
            "comissao_fixa": 0,
            "pode_cancelar": False,
            "pode_dar_desconto": True,
            "desconto_maximo": 15,
            "ativo": True
        }
        result = self.test_endpoint("POST", "/api/impressoras/operadores/", 
                                   operador_data, expected_status=[200, 201, 401])
        
        # 4. Testar equipamentos
        logger.info("\n🖥️ Testando equipamentos...")
        self.test_endpoint("GET", "/api/impressoras/equipamentos/", expected_status=[200, 401])
        
        # Criar um equipamento
        equipamento_data = {
            "codigo": "API-TEST-001",
            "tipo": "POS",
            "nome": "Terminal API Test",
            "perfil_venda": "Padrão",
            "localizacao": "Teste",
            "versao_software": "1.0.0"
        }
        result = self.test_endpoint("POST", "/api/impressoras/equipamentos/", 
                                   equipamento_data, expected_status=[200, 201, 401])
        
        # 5. Testar fila de impressão
        logger.info("\n📬 Testando fila...")
        self.test_endpoint("GET", "/api/impressoras/fila/", expected_status=[200, 401])
        
        # 6. Testar logs
        logger.info("\n📊 Testando logs...")
        self.test_endpoint("GET", "/api/impressoras/logs/", expected_status=[200, 401])
        
        # 7. Testar roteamento inteligente
        logger.info("\n🧠 Testando roteamento inteligente...")
        self.test_endpoint("GET", "/api/impressoras/inteligentes/", expected_status=[200, 401])
        
        # Imprimir resumo
        self.print_summary()
        
    def print_summary(self):
        """Imprimir resumo dos testes"""
        logger.info("\n" + "="*50)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("="*50)
        
        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r.get("success", False))
        failed = total - success
        
        logger.info(f"Total: {total}")
        logger.info(f"✅ Sucesso: {success}")
        logger.info(f"❌ Falhou: {failed}")
        
        if failed > 0:
            logger.info("\n⚠️ Endpoints com falha:")
            for result in self.test_results:
                if not result.get("success", False):
                    logger.info(f"  - {result['endpoint']}: Status {result.get('status', 'ERROR')}")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total": total,
            "success": success,
            "failed": failed,
            "results": self.test_results
        }
        
        with open("test_impressoras_api_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Relatório salvo em: test_impressoras_api_report.json")


if __name__ == "__main__":
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            logger.info("✅ Servidor FastAPI está rodando")
        else:
            logger.warning("⚠️ Servidor respondeu com status: " + str(response.status_code))
    except requests.ConnectionError:
        logger.error("❌ Servidor não está rodando! Execute: cd backend && python -m uvicorn app.main:app --reload")
        exit(1)
    
    # Executar testes
    tester = APITester()
    tester.run_tests()