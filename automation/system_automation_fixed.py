#!/usr/bin/env python3
"""
SISTEMA DE AUTOMACAO COMPLETA - NIVEL 1
Sistema de monitoramento, testes e correcoes automaticas para o projeto Sistema Cesar
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
        logging.FileHandler('automation.log', encoding='utf-8'),
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
        """Inicializar sistema de automacao"""
        logger.info("[INIT] Inicializando Sistema de Automacao Completa")
        
        # Criar diretorios necessarios
        (self.base_dir / "automation" / "logs").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "automation" / "reports").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "automation" / "fixes").mkdir(parents=True, exist_ok=True)
        
        logger.info("[INIT] Estrutura de automacao criada")
        
    async def health_check_complete(self):
        """Health check completo do sistema"""
        logger.info("[HEALTH] Executando health check completo...")
        
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
                        logger.info("[HEALTH] Backend: OK")
                    else:
                        results["services"]["backend"] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}"
                        }
                        self.status["backend"] = False
                        logger.warning(f"[HEALTH] Backend: ERRO HTTP {response.status_code}")
            except Exception as e:
                results["services"]["backend"] = {
                    "status": "error",
                    "error": str(e)
                }
                results["errors"].append(f"Backend error: {e}")
                self.status["backend"] = False
                logger.error(f"[HEALTH] Backend: ERRO {e}")
            
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
                        logger.info("[HEALTH] Frontend: OK")
                    else:
                        results["services"]["frontend"] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}"
                        }
                        self.status["frontend"] = False
                        logger.warning(f"[HEALTH] Frontend: ERRO HTTP {response.status_code}")
            except Exception as e:
                results["services"]["frontend"] = {
                    "status": "error",
                    "error": str(e)
                }
                results["errors"].append(f"Frontend error: {e}")
                self.status["frontend"] = False
                logger.error(f"[HEALTH] Frontend: ERRO {e}")
            
            # 3. Verificar Sistema (CPU, Memory, Disk)
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage(str(self.base_dir))
                
                results["system"] = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "processes": len(psutil.pids())
                }
                logger.info(f"[HEALTH] Sistema: CPU {cpu_percent}%, RAM {memory.percent}%, DISK {disk.percent}%")
            except Exception as e:
                logger.error(f"[HEALTH] Sistema: ERRO {e}")
            
            # 4. Verificar APIs especificas do sistema
            api_endpoints = [
                "/api/health",
                "/api/docs",
                "/api/usuarios",
                "/api/eventos"
            ]
            
            results["modules"] = {}
            for endpoint in api_endpoints:
                try:
                    async with httpx.AsyncClient(timeout=3) as client:
                        response = await client.get(f"{self.backend_url}{endpoint}")
                        results["modules"][endpoint] = {
                            "status": "ok" if response.status_code in [200, 401] else "error",
                            "response_code": response.status_code,
                            "response_time": response.elapsed.total_seconds()
                        }
                        if response.status_code in [200, 401]:
                            logger.info(f"[HEALTH] API {endpoint}: OK")
                        else:
                            logger.warning(f"[HEALTH] API {endpoint}: HTTP {response.status_code}")
                except Exception as e:
                    results["modules"][endpoint] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"[HEALTH] API {endpoint}: ERRO {e}")
            
            # Definir saude geral
            healthy_services = sum(1 for s in results["services"].values() if s.get("status") == "healthy")
            total_services = len(results["services"])
            
            if healthy_services == total_services:
                self.status["overall_health"] = "healthy"
                logger.info("[HEALTH] Status Geral: SAUDAVEL")
            elif healthy_services > 0:
                self.status["overall_health"] = "partial"
                logger.warning("[HEALTH] Status Geral: PARCIAL")
            else:
                self.status["overall_health"] = "unhealthy"
                logger.error("[HEALTH] Status Geral: NAO SAUDAVEL")
            
            # Salvar resultado
            report_path = self.base_dir / "automation" / "logs" / f"health_check_{int(time.time())}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[HEALTH] Relatorio salvo: {report_path}")
            self.last_check = datetime.now()
            
            return results
            
        except Exception as e:
            logger.error(f"[HEALTH] Erro geral no health check: {e}")
            return {"error": str(e)}
    
    async def module_mapping(self):
        """Mapeamento completo de modulos do sistema"""
        logger.info("[MAPPING] Iniciando mapeamento de modulos...")
        
        modules = {
            "autenticacao": {
                "endpoints": ["/api/auth/login", "/api/auth/register", "/api/auth/me"],
                "description": "Sistema de autenticacao e usuarios",
                "status": "unknown"
            },
            "eventos": {
                "endpoints": ["/api/eventos", "/api/eventos/{id}"],
                "description": "Gestao de eventos",
                "status": "unknown"
            },
            "checkin": {
                "endpoints": ["/api/checkin", "/api/checkin/{id}"],
                "description": "Sistema de check-in e QR Code",
                "status": "unknown"
            },
            "pdv": {
                "endpoints": ["/api/pdv", "/api/pdv/vendas"],
                "description": "Ponto de venda",
                "status": "unknown"
            },
            "financeiro": {
                "endpoints": ["/api/financeiro", "/api/financeiro/transacoes"],
                "description": "Sistema financeiro",
                "status": "unknown"
            },
            "gamificacao": {
                "endpoints": ["/api/gamificacao", "/api/gamificacao/ranking"],
                "description": "Sistema de gamificacao",
                "status": "unknown"
            }
        }
        
        # Testar cada modulo
        for module_name, module_info in modules.items():
            logger.info(f"[MAPPING] Testando modulo: {module_name}")
            
            working_endpoints = 0
            total_endpoints = len(module_info["endpoints"])
            
            for endpoint in module_info["endpoints"]:
                try:
                    # Substituir {id} por um ID de teste
                    test_endpoint = endpoint.replace("{id}", "1")
                    
                    async with httpx.AsyncClient(timeout=3) as client:
                        response = await client.get(f"{self.backend_url}{test_endpoint}")
                        
                        # Considerar sucesso se retornar 200, 401 (auth necessario), ou 404 (endpoint existe)
                        if response.status_code in [200, 401, 404, 422]:
                            working_endpoints += 1
                            logger.info(f"[MAPPING] {endpoint}: OK ({response.status_code})")
                        else:
                            logger.warning(f"[MAPPING] {endpoint}: HTTP {response.status_code}")
                            
                except Exception as e:
                    logger.error(f"[MAPPING] {endpoint}: ERRO {e}")
            
            # Definir status do modulo
            if working_endpoints == total_endpoints:
                modules[module_name]["status"] = "working"
            elif working_endpoints > 0:
                modules[module_name]["status"] = "partial"
            else:
                modules[module_name]["status"] = "error"
            
            modules[module_name]["working_endpoints"] = working_endpoints
            modules[module_name]["total_endpoints"] = total_endpoints
        
        # Salvar mapeamento
        mapping_path = self.base_dir / "automation" / "logs" / f"module_mapping_{int(time.time())}.json"
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(modules, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[MAPPING] Mapeamento salvo: {mapping_path}")
        self.modules_status = modules
        
        return modules
    
    async def auto_fix_system(self):
        """Sistema de correcao automatica"""
        logger.info("[AUTOFIX] Iniciando sistema de correcao automatica...")
        
        fixes_applied = []
        
        try:
            # 1. Verificar se backend esta rodando
            if not self.status["backend"]:
                logger.info("[AUTOFIX] Tentando iniciar backend...")
                try:
                    # Verificar se ja existe processo
                    backend_process = None
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if 'uvicorn' in str(proc.info['cmdline']):
                            backend_process = proc
                            break
                    
                    if not backend_process:
                        # Iniciar backend
                        backend_dir = self.base_dir / "backend"
                        if backend_dir.exists():
                            cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
                            subprocess.Popen(cmd, cwd=backend_dir)
                            fixes_applied.append("Backend iniciado automaticamente")
                            logger.info("[AUTOFIX] Backend iniciado")
                        else:
                            logger.error("[AUTOFIX] Diretorio backend nao encontrado")
                    else:
                        logger.info("[AUTOFIX] Backend ja esta rodando")
                        
                except Exception as e:
                    logger.error(f"[AUTOFIX] Erro ao iniciar backend: {e}")
            
            # 2. Verificar se frontend esta rodando
            if not self.status["frontend"]:
                logger.info("[AUTOFIX] Tentando iniciar frontend...")
                try:
                    # Verificar se ja existe processo
                    frontend_process = None
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if 'vite' in str(proc.info['cmdline']) or 'npm' in str(proc.info['cmdline']):
                            frontend_process = proc
                            break
                    
                    if not frontend_process:
                        # Iniciar frontend
                        frontend_dir = self.base_dir / "frontend"
                        if frontend_dir.exists():
                            cmd = ["npm", "run", "dev"]
                            subprocess.Popen(cmd, cwd=frontend_dir, shell=True)
                            fixes_applied.append("Frontend iniciado automaticamente")
                            logger.info("[AUTOFIX] Frontend iniciado")
                        else:
                            logger.error("[AUTOFIX] Diretorio frontend nao encontrado")
                    else:
                        logger.info("[AUTOFIX] Frontend ja esta rodando")
                        
                except Exception as e:
                    logger.error(f"[AUTOFIX] Erro ao iniciar frontend: {e}")
            
            # 3. Aguardar servicos iniciarem
            if fixes_applied:
                logger.info("[AUTOFIX] Aguardando servicos iniciarem...")
                await asyncio.sleep(10)
                
                # Verificar novamente
                await self.health_check_complete()
        
        except Exception as e:
            logger.error(f"[AUTOFIX] Erro geral: {e}")
        
        # Salvar resultado
        fix_report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": fixes_applied,
            "system_status": self.status
        }
        
        fix_path = self.base_dir / "automation" / "fixes" / f"autofix_{int(time.time())}.json"
        with open(fix_path, 'w', encoding='utf-8') as f:
            json.dump(fix_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[AUTOFIX] Relatorio salvo: {fix_path}")
        return fixes_applied

    async def run_continuous_monitoring(self):
        """Executar monitoramento continuo"""
        logger.info("[MONITOR] Iniciando monitoramento continuo...")
        
        while True:
            try:
                # Health check
                await self.health_check_complete()
                
                # Se sistema nao esta saudavel, tentar corrigir
                if self.status["overall_health"] != "healthy":
                    logger.warning("[MONITOR] Sistema nao saudavel, tentando corrigir...")
                    await self.auto_fix_system()
                
                # Aguardar proximo ciclo (30 segundos)
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("[MONITOR] Monitoramento interrompido pelo usuario")
                break
            except Exception as e:
                logger.error(f"[MONITOR] Erro no monitoramento: {e}")
                await asyncio.sleep(10)

    async def run_complete_analysis(self):
        """Executar analise completa do sistema"""
        logger.info("[ANALYSIS] Iniciando analise completa do sistema...")
        
        # 1. Inicializar
        await self.initialize()
        
        # 2. Health check
        health_results = await self.health_check_complete()
        
        # 3. Mapeamento de modulos
        module_results = await self.module_mapping()
        
        # 4. Auto-fix se necessario
        if self.status["overall_health"] != "healthy":
            fix_results = await self.auto_fix_system()
        else:
            fix_results = ["Sistema ja esta saudavel"]
        
        # 5. Gerar relatorio final
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "health_check": health_results,
            "module_mapping": module_results,
            "auto_fixes": fix_results,
            "overall_status": self.status
        }
        
        report_path = self.base_dir / "automation" / "reports" / f"complete_analysis_{int(time.time())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[ANALYSIS] Relatorio final salvo: {report_path}")
        
        # Mostrar resumo
        print("\n" + "="*60)
        print("RESUMO DA ANALISE COMPLETA DO SISTEMA")
        print("="*60)
        print(f"Backend: {'OK' if self.status['backend'] else 'ERRO'}")
        print(f"Frontend: {'OK' if self.status['frontend'] else 'ERRO'}")
        print(f"Status Geral: {self.status['overall_health'].upper()}")
        print(f"Modulos Testados: {len(module_results)}")
        print(f"Correcoes Aplicadas: {len(fix_results)}")
        print("="*60)
        
        return final_report

async def main():
    """Funcao principal"""
    automation = SystemAutomation()
    
    # Executar analise completa
    await automation.run_complete_analysis()
    
    # Perguntar se quer monitoramento continuo
    print("\nDeseja executar monitoramento continuo? (y/n): ", end="")
    try:
        import msvcrt
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 'y':
            print("Sim")
            await automation.run_continuous_monitoring()
        else:
            print("Nao")
            print("Automacao finalizada!")
    except:
        print("Automacao finalizada!")

if __name__ == "__main__":
    asyncio.run(main())