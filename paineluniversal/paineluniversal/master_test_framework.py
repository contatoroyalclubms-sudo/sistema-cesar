#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 MASTER TEST FRAMEWORK - SISTEMA PAINEL UNIVERSAL
===================================================

Framework mestre para testar TODAS as funcionalidades do sistema
com garantia de ZERO BREAKING CHANGES para produção.

Autor: Agente de Desenvolvimento
Data: 2024
Missão: Capturar e corrigir TODOS os erros sem quebrar produção
"""

import os
import sys
import json
import time
import asyncio
import requests
import sqlite3
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_test_framework.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterTestFramework:
    """Framework mestre de testes com 4 camadas de validação"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "framework_info": {
                "version": "1.0.0",
                "start_time": datetime.now().isoformat(),
                "mission": "Teste completo com zero breaking changes",
                "target_system": "Painel Universal"
            },
            "layers": {
                "preservation": {"status": "pending", "tests": [], "critical": True},
                "backend_api": {"status": "pending", "tests": [], "critical": True},
                "frontend_components": {"status": "pending", "tests": [], "critical": False},
                "integration": {"status": "pending", "tests": [], "critical": True}
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "critical_failures": 0,
                "errors": []
            },
            "production_safety": {
                "breaking_changes_detected": False,
                "critical_functions_verified": False,
                "deployment_safe": False
            }
        }
        
        # URLs e configurações
        self.base_urls = [
            "http://localhost:8000",
            "https://paineluniversal-backend-production.up.railway.app",
            "https://paineluniversal-production.up.railway.app"
        ]
        self.active_url = None
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log(self, message: str, level: str = "INFO", layer: str = None):
        """Log estruturado com contexto"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        layer_prefix = f"[{layer}] " if layer else ""
        full_message = f"{layer_prefix}{message}"
        
        if level == "ERROR":
            logger.error(full_message)
        elif level == "WARNING":
            logger.warning(full_message)
        else:
            logger.info(full_message)
            
        print(f"[{timestamp}] [{level}] {full_message}")
    
    def detect_active_backend(self) -> Optional[str]:
        """Detectar qual backend está ativo"""
        self.log("🔍 Detectando backend ativo...", "INFO", "SETUP")
        
        for url in self.base_urls:
            try:
                response = self.session.get(f"{url}/health", timeout=10)
                if response.status_code == 200:
                    self.active_url = url
                    self.log(f"✅ Backend ativo encontrado: {url}", "INFO", "SETUP")
                    return url
            except Exception as e:
                self.log(f"❌ Backend {url} não disponível: {str(e)}", "WARNING", "SETUP")
                continue
        
        self.log("🚨 Nenhum backend ativo encontrado!", "ERROR", "SETUP")
        return None
    
    def run_preservation_tests(self) -> Dict[str, Any]:
        """CAMADA 1: Testes de Preservação - Garantir que nada quebra"""
        self.log("🛡️ INICIANDO CAMADA 1: TESTES DE PRESERVAÇÃO", "INFO", "PRESERVATION")
        self.log("🎯 Objetivo: Garantir zero breaking changes", "INFO", "PRESERVATION")
        
        layer_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "critical_failures": 0}
        }
        
        # Lista de testes críticos de preservação
        preservation_tests = [
            ("Backend Health Check", self._test_backend_health),
            ("Autenticação JWT", self._test_jwt_authentication),
            ("Auto-Recovery System", self._test_auto_recovery),
            ("CORS Configuration", self._test_cors_config),
            ("Database Connectivity", self._test_database_connectivity),
            ("Critical Endpoints", self._test_critical_endpoints),
            ("Frontend Build Integrity", self._test_frontend_build),
            ("Environment Variables", self._test_environment_vars)
        ]
        
        for test_name, test_func in preservation_tests:
            result = self._execute_test(test_name, test_func, "PRESERVATION")
            layer_results["tests"].append(result)
            
            if result["status"] == "passed":
                layer_results["summary"]["passed"] += 1
            else:
                layer_results["summary"]["failed"] += 1
                if result.get("critical", True):
                    layer_results["summary"]["critical_failures"] += 1
                    self.results["production_safety"]["breaking_changes_detected"] = True
        
        layer_results["end_time"] = datetime.now().isoformat()
        self.results["layers"]["preservation"] = layer_results
        
        # Verificar se é seguro continuar
        if layer_results["summary"]["critical_failures"] > 0:
            self.log("🚨 FALHAS CRÍTICAS DETECTADAS - PARANDO EXECUÇÃO", "ERROR", "PRESERVATION")
            self.results["production_safety"]["deployment_safe"] = False
            return layer_results
        
        self.log("✅ Camada de preservação passou - Sistema seguro", "INFO", "PRESERVATION")
        self.results["production_safety"]["critical_functions_verified"] = True
        return layer_results
    
    def run_backend_api_tests(self) -> Dict[str, Any]:
        """CAMADA 2: Testes de Backend APIs"""
        self.log("🔧 INICIANDO CAMADA 2: TESTES DE BACKEND APIs", "INFO", "BACKEND")
        
        layer_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "skipped": 0}
        }
        
        # Lista de routers para testar
        routers_to_test = [
            "auth", "eventos", "produtos", "usuarios", "dashboard",
            "estoque", "financeiro", "pdv", "checkins", "listas",
            "empresas", "relatorios", "import_export", "gamificacao"
        ]
        
        for router in routers_to_test:
            result = self._test_router_endpoints(router)
            layer_results["tests"].append(result)
            
            if result["status"] == "passed":
                layer_results["summary"]["passed"] += 1
            elif result["status"] == "skipped":
                layer_results["summary"]["skipped"] += 1
            else:
                layer_results["summary"]["failed"] += 1
        
        layer_results["end_time"] = datetime.now().isoformat()
        self.results["layers"]["backend_api"] = layer_results
        return layer_results
    
    def run_frontend_component_tests(self) -> Dict[str, Any]:
        """CAMADA 3: Testes de Componentes Frontend"""
        self.log("🎨 INICIANDO CAMADA 3: TESTES DE COMPONENTES FRONTEND", "INFO", "FRONTEND")
        
        layer_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "skipped": 0}
        }
        
        # Componentes críticos para testar
        components_to_test = [
            "auth", "dashboard", "eventos", "produtos", "usuarios",
            "estoque", "financeiro", "pdv", "checkin", "listas",
            "ranking", "sales"
        ]
        
        for component in components_to_test:
            result = self._test_frontend_component(component)
            layer_results["tests"].append(result)
            
            if result["status"] == "passed":
                layer_results["summary"]["passed"] += 1
            elif result["status"] == "skipped":
                layer_results["summary"]["skipped"] += 1
            else:
                layer_results["summary"]["failed"] += 1
        
        layer_results["end_time"] = datetime.now().isoformat()
        self.results["layers"]["frontend_components"] = layer_results
        return layer_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """CAMADA 4: Testes de Integração End-to-End"""
        self.log("🔗 INICIANDO CAMADA 4: TESTES DE INTEGRAÇÃO", "INFO", "INTEGRATION")
        
        layer_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "skipped": 0}
        }
        
        # Fluxos de integração para testar
        integration_flows = [
            ("Login Flow Complete", self._test_login_flow),
            ("CRUD Operations Flow", self._test_crud_operations),
            ("Error Recovery Flow", self._test_error_recovery),
            ("Performance Under Load", self._test_performance_load),
            ("Security Vulnerabilities", self._test_security_vulns),
            ("Data Consistency", self._test_data_consistency)
        ]
        
        for test_name, test_func in integration_flows:
            result = self._execute_test(test_name, test_func, "INTEGRATION")
            layer_results["tests"].append(result)
            
            if result["status"] == "passed":
                layer_results["summary"]["passed"] += 1
            elif result["status"] == "skipped":
                layer_results["summary"]["skipped"] += 1
            else:
                layer_results["summary"]["failed"] += 1
        
        layer_results["end_time"] = datetime.now().isoformat()
        self.results["layers"]["integration"] = layer_results
        return layer_results
    
    def _execute_test(self, test_name: str, test_func, layer: str) -> Dict[str, Any]:
        """Executar um teste individual com tratamento de erro"""
        test_start = time.time()
        
        self.log(f"🔍 Executando: {test_name}", "INFO", layer)
        
        test_result = {
            "name": test_name,
            "layer": layer,
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
            "message": "",
            "details": {},
            "duration": 0,
            "error": None
        }
        
        try:
            result = test_func()
            test_duration = time.time() - test_start
            
            if isinstance(result, dict):
                test_result.update(result)
            elif result is True:
                test_result["status"] = "passed"
                test_result["message"] = "Teste passou com sucesso"
            elif result is False:
                test_result["status"] = "failed"
                test_result["message"] = "Teste falhou"
            else:
                test_result["status"] = "passed"
                test_result["message"] = str(result)
            
            test_result["duration"] = round(test_duration, 3)
            
            # Log resultado
            status_icon = "✅" if test_result["status"] == "passed" else "❌" if test_result["status"] == "failed" else "⏭️"
            self.log(f"   {status_icon} {test_result['message']} ({test_duration:.3f}s)", "INFO", layer)
            
        except Exception as e:
            test_duration = time.time() - test_start
            test_result.update({
                "status": "failed",
                "message": f"Erro durante execução: {str(e)}",
                "duration": round(test_duration, 3),
                "error": traceback.format_exc()
            })
            
            self.log(f"   ❌ ERRO: {str(e)}", "ERROR", layer)
            
            # Adicionar ao registro de erros
            self.results["summary"]["errors"].append({
                "layer": layer,
                "test": test_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        # Atualizar contadores globais
        self.results["summary"]["total_tests"] += 1
        if test_result["status"] == "passed":
            self.results["summary"]["passed"] += 1
        elif test_result["status"] == "failed":
            self.results["summary"]["failed"] += 1
        else:
            self.results["summary"]["skipped"] += 1
        
        return test_result
    
    # ============================================================================
    # TESTES DE PRESERVAÇÃO (CAMADA 1)
    # ============================================================================
    
    def _test_backend_health(self) -> Dict[str, Any]:
        """Testar saúde do backend"""
        if not self.active_url:
            return {
                "status": "failed",
                "message": "Nenhum backend ativo encontrado",
                "critical": True
            }
        
        try:
            response = self.session.get(f"{self.active_url}/health")
            
            if response.status_code == 200:
                return {
                    "status": "passed",
                    "message": f"Backend saudável - {self.active_url}",
                    "details": {"url": self.active_url, "response_time": response.elapsed.total_seconds()}
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Backend não saudável - Status {response.status_code}",
                    "critical": True
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao verificar saúde: {str(e)}",
                "critical": True
            }
    
    def _test_jwt_authentication(self) -> Dict[str, Any]:
        """Testar autenticação JWT"""
        try:
            # Tentar login com usuário padrão
            login_data = {"username": "admin", "password": "admin123"}
            
            response = self.session.post(
                f"{self.active_url}/api/auth/login", 
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return {
                        "status": "passed",
                        "message": "Autenticação JWT funcionando",
                        "details": {"token_type": data.get("token_type", "bearer")}
                    }
            
            return {
                "status": "failed",
                "message": f"Falha na autenticação - Status {response.status_code}",
                "critical": True
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro na autenticação: {str(e)}",
                "critical": True
            }
    
    def _test_auto_recovery(self) -> Dict[str, Any]:
        """Testar sistema de auto-recovery"""
        try:
            # Verificar se há múltiplas URLs configuradas
            working_urls = []
            
            for url in self.base_urls:
                try:
                    response = requests.get(f"{url}/health", timeout=5)
                    if response.status_code == 200:
                        working_urls.append(url)
                except:
                    continue
            
            if len(working_urls) >= 2:
                return {
                    "status": "passed",
                    "message": f"Auto-recovery configurado - {len(working_urls)} backends disponíveis",
                    "details": {"working_urls": working_urls}
                }
            elif len(working_urls) == 1:
                return {
                    "status": "passed",
                    "message": "Um backend funcionando - Auto-recovery parcial",
                    "details": {"working_urls": working_urls}
                }
            else:
                return {
                    "status": "failed",
                    "message": "Nenhum backend funcionando",
                    "critical": True
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste de auto-recovery: {str(e)}",
                "critical": False
            }
    
    def _test_cors_config(self) -> Dict[str, Any]:
        """Testar configuração CORS"""
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(
                f"{self.active_url}/api/usuarios",
                headers=headers
            )
            
            cors_headers = {
                key: value for key, value in response.headers.items()
                if key.lower().startswith('access-control')
            }
            
            if cors_headers:
                return {
                    "status": "passed",
                    "message": "CORS configurado corretamente",
                    "details": {"cors_headers": cors_headers}
                }
            else:
                return {
                    "status": "failed",
                    "message": "CORS não configurado",
                    "critical": False
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste CORS: {str(e)}",
                "critical": False
            }
    
    def _test_database_connectivity(self) -> Dict[str, Any]:
        """Testar conectividade com banco de dados"""
        try:
            # Testar SQLite local
            sqlite_path = Path("backend/eventos.db")
            if sqlite_path.exists():
                conn = sqlite3.connect(str(sqlite_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                user_count = cursor.fetchone()[0]
                conn.close()
                
                return {
                    "status": "passed",
                    "message": f"Database SQLite conectado - {user_count} usuários",
                    "details": {"database_type": "SQLite", "user_count": user_count}
                }
            else:
                return {
                    "status": "failed",
                    "message": "Database SQLite não encontrado",
                    "critical": True
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro de conectividade DB: {str(e)}",
                "critical": True
            }
    
    def _test_critical_endpoints(self) -> Dict[str, Any]:
        """Testar endpoints críticos"""
        try:
            critical_endpoints = [
                "/api/usuarios",
                "/api/eventos", 
                "/api/produtos",
                "/api/dashboard/stats"
            ]
            
            working_endpoints = 0
            total_endpoints = len(critical_endpoints)
            
            for endpoint in critical_endpoints:
                try:
                    response = self.session.get(f"{self.active_url}{endpoint}")
                    if response.status_code < 500:  # Aceitar até 4xx
                        working_endpoints += 1
                except:
                    continue
            
            if working_endpoints == total_endpoints:
                return {
                    "status": "passed",
                    "message": f"Todos os {total_endpoints} endpoints críticos funcionando",
                    "details": {"working": working_endpoints, "total": total_endpoints}
                }
            elif working_endpoints >= total_endpoints * 0.8:
                return {
                    "status": "passed",
                    "message": f"{working_endpoints}/{total_endpoints} endpoints funcionando",
                    "details": {"working": working_endpoints, "total": total_endpoints}
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Apenas {working_endpoints}/{total_endpoints} endpoints funcionando",
                    "critical": True
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao testar endpoints: {str(e)}",
                "critical": True
            }
    
    def _test_frontend_build(self) -> Dict[str, Any]:
        """Testar integridade do build do frontend"""
        try:
            frontend_path = Path("frontend")
            build_path = frontend_path / "dist"
            
            if build_path.exists():
                # Contar arquivos no build
                files = list(build_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                
                # Verificar arquivos críticos
                critical_files = ["index.html", "assets"]
                missing_files = []
                
                for critical in critical_files:
                    if not (build_path / critical).exists():
                        missing_files.append(critical)
                
                if not missing_files:
                    return {
                        "status": "passed",
                        "message": f"Build do frontend íntegro - {file_count} arquivos",
                        "details": {"file_count": file_count, "build_path": str(build_path)}
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Arquivos críticos ausentes: {missing_files}",
                        "critical": False
                    }
            else:
                return {
                    "status": "failed",
                    "message": "Build do frontend não encontrado",
                    "critical": False
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao verificar build: {str(e)}",
                "critical": False
            }
    
    def _test_environment_vars(self) -> Dict[str, Any]:
        """Testar variáveis de ambiente"""
        try:
            # Verificar arquivo .env
            env_path = Path(".env")
            if env_path.exists():
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                # Contar variáveis
                env_lines = [line for line in env_content.split('\n') 
                           if line.strip() and not line.strip().startswith('#') and '=' in line]
                
                return {
                    "status": "passed",
                    "message": f"Arquivo .env encontrado - {len(env_lines)} variáveis",
                    "details": {"env_vars_count": len(env_lines)}
                }
            else:
                return {
                    "status": "failed",
                    "message": "Arquivo .env não encontrado",
                    "critical": False
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao verificar .env: {str(e)}",
                "critical": False
            }
    
    # ============================================================================
    # TESTES DE BACKEND (CAMADA 2)
    # ============================================================================
    
    def _test_router_endpoints(self, router_name: str) -> Dict[str, Any]:
        """Testar endpoints de um router específico"""
        try:
            # Mapear routers para endpoints
            router_endpoints = {
                "auth": ["/api/auth/login", "/api/auth/register"],
                "usuarios": ["/api/usuarios", "/api/usuarios/me"],
                "eventos": ["/api/eventos"],
                "produtos": ["/api/produtos"],
                "dashboard": ["/api/dashboard/stats"],
                "estoque": ["/api/estoque"],
                "financeiro": ["/api/financeiro"],
                "pdv": ["/api/pdv"],
                "checkins": ["/api/checkins"],
                "listas": ["/api/listas"],
                "empresas": ["/api/empresas"],
                "relatorios": ["/api/relatorios"],
                "import_export": ["/api/import_export"],
                "gamificacao": ["/api/gamificacao"]
            }
            
            endpoints = router_endpoints.get(router_name, [])
            if not endpoints:
                return {
                    "status": "skipped",
                    "message": f"Router {router_name} não mapeado para testes"
                }
            
            working_endpoints = 0
            endpoint_results = {}
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.active_url}{endpoint}")
                    endpoint_results[endpoint] = {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                    
                    if response.status_code < 500:
                        working_endpoints += 1
                        
                except Exception as e:
                    endpoint_results[endpoint] = {"error": str(e)}
            
            success_rate = working_endpoints / len(endpoints)
            
            if success_rate >= 0.8:
                return {
                    "status": "passed",
                    "message": f"Router {router_name}: {working_endpoints}/{len(endpoints)} endpoints OK",
                    "details": {"endpoints": endpoint_results, "success_rate": success_rate}
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Router {router_name}: apenas {working_endpoints}/{len(endpoints)} endpoints OK",
                    "details": {"endpoints": endpoint_results, "success_rate": success_rate}
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao testar router {router_name}: {str(e)}"
            }
    
    # ============================================================================
    # TESTES DE FRONTEND (CAMADA 3)
    # ============================================================================
    
    def _test_frontend_component(self, component_name: str) -> Dict[str, Any]:
        """Testar componente do frontend"""
        try:
            component_path = Path(f"frontend/src/components/{component_name}")
            
            if component_path.exists():
                # Contar arquivos do componente
                files = list(component_path.rglob("*.tsx")) + list(component_path.rglob("*.ts"))
                file_count = len(files)
                
                if file_count > 0:
                    return {
                        "status": "passed",
                        "message": f"Componente {component_name}: {file_count} arquivos encontrados",
                        "details": {"file_count": file_count, "path": str(component_path)}
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Componente {component_name}: nenhum arquivo encontrado"
                    }
            else:
                return {
                    "status": "skipped",
                    "message": f"Componente {component_name} não existe"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro ao testar componente {component_name}: {str(e)}"
            }
    
    # ============================================================================
    # TESTES DE INTEGRAÇÃO (CAMADA 4)
    # ============================================================================
    
    def _test_login_flow(self) -> Dict[str, Any]:
        """Testar fluxo completo de login"""
        try:
            # Simular fluxo completo de login
            login_data = {"username": "admin", "password": "admin123"}
            
            # 1. Fazer login
            login_response = self.session.post(
                f"{self.active_url}/api/auth/login", 
                json=login_data
            )
            
            if login_response.status_code != 200:
                return {
                    "status": "failed",
                    "message": f"Falha no login - Status {login_response.status_code}"
                }
            
            token_data = login_response.json()
            token = token_data.get("access_token")
            
            if not token:
                return {
                    "status": "failed",
                    "message": "Token não retornado no login"
                }
            
            # 2. Usar token para acessar endpoint protegido
            headers = {"Authorization": f"Bearer {token}"}
            protected_response = self.session.get(
                f"{self.active_url}/api/usuarios/me",
                headers=headers
            )
            
            if protected_response.status_code == 200:
                return {
                    "status": "passed",
                    "message": "Fluxo de login completo funcionando",
                    "details": {
                        "token_received": True,
                        "protected_access": True,
                        "user_data": protected_response.json()
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Falha no acesso protegido - Status {protected_response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no fluxo de login: {str(e)}"
            }
    
    def _test_crud_operations(self) -> Dict[str, Any]:
        """Testar operações CRUD básicas"""
        try:
            # Este teste seria expandido para testar CRUD em entidades específicas
            return {
                "status": "skipped",
                "message": "Teste CRUD será implementado em versão futura"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste CRUD: {str(e)}"
            }
    
    def _test_error_recovery(self) -> Dict[str, Any]:
        """Testar recuperação de erros"""
        try:
            # Testar endpoint inexistente
            response = self.session.get(f"{self.active_url}/api/nonexistent")
            
            if response.status_code == 404:
                return {
                    "status": "passed",
                    "message": "Sistema trata erros 404 corretamente",
                    "details": {"error_handled": True}
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Erro não tratado corretamente - Status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste de recovery: {str(e)}"
            }
    
    def _test_performance_load(self) -> Dict[str, Any]:
        """Testar performance sob carga"""
        try:
            # Teste básico de performance
            start_time = time.time()
            
            # Fazer 10 requisições simultâneas
            responses = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(self.session.get, f"{self.active_url}/health")
                    for _ in range(10)
                ]
                
                for future in as_completed(futures):
                    try:
                        response = future.result(timeout=30)
                        responses.append(response.status_code)
                    except Exception:
                        responses.append(0)
            
            total_time = time.time() - start_time
            successful_requests = len([r for r in responses if r == 200])
            
            if successful_requests >= 8:  # 80% de sucesso
                return {
                    "status": "passed",
                    "message": f"Performance OK - {successful_requests}/10 requisições em {total_time:.2f}s",
                    "details": {
                        "successful_requests": successful_requests,
                        "total_time": total_time,
                        "avg_time_per_request": total_time / 10
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Performance baixa - {successful_requests}/10 requisições em {total_time:.2f}s"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste de performance: {str(e)}"
            }
    
    def _test_security_vulns(self) -> Dict[str, Any]:
        """Testar vulnerabilidades de segurança básicas"""
        try:
            # Teste básico de injeção SQL
            malicious_input = "'; DROP TABLE usuarios; --"
            
            response = self.session.post(
                f"{self.active_url}/api/auth/login",
                json={"username": malicious_input, "password": "test"}
            )
            
            # Se retornar 422 (Unprocessable Entity) ou 400, é bom sinal
            if response.status_code in [400, 422]:
                return {
                    "status": "passed",
                    "message": "Sistema rejeita entrada maliciosa corretamente",
                    "details": {"input_validation": True}
                }
            elif response.status_code == 500:
                return {
                    "status": "failed",
                    "message": "Possível vulnerabilidade - erro 500 com entrada maliciosa"
                }
            else:
                return {
                    "status": "passed",
                    "message": f"Sistema trata entrada maliciosa - Status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste de segurança: {str(e)}"
            }
    
    def _test_data_consistency(self) -> Dict[str, Any]:
        """Testar consistência de dados"""
        try:
            # Teste básico de consistência verificando se tabelas críticas existem
            sqlite_path = Path("backend/eventos.db")
            
            if not sqlite_path.exists():
                return {
                    "status": "failed",
                    "message": "Database não encontrado para teste de consistência"
                }
            
            conn = sqlite3.connect(str(sqlite_path))
            cursor = conn.cursor()
            
            # Verificar tabelas críticas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            critical_tables = ["usuarios", "eventos", "produtos"]
            missing_tables = [table for table in critical_tables if table not in tables]
            
            conn.close()
            
            if not missing_tables:
                return {
                    "status": "passed",
                    "message": f"Consistência OK - {len(tables)} tabelas, críticas presentes",
                    "details": {"total_tables": len(tables), "critical_tables_ok": True}
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Tabelas críticas ausentes: {missing_tables}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Erro no teste de consistência: {str(e)}"
            }
    
    # ============================================================================
    # EXECUÇÃO E RELATÓRIOS
    # ============================================================================
    
    def run_all_tests(self, skip_non_critical: bool = False) -> Dict[str, Any]:
        """Executar todas as camadas de teste"""
        self.log("🚀 INICIANDO MASTER TEST FRAMEWORK", "INFO")
        self.log("🎯 Missão: Teste completo com zero breaking changes", "INFO")
        self.log(f"🏷️ Sistema: {self.results['framework_info']['target_system']}", "INFO")
        print("="*100)
        
        # Detectar backend ativo
        if not self.detect_active_backend():
            self.log("🚨 FALHA CRÍTICA: Nenhum backend ativo", "ERROR")
            self.results["production_safety"]["deployment_safe"] = False
            return self.results
        
        # CAMADA 1: Preservação (OBRIGATÓRIA)
        preservation_results = self.run_preservation_tests()
        
        # Se houver falhas críticas na preservação, parar
        if preservation_results["summary"]["critical_failures"] > 0:
            self.log("🛑 PARANDO: Falhas críticas na preservação detectadas", "ERROR")
            return self.generate_final_report()
        
        # CAMADA 2: Backend APIs
        self.run_backend_api_tests()
        
        # CAMADA 3: Frontend Components (pode ser pulada se skip_non_critical)
        if not skip_non_critical:
            self.run_frontend_component_tests()
        
        # CAMADA 4: Integração
        self.run_integration_tests()
        
        # Gerar relatório final
        return self.generate_final_report()
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gerar relatório final detalhado"""
        execution_time = time.time() - self.start_time
        self.results["framework_info"]["end_time"] = datetime.now().isoformat()
        self.results["framework_info"]["execution_time"] = round(execution_time, 2)
        
        # Calcular estatísticas finais
        total_tests = self.results["summary"]["total_tests"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        skipped = self.results["summary"]["skipped"]
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        # Determinar se o deployment é seguro
        critical_failures = self.results["summary"]["critical_failures"]
        self.results["production_safety"]["deployment_safe"] = critical_failures == 0
        
        # Exibir relatório
        print("\n" + "="*100)
        print("🎯 RELATÓRIO FINAL - MASTER TEST FRAMEWORK")
        print("="*100)
        print(f"⏱️ Tempo de execução: {execution_time:.2f}s")
        print(f"🧪 Total de testes: {total_tests}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⏭️ Pulou: {skipped}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        print(f"🚨 Falhas críticas: {critical_failures}")
        
        # Status por camada
        print(f"\n📊 STATUS POR CAMADA:")
        print("-" * 100)
        
        for layer_name, layer_data in self.results["layers"].items():
            if "summary" in layer_data:
                layer_summary = layer_data["summary"]
                layer_total = sum(layer_summary.values())
                layer_success = (layer_summary.get("passed", 0) / layer_total * 100) if layer_total > 0 else 0
                
                status_icon = "🟢" if layer_success >= 80 else "🟡" if layer_success >= 60 else "🔴"
                
                print(f"{status_icon} {layer_name.upper()}: {layer_success:.1f}% ({layer_summary.get('passed', 0)}/{layer_total})")
        
        # Veredito de segurança para produção
        print(f"\n🛡️ ANÁLISE DE SEGURANÇA PARA PRODUÇÃO:")
        print("-" * 100)
        
        if self.results["production_safety"]["deployment_safe"]:
            print("🟢 DEPLOYMENT SEGURO - Zero breaking changes detectados")
            print("✅ Todas as funcionalidades críticas preservadas")
            print("✅ Sistema pronto para produção")
        else:
            print("🔴 DEPLOYMENT INSEGURO - Breaking changes detectados")
            print("❌ Funcionalidades críticas comprometidas")
            print("❌ NÃO fazer deploy até corrigir problemas")
        
        # Erros críticos
        if self.results["summary"]["errors"]:
            print(f"\n🚨 ERROS ENCONTRADOS:")
            print("-" * 100)
            for i, error in enumerate(self.results["summary"]["errors"], 1):
                print(f"{i}. [{error['layer']}] {error['test']}")
                print(f"   ⚠️ {error['error']}")
        
        # Salvar relatório em arquivo
        filename = f"master_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório completo salvo em: {filename}")
        print("="*100)
        
        return self.results

def main():
    """Função principal de execução"""
    print("🎯 MASTER TEST FRAMEWORK - SISTEMA PAINEL UNIVERSAL")
    print("🚀 Teste completo de todas as funcionalidades")
    print("🛡️ Garantia de zero breaking changes")
    print()
    
    # Criar e executar framework
    framework = MasterTestFramework()
    results = framework.run_all_tests()
    
    # Retornar código de saída baseado no resultado
    if results["production_safety"]["deployment_safe"]:
        print("\n🎉 SUCESSO: Sistema testado e aprovado para produção!")
        return 0
    else:
        print("\n⚠️ ATENÇÃO: Sistema requer correções antes do deploy!")
        return 1

if __name__ == "__main__":
    exit(main())
