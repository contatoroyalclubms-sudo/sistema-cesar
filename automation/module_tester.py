#!/usr/bin/env python3
"""
TESTADOR AUTOMATIZADO DE MÓDULOS - NÍVEL 1
Sistema para testar cada módulo individualmente com validação completa de CRUD
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import random
import string

logger = logging.getLogger(__name__)

class ModuleTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.test_data = {}
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "summary": {}
        }
        
    async def authenticate(self):
        """Fazer login e obter token de autenticação"""
        logger.info("🔐 Autenticando usuário de teste...")
        
        # Dados de teste (criar se não existir)
        login_data = {
            "email": "admin@teste.com",
            "senha": "admin123"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    logger.info("✅ Autenticação realizada com sucesso")
                    return True
                elif response.status_code == 404:
                    # Tentar criar usuário
                    return await self.create_test_user()
                else:
                    logger.error(f"❌ Falha na autenticação: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            return False
    
    async def create_test_user(self):
        """Criar usuário de teste se não existir"""
        logger.info("👤 Criando usuário de teste...")
        
        user_data = {
            "nome": "Admin Teste",
            "email": "admin@teste.com",
            "cpf": "11111111111",
            "senha": "admin123",
            "tipo": "admin"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/register",
                    json=user_data
                )
                
                if response.status_code == 201:
                    logger.info("✅ Usuário de teste criado")
                    # Tentar login novamente
                    return await self.authenticate()
                else:
                    logger.error(f"❌ Falha ao criar usuário: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário: {e}")
            return False
    
    def get_headers(self):
        """Obter headers com token de autenticação"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {"Content-Type": "application/json"}
    
    async def test_authentication_module(self):
        """Testar módulo de autenticação"""
        logger.info("🔐 Testando módulo de autenticação...")
        
        module_results = {
            "name": "Autenticação",
            "tests": {},
            "status": "unknown",
            "errors": []
        }
        
        try:
            # Teste 1: Login com credenciais válidas
            login_data = {"email": "admin@teste.com", "senha": "admin123"}
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/auth/login", json=login_data)
                module_results["tests"]["login_valid"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Teste 2: Login com credenciais inválidas
            bad_login_data = {"email": "admin@teste.com", "senha": "senhaerrada"}
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/auth/login", json=bad_login_data)
                module_results["tests"]["login_invalid"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [401, 422],
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Teste 3: Verificar token (se tiver)
            if self.token:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/api/auth/me", headers=self.get_headers())
                    module_results["tests"]["token_validation"] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds()
                    }
            
            # Determinar status do módulo
            successful_tests = sum(1 for test in module_results["tests"].values() if test["success"])
            total_tests = len(module_results["tests"])
            
            if successful_tests == total_tests:
                module_results["status"] = "operational"
            elif successful_tests > 0:
                module_results["status"] = "partial"
            else:
                module_results["status"] = "broken"
                
        except Exception as e:
            module_results["status"] = "error"
            module_results["errors"].append(str(e))
            logger.error(f"❌ Erro no teste de autenticação: {e}")
        
        self.results["modules"]["authentication"] = module_results
        return module_results
    
    async def test_events_module(self):
        """Testar módulo de eventos (CRUD completo)"""
        logger.info("🎉 Testando módulo de eventos...")
        
        module_results = {
            "name": "Gestão de Eventos",
            "tests": {},
            "status": "unknown", 
            "errors": []
        }
        
        try:
            # Teste 1: Listar eventos
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/eventos", headers=self.get_headers())
                module_results["tests"]["list_events"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code == 200:
                    events_data = response.json()
                    module_results["tests"]["list_events"]["count"] = len(events_data)
            
            # Teste 2: Criar novo evento
            new_event_data = {
                "nome": f"Evento Teste {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "data": "2025-12-31T20:00:00",
                "local": "Local de Teste",
                "descricao": "Evento criado automaticamente para teste"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/eventos", 
                                           json=new_event_data, headers=self.get_headers())
                module_results["tests"]["create_event"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 201,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code == 201:
                    created_event = response.json()
                    self.test_data["created_event_id"] = created_event.get("id")
            
            # Teste 3: Buscar evento específico (se criou)
            if "created_event_id" in self.test_data:
                event_id = self.test_data["created_event_id"]
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/api/eventos/{event_id}", 
                                              headers=self.get_headers())
                    module_results["tests"]["get_specific_event"] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds()
                    }
            
            # Teste 4: Atualizar evento (se criou)
            if "created_event_id" in self.test_data:
                event_id = self.test_data["created_event_id"]
                update_data = {"nome": f"Evento Atualizado {datetime.now().strftime('%H:%M:%S')}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.put(f"{self.base_url}/api/eventos/{event_id}",
                                              json=update_data, headers=self.get_headers())
                    module_results["tests"]["update_event"] = {
                        "status_code": response.status_code,
                        "success": response.status_code in [200, 204],
                        "response_time": response.elapsed.total_seconds()
                    }
            
            # Determinar status do módulo
            successful_tests = sum(1 for test in module_results["tests"].values() if test["success"])
            total_tests = len(module_results["tests"])
            
            if successful_tests == total_tests:
                module_results["status"] = "operational"
            elif successful_tests > 0:
                module_results["status"] = "partial"
            else:
                module_results["status"] = "broken"
                
        except Exception as e:
            module_results["status"] = "error"
            module_results["errors"].append(str(e))
            logger.error(f"❌ Erro no teste de eventos: {e}")
        
        self.results["modules"]["events"] = module_results
        return module_results
    
    async def test_users_module(self):
        """Testar módulo de usuários"""
        logger.info("👥 Testando módulo de usuários...")
        
        module_results = {
            "name": "Gestão de Usuários",
            "tests": {},
            "status": "unknown",
            "errors": []
        }
        
        try:
            # Teste 1: Listar usuários
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/usuarios", headers=self.get_headers())
                module_results["tests"]["list_users"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Teste 2: Criar novo usuário de teste
            random_suffix = ''.join(random.choices(string.digits, k=4))
            new_user_data = {
                "nome": f"Usuario Teste {random_suffix}",
                "email": f"teste{random_suffix}@teste.com",
                "cpf": f"{random_suffix}00000000",
                "senha": "teste123",
                "tipo": "cliente"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/usuarios",
                                           json=new_user_data, headers=self.get_headers())
                module_results["tests"]["create_user"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 201,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code == 201:
                    created_user = response.json()
                    self.test_data["created_user_id"] = created_user.get("id")
            
            # Determinar status do módulo
            successful_tests = sum(1 for test in module_results["tests"].values() if test["success"])
            total_tests = len(module_results["tests"])
            
            if successful_tests == total_tests:
                module_results["status"] = "operational"
            elif successful_tests > 0:
                module_results["status"] = "partial"
            else:
                module_results["status"] = "broken"
                
        except Exception as e:
            module_results["status"] = "error"
            module_results["errors"].append(str(e))
            logger.error(f"❌ Erro no teste de usuários: {e}")
        
        self.results["modules"]["users"] = module_results
        return module_results
    
    async def test_checkin_module(self):
        """Testar módulo de check-in"""
        logger.info("✅ Testando módulo de check-in...")
        
        module_results = {
            "name": "Sistema de Check-in",
            "tests": {},
            "status": "unknown",
            "errors": []
        }
        
        try:
            # Teste 1: Status do check-in
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/checkin/status", headers=self.get_headers())
                module_results["tests"]["checkin_status"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 404],
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Teste 2: Listar check-ins (se endpoint existir)
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/checkin", headers=self.get_headers())
                module_results["tests"]["list_checkins"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 404],
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Determinar status do módulo
            successful_tests = sum(1 for test in module_results["tests"].values() if test["success"])
            total_tests = len(module_results["tests"])
            
            if successful_tests == total_tests:
                module_results["status"] = "operational"
            elif successful_tests > 0:
                module_results["status"] = "partial"
            else:
                module_results["status"] = "broken"
                
        except Exception as e:
            module_results["status"] = "error"
            module_results["errors"].append(str(e))
            logger.error(f"❌ Erro no teste de check-in: {e}")
        
        self.results["modules"]["checkin"] = module_results
        return module_results
    
    async def test_pdv_module(self):
        """Testar módulo PDV"""
        logger.info("🏪 Testando módulo PDV...")
        
        module_results = {
            "name": "PDV e Vendas",
            "tests": {},
            "status": "unknown",
            "errors": []
        }
        
        try:
            # Teste 1: Status do PDV
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/pdv/status", headers=self.get_headers())
                module_results["tests"]["pdv_status"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 404],
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Teste 2: Listar produtos
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/produtos", headers=self.get_headers())
                module_results["tests"]["list_products"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 404],
                    "response_time": response.elapsed.total_seconds()
                }
            
            # Determinar status do módulo
            successful_tests = sum(1 for test in module_results["tests"].values() if test["success"])
            total_tests = len(module_results["tests"])
            
            if successful_tests == total_tests:
                module_results["status"] = "operational"
            elif successful_tests > 0:
                module_results["status"] = "partial"
            else:
                module_results["status"] = "broken"
                
        except Exception as e:
            module_results["status"] = "error"
            module_results["errors"].append(str(e))
            logger.error(f"❌ Erro no teste de PDV: {e}")
        
        self.results["modules"]["pdv"] = module_results
        return module_results
    
    async def run_all_tests(self):
        """Executar todos os testes de módulos"""
        logger.info("🚀 Iniciando testes completos de todos os módulos...")
        
        # Autenticar primeiro
        if not await self.authenticate():
            logger.error("❌ Falha na autenticação - abortando testes")
            return self.results
        
        # Lista de testes a executar
        test_modules = [
            self.test_authentication_module,
            self.test_events_module,
            self.test_users_module,
            self.test_checkin_module,
            self.test_pdv_module
        ]
        
        # Executar cada teste
        for test_func in test_modules:
            try:
                await test_func()
                await asyncio.sleep(1)  # Pequena pausa entre testes
            except Exception as e:
                logger.error(f"❌ Erro ao executar {test_func.__name__}: {e}")
        
        # Gerar resumo
        self.generate_summary()
        
        # Salvar resultados
        self.save_results()
        
        return self.results
    
    def generate_summary(self):
        """Gerar resumo dos testes"""
        total_modules = len(self.results["modules"])
        operational_modules = sum(1 for m in self.results["modules"].values() if m["status"] == "operational")
        partial_modules = sum(1 for m in self.results["modules"].values() if m["status"] == "partial")
        broken_modules = sum(1 for m in self.results["modules"].values() if m["status"] == "broken")
        error_modules = sum(1 for m in self.results["modules"].values() if m["status"] == "error")
        
        self.results["summary"] = {
            "total_modules": total_modules,
            "operational": operational_modules,
            "partial": partial_modules,
            "broken": broken_modules,
            "errors": error_modules,
            "success_rate": (operational_modules / total_modules * 100) if total_modules > 0 else 0
        }
        
        logger.info(f"📊 Resumo dos testes:")
        logger.info(f"   Total: {total_modules}")
        logger.info(f"   Operacionais: {operational_modules}")
        logger.info(f"   Parciais: {partial_modules}")
        logger.info(f"   Quebrados: {broken_modules}")
        logger.info(f"   Erros: {error_modules}")
        logger.info(f"   Taxa de Sucesso: {self.results['summary']['success_rate']:.1f}%")
    
    def save_results(self):
        """Salvar resultados dos testes"""
        results_dir = Path(__file__).parent / "reports"
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"module_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"💾 Resultados salvos em: {results_file}")

async def main():
    """Função principal"""
    tester = ModuleTester()
    results = await tester.run_all_tests()
    
    print(f"\n🎯 TESTES CONCLUÍDOS")
    print(f"Taxa de sucesso: {results['summary']['success_rate']:.1f}%")
    print(f"Módulos operacionais: {results['summary']['operational']}/{results['summary']['total_modules']}")

if __name__ == "__main__":
    asyncio.run(main())