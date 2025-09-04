#!/usr/bin/env python3
"""
SISTEMA DE AUTOMAÇÃO COMPLETA - NÍVEL 1
Sistema de monitoramento, testes e correções automáticas para o projeto Sistema Cesar
"""

import asyncio
import json
import time
import httpx
import psutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import sys
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemAutomation:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.status = {
            "backend": False,
            "frontend": False,
            "database": False,
            "overall_health": "unknown"
        }
        self.modules_status = {}
        self.error_count = 0
        self.last_check = None
        
    async def initialize(self):
        """Inicializar sistema de automação"""
        logger.info("🚀 Inicializando Sistema de Automação Completa")
        
        # Criar diretórios necessários
        (self.base_dir / "automation" / "logs").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "automation" / "reports").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "automation" / "fixes").mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Estrutura de automação criada")
        
    async def health_check_complete(self):
        """Health check completo do sistema"""
        logger.info("🔍 Executando health check completo...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "system": {},
            "modules": {},
            "errors": []
        }
        
        try:
            # 1. Verificar Backend FastAPI
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{self.backend_url}/docs")
                    if response.status_code == 200:
                        results["services"]["backend"] = {
                            "status": "healthy",
                            "url": self.backend_url,
                            "response_time": response.elapsed.total_seconds()
                        }
                        self.status["backend"] = True
                    else:
                        results["services"]["backend"] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}"
                        }
                        self.status["backend"] = False
            except Exception as e:
                results["services"]["backend"] = {
                    "status": "error",
                    "error": str(e)
                }
                results["errors"].append(f"Backend error: {e}")
                self.status["backend"] = False
            
            # 2. Verificar Frontend Vite
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(self.frontend_url)
                    if response.status_code == 200:
                        results["services"]["frontend"] = {
                            "status": "healthy",
                            "url": self.frontend_url,
                            "response_time": response.elapsed.total_seconds()
                        }
                        self.status["frontend"] = True
                    else:
                        results["services"]["frontend"] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}"
                        }
                        self.status["frontend"] = False
            except Exception as e:
                results["services"]["frontend"] = {
                    "status": "error",
                    "error": str(e)
                }
                results["errors"].append(f"Frontend error: {e}")
                self.status["frontend"] = False
            
            # 3. Verificar Sistema (CPU, Memory, Disk)
            results["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "processes": len(psutil.pids())
            }
            
            # 4. Verificar APIs específicas do sistema
            api_endpoints = [
                "/api/auth/me",
                "/api/eventos",
                "/api/usuarios", 
                "/api/pdv/status",
                "/api/checkin/status"
            ]
            
            results["modules"] = {}
            for endpoint in api_endpoints:
                try:
                    async with httpx.AsyncClient(timeout=3) as client:
                        response = await client.get(f"{self.backend_url}{endpoint}")
                        module_name = endpoint.split('/')[2]
                        results["modules"][module_name] = {
                            "status": "healthy" if response.status_code in [200, 401] else "unhealthy",
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds()
                        }
                except Exception as e:
                    module_name = endpoint.split('/')[2] 
                    results["modules"][module_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            # 5. Determinar saúde geral
            healthy_services = sum(1 for s in results["services"].values() if s["status"] == "healthy")
            total_services = len(results["services"])
            
            if healthy_services == total_services:
                results["overall_health"] = "healthy"
                self.status["overall_health"] = "healthy"
            elif healthy_services > 0:
                results["overall_health"] = "degraded" 
                self.status["overall_health"] = "degraded"
            else:
                results["overall_health"] = "critical"
                self.status["overall_health"] = "critical"
            
            self.last_check = datetime.now()
            
            # Salvar relatório
            report_file = self.base_dir / "automation" / "reports" / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"✅ Health check completo - Status: {results['overall_health']}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro no health check: {e}")
            results["overall_health"] = "error"
            results["errors"].append(str(e))
            return results
    
    async def module_mapper(self):
        """Mapear todos os módulos do sistema"""
        logger.info("🗺️ Mapeando módulos do sistema...")
        
        modules_map = {
            "authentication": {
                "name": "Sistema de Autenticação",
                "endpoints": ["/api/auth/login", "/api/auth/register", "/api/auth/me"],
                "files": ["backend/app/routers/auth.py", "frontend/src/pages/Login.tsx"],
                "database_tables": ["usuarios"],
                "status": "unknown",
                "priority": "critical"
            },
            "events": {
                "name": "Gestão de Eventos",
                "endpoints": ["/api/eventos", "/api/eventos/{id}"],
                "files": ["backend/app/routers/eventos.py", "frontend/src/pages/Eventos.tsx"],
                "database_tables": ["eventos", "listas"],
                "status": "unknown", 
                "priority": "high"
            },
            "users": {
                "name": "Gestão de Usuários",
                "endpoints": ["/api/usuarios", "/api/usuarios/{id}"],
                "files": ["backend/app/routers/usuarios.py", "frontend/src/pages/Usuarios.tsx"],
                "database_tables": ["usuarios"],
                "status": "unknown",
                "priority": "high"
            },
            "checkin": {
                "name": "Sistema de Check-in",
                "endpoints": ["/api/checkin", "/api/checkin/qr"],
                "files": ["backend/app/routers/checkins.py", "frontend/src/pages/CheckIn.tsx"],
                "database_tables": ["checkins"],
                "status": "unknown",
                "priority": "medium"
            },
            "pdv": {
                "name": "PDV e Vendas",
                "endpoints": ["/api/pdv", "/api/pdv/vendas"],
                "files": ["backend/app/routers/pdv.py", "frontend/src/pages/PDV.tsx"],
                "database_tables": ["vendas", "produtos"],
                "status": "unknown",
                "priority": "high"
            },
            "financial": {
                "name": "Sistema Financeiro", 
                "endpoints": ["/api/financeiro", "/api/financeiro/relatorios"],
                "files": ["backend/app/routers/financeiro.py", "frontend/src/pages/Financeiro.tsx"],
                "database_tables": ["transacoes_financeiras"],
                "status": "unknown",
                "priority": "medium"
            },
            "analytics": {
                "name": "Analytics e Relatórios",
                "endpoints": ["/api/analytics", "/api/relatorios"],
                "files": ["backend/app/routers/analytics.py", "frontend/src/pages/Analytics.tsx"],
                "database_tables": [],
                "status": "unknown",
                "priority": "low"
            },
            "whatsapp": {
                "name": "Integração WhatsApp",
                "endpoints": ["/api/whatsapp", "/api/whatsapp/send"],
                "files": ["backend/app/routers/whatsapp.py"],
                "database_tables": [],
                "status": "unknown",
                "priority": "low"
            }
        }
        
        # Testar cada módulo
        for module_id, module_info in modules_map.items():
            try:
                # Testar endpoints
                endpoint_status = []
                for endpoint in module_info["endpoints"]:
                    try:
                        async with httpx.AsyncClient(timeout=3) as client:
                            response = await client.get(f"{self.backend_url}{endpoint}")
                            endpoint_status.append({
                                "endpoint": endpoint,
                                "status_code": response.status_code,
                                "working": response.status_code in [200, 401, 404]
                            })
                    except Exception as e:
                        endpoint_status.append({
                            "endpoint": endpoint,
                            "error": str(e),
                            "working": False
                        })
                
                # Determinar status do módulo
                working_endpoints = sum(1 for e in endpoint_status if e.get("working", False))
                total_endpoints = len(endpoint_status)
                
                if working_endpoints == total_endpoints:
                    modules_map[module_id]["status"] = "operational"
                elif working_endpoints > 0:
                    modules_map[module_id]["status"] = "partial"
                else:
                    modules_map[module_id]["status"] = "broken"
                
                modules_map[module_id]["endpoint_tests"] = endpoint_status
                
            except Exception as e:
                modules_map[module_id]["status"] = "error"
                modules_map[module_id]["error"] = str(e)
        
        # Salvar mapeamento
        mapping_file = self.base_dir / "automation" / "reports" / "modules_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(modules_map, f, indent=2)
        
        self.modules_status = modules_map
        logger.info(f"✅ Mapeamento completo - {len(modules_map)} módulos identificados")
        return modules_map
    
    async def auto_fix_common_issues(self):
        """Sistema de correção automática"""
        logger.info("🔧 Executando correções automáticas...")
        
        fixes_applied = []
        
        try:
            # 1. Verificar e corrigir permissões
            if os.name != 'nt':  # Unix-like systems
                try:
                    subprocess.run(['chmod', '+x', 'backend/run_server.py'], check=True)
                    fixes_applied.append("Permissões do backend corrigidas")
                except:
                    pass
            
            # 2. Verificar dependências do Python
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    # Tentar instalar dependências faltantes
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], 
                                 check=True)
                    fixes_applied.append("Dependências Python reinstaladas")
            except:
                pass
            
            # 3. Verificar banco de dados
            db_file = self.base_dir / "eventos.db"
            if not db_file.exists():
                try:
                    # Tentar criar banco
                    subprocess.run([sys.executable, 'backend/create_sqlite_db.py'], 
                                 cwd=self.base_dir, check=True)
                    fixes_applied.append("Banco de dados SQLite criado")
                except:
                    pass
            
            # 4. Verificar portas em uso
            try:
                backend_port_free = self.check_port_free(8000)
                frontend_port_free = self.check_port_free(5173)
                
                if not backend_port_free:
                    fixes_applied.append("Porta 8000 em uso - requer intervenção manual")
                if not frontend_port_free:
                    fixes_applied.append("Porta 5173 em uso - requer intervenção manual")
                    
            except:
                pass
            
            if fixes_applied:
                logger.info(f"✅ Correções aplicadas: {len(fixes_applied)}")
                for fix in fixes_applied:
                    logger.info(f"   - {fix}")
            else:
                logger.info("ℹ️ Nenhuma correção automática necessária")
            
            return fixes_applied
            
        except Exception as e:
            logger.error(f"❌ Erro nas correções automáticas: {e}")
            return []
    
    def check_port_free(self, port: int) -> bool:
        """Verificar se porta está livre"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) != 0
        except:
            return False
    
    async def generate_status_report(self):
        """Gerar relatório de status completo"""
        logger.info("📋 Gerando relatório de status...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(self.base_dir)
            },
            "services_status": self.status,
            "modules_status": self.modules_status,
            "last_health_check": self.last_check.isoformat() if self.last_check else None,
            "error_count": self.error_count,
            "recommendations": []
        }
        
        # Adicionar recomendações baseadas no status
        if not self.status["backend"]:
            report["recommendations"].append("Backend não está respondendo - verificar se uvicorn está rodando")
        
        if not self.status["frontend"]:
            report["recommendations"].append("Frontend não está respondendo - verificar se Vite está rodando")
        
        if self.error_count > 10:
            report["recommendations"].append("Muitos erros detectados - considerar reinicialização completa")
        
        # Salvar relatório
        report_file = self.base_dir / "automation" / "reports" / "status_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Relatório de status salvo")
        return report
    
    async def monitor_loop(self, interval: int = 60):
        """Loop principal de monitoramento"""
        logger.info(f"👀 Iniciando monitoramento contínuo (intervalo: {interval}s)")
        
        while True:
            try:
                # Health check
                health_results = await self.health_check_complete()
                
                # Auto-fix se necessário
                if health_results["overall_health"] in ["degraded", "critical"]:
                    await self.auto_fix_common_issues()
                
                # Gerar relatório a cada 10 ciclos
                if hasattr(self, '_cycle_count'):
                    self._cycle_count += 1
                else:
                    self._cycle_count = 1
                
                if self._cycle_count % 10 == 0:
                    await self.generate_status_report()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                self.error_count += 1
                await asyncio.sleep(interval)

async def main():
    """Função principal"""
    automation = SystemAutomation()
    
    try:
        # Inicializar
        await automation.initialize()
        
        # Health check inicial
        health_results = await automation.health_check_complete()
        print(f"\n📊 STATUS INICIAL: {health_results['overall_health'].upper()}")
        
        # Mapear módulos
        modules = await automation.module_mapper()
        print(f"🗺️ MÓDULOS MAPEADOS: {len(modules)}")
        
        # Correções automáticas
        fixes = await automation.auto_fix_common_issues()
        if fixes:
            print(f"🔧 CORREÇÕES APLICADAS: {len(fixes)}")
        
        # Gerar relatório
        report = await automation.generate_status_report()
        print(f"📋 RELATÓRIO GERADO: {report['timestamp']}")
        
        # Opção de monitoramento contínuo
        print("\n🤖 Sistema de automação pronto!")
        print("Para monitoramento contínuo, descomente a linha abaixo:")
        print("# await automation.monitor_loop(60)")
        
        # await automation.monitor_loop(60)  # Monitoramento contínuo
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())