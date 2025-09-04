#!/usr/bin/env python3
"""
MOTOR DE CORRECAO AUTOMATICA - SISTEMA CESAR
Sistema inteligente que detecta problemas e aplica correcoes automaticas
"""

import asyncio
import json
import time
import httpx
import psutil
import logging
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_fix.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoFixEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.meep_url = "http://localhost:3000"
        self.paineluniversal_backend_url = "http://localhost:8000"
        self.paineluniversal_frontend_url = "http://localhost:5173"
        
        self.fixes_applied = []
        self.detection_results = {}
        
    async def detect_problems(self):
        """Detectar problemas no sistema"""
        logger.info("[AUTOFIX] Detectando problemas no sistema...")
        
        problems = {
            "services_down": [],
            "authentication_issues": [],
            "database_issues": [],
            "configuration_issues": [],
            "dependency_issues": []
        }
        
        # 1. Verificar servicos
        services = {
            "MEEP Enterprise": self.meep_url,
            "PainelUniversal Backend": self.paineluniversal_backend_url,
            "PainelUniversal Frontend": self.paineluniversal_frontend_url
        }
        
        for service_name, url in services.items():
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    if "frontend" in service_name.lower():
                        response = await client.get(url)
                    else:
                        response = await client.get(f"{url}/docs")
                    
                    if response.status_code != 200:
                        problems["services_down"].append({
                            "service": service_name,
                            "url": url,
                            "status_code": response.status_code,
                            "fixable": True
                        })
                        
            except Exception as e:
                problems["services_down"].append({
                    "service": service_name,
                    "url": url,
                    "error": str(e),
                    "fixable": True
                })
        
        # 2. Verificar autenticacao
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Testar login MEEP
                meep_login = await client.post(
                    f"{self.meep_url}/api/auth/login",
                    json={"email": "admin@meep.com", "senha": "admin123"}
                )
                
                if meep_login.status_code != 200:
                    problems["authentication_issues"].append({
                        "system": "MEEP",
                        "issue": f"Login failed: HTTP {meep_login.status_code}",
                        "fixable": True
                    })
        except Exception as e:
            problems["authentication_issues"].append({
                "system": "MEEP",
                "issue": f"Login error: {e}",
                "fixable": False
            })
        
        # 3. Verificar banco de dados
        db_file = self.base_dir / "backend" / "eventos.db"
        if not db_file.exists():
            problems["database_issues"].append({
                "issue": "Database file missing",
                "path": str(db_file),
                "fixable": True
            })
        
        # 4. Verificar configuracoes
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            problems["configuration_issues"].append({
                "issue": "Environment file missing",
                "path": str(env_file),
                "fixable": True
            })
        
        # 5. Verificar dependencias Python
        try:
            import fastapi
            import uvicorn
            import sqlalchemy
        except ImportError as e:
            problems["dependency_issues"].append({
                "issue": f"Missing Python dependency: {e}",
                "fixable": True
            })
        
        self.detection_results = problems
        logger.info(f"[AUTOFIX] Detectados {sum(len(v) for v in problems.values())} problemas")
        
        return problems
    
    async def fix_services_down(self, services_down):
        """Corrigir servicos que estao down"""
        logger.info("[AUTOFIX] Corrigindo servicos offline...")
        
        fixes = []
        
        for service in services_down:
            service_name = service["service"]
            
            try:
                if "Backend" in service_name:
                    # Tentar iniciar backend
                    logger.info(f"[AUTOFIX] Iniciando {service_name}...")
                    
                    # Verificar se ja esta rodando
                    backend_running = False
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if proc.info['cmdline'] and 'uvicorn' in str(proc.info['cmdline']):
                            backend_running = True
                            break
                    
                    if not backend_running:
                        backend_dir = self.base_dir / "backend"
                        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
                        subprocess.Popen(cmd, cwd=backend_dir)
                        
                        # Aguardar inicializacao
                        await asyncio.sleep(5)
                        
                        # Verificar se funcionou
                        async with httpx.AsyncClient(timeout=5) as client:
                            try:
                                response = await client.get(f"{self.paineluniversal_backend_url}/docs")
                                if response.status_code == 200:
                                    fixes.append(f"Backend {service_name} iniciado com sucesso")
                                    logger.info(f"[AUTOFIX] {service_name} corrigido")
                                else:
                                    logger.warning(f"[AUTOFIX] {service_name} ainda com problemas")
                            except:
                                logger.warning(f"[AUTOFIX] {service_name} ainda nao acessivel")
                    else:
                        fixes.append(f"{service_name} ja estava rodando")
                
                elif "Frontend" in service_name:
                    # Verificar se frontend esta rodando
                    frontend_running = False
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if proc.info['cmdline'] and ('vite' in str(proc.info['cmdline']) or 'npm' in str(proc.info['cmdline'])):
                            frontend_running = True
                            break
                    
                    if not frontend_running:
                        logger.info(f"[AUTOFIX] Iniciando {service_name}...")
                        frontend_dir = self.base_dir / "frontend"
                        cmd = ["npm", "run", "dev"]
                        subprocess.Popen(cmd, cwd=frontend_dir, shell=True)
                        fixes.append(f"Frontend {service_name} iniciado")
                        logger.info(f"[AUTOFIX] {service_name} iniciado")
                    else:
                        fixes.append(f"{service_name} ja estava rodando")
                
                elif "MEEP" in service_name:
                    # MEEP Enterprise - verificar se processo existe
                    meep_running = False
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if proc.info['cmdline'] and 'meep' in str(proc.info['cmdline']).lower():
                            meep_running = True
                            break
                    
                    if not meep_running:
                        # Tentar iniciar MEEP se existe
                        meep_main_dir = Path(__file__).parent.parent.parent
                        meep_file = meep_main_dir / "meep-integrated-system.js"
                        if meep_file.exists():
                            logger.info(f"[AUTOFIX] Iniciando {service_name}...")
                            cmd = ["node", str(meep_file)]
                            subprocess.Popen(cmd, cwd=meep_main_dir)
                            fixes.append(f"MEEP {service_name} iniciado")
                            logger.info(f"[AUTOFIX] {service_name} iniciado")
                        else:
                            fixes.append(f"MEEP system file not found: {meep_file}")
                    else:
                        fixes.append(f"{service_name} ja estava rodando")
                        
            except Exception as e:
                logger.error(f"[AUTOFIX] Erro ao corrigir {service_name}: {e}")
                fixes.append(f"Erro ao corrigir {service_name}: {e}")
        
        return fixes
    
    async def fix_database_issues(self, db_issues):
        """Corrigir problemas do banco de dados"""
        logger.info("[AUTOFIX] Corrigindo problemas do banco de dados...")
        
        fixes = []
        
        for issue in db_issues:
            if "Database file missing" in issue["issue"]:
                try:
                    # Criar banco de dados
                    db_path = Path(issue["path"])
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Executar script de criacao do banco
                    backend_dir = self.base_dir / "backend"
                    create_script = backend_dir / "create_sqlite_db.py"
                    
                    if create_script.exists():
                        result = subprocess.run(
                            [sys.executable, str(create_script)],
                            cwd=backend_dir,
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            fixes.append("Database criado com sucesso")
                            logger.info("[AUTOFIX] Database criado")
                        else:
                            fixes.append(f"Erro ao criar database: {result.stderr}")
                            logger.error(f"[AUTOFIX] Erro ao criar database: {result.stderr}")
                    else:
                        # Criar database basico
                        import sqlite3
                        conn = sqlite3.connect(db_path)
                        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
                        conn.close()
                        fixes.append("Database basico criado")
                        logger.info("[AUTOFIX] Database basico criado")
                        
                except Exception as e:
                    fixes.append(f"Erro ao criar database: {e}")
                    logger.error(f"[AUTOFIX] Erro ao criar database: {e}")
        
        return fixes
    
    async def fix_configuration_issues(self, config_issues):
        """Corrigir problemas de configuracao"""
        logger.info("[AUTOFIX] Corrigindo problemas de configuracao...")
        
        fixes = []
        
        for issue in config_issues:
            if "Environment file missing" in issue["issue"]:
                try:
                    env_path = Path(issue["path"])
                    
                    # Criar .env basico
                    env_content = '''# Configuracao basica gerada automaticamente
DATABASE_URL=sqlite:///./eventos.db
DATABASE_TYPE=sqlite
SECRET_KEY=auto_generated_secret_key_for_development
JWT_SECRET=auto_generated_jwt_secret_for_development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
DEBUG=true
FRONTEND_URL=http://localhost:5173
VITE_API_URL=http://localhost:8000
'''
                    
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.write(env_content)
                    
                    fixes.append("Arquivo .env criado automaticamente")
                    logger.info("[AUTOFIX] Arquivo .env criado")
                    
                except Exception as e:
                    fixes.append(f"Erro ao criar .env: {e}")
                    logger.error(f"[AUTOFIX] Erro ao criar .env: {e}")
        
        return fixes
    
    async def fix_dependency_issues(self, dep_issues):
        """Corrigir problemas de dependencias"""
        logger.info("[AUTOFIX] Corrigindo problemas de dependencias...")
        
        fixes = []
        
        for issue in dep_issues:
            try:
                # Tentar instalar dependencias faltantes
                missing_package = issue["issue"].split(":")[1].strip().replace("'", "")
                
                logger.info(f"[AUTOFIX] Instalando {missing_package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", missing_package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    fixes.append(f"Dependencia {missing_package} instalada")
                    logger.info(f"[AUTOFIX] {missing_package} instalado")
                else:
                    fixes.append(f"Erro ao instalar {missing_package}: {result.stderr}")
                    logger.error(f"[AUTOFIX] Erro ao instalar {missing_package}")
                    
            except Exception as e:
                fixes.append(f"Erro ao processar dependencia: {e}")
                logger.error(f"[AUTOFIX] Erro ao processar dependencia: {e}")
        
        return fixes
    
    async def apply_all_fixes(self):
        """Aplicar todas as correcoes necessarias"""
        logger.info("[AUTOFIX] Iniciando motor de correcao automatica...")
        
        # 1. Detectar problemas
        problems = await self.detect_problems()
        
        if not any(problems.values()):
            logger.info("[AUTOFIX] Nenhum problema detectado!")
            return {"message": "Sistema saudavel, nenhuma correcao necessaria"}
        
        # 2. Aplicar correcoes
        all_fixes = []
        
        # Corrigir servicos
        if problems["services_down"]:
            service_fixes = await self.fix_services_down(problems["services_down"])
            all_fixes.extend(service_fixes)
        
        # Corrigir banco de dados
        if problems["database_issues"]:
            db_fixes = await self.fix_database_issues(problems["database_issues"])
            all_fixes.extend(db_fixes)
        
        # Corrigir configuracoes
        if problems["configuration_issues"]:
            config_fixes = await self.fix_configuration_issues(problems["configuration_issues"])
            all_fixes.extend(config_fixes)
        
        # Corrigir dependencias
        if problems["dependency_issues"]:
            dep_fixes = await self.fix_dependency_issues(problems["dependency_issues"])
            all_fixes.extend(dep_fixes)
        
        # 3. Aguardar sistemas reiniciarem
        logger.info("[AUTOFIX] Aguardando sistemas reiniciarem...")
        await asyncio.sleep(10)
        
        # 4. Verificar se correcoes funcionaram
        logger.info("[AUTOFIX] Verificando se correcoes funcionaram...")
        problems_after = await self.detect_problems()
        
        total_before = sum(len(v) for v in problems.values())
        total_after = sum(len(v) for v in problems_after.values())
        
        # 5. Gerar relatorio
        fix_report = {
            "timestamp": datetime.now().isoformat(),
            "problems_detected": problems,
            "fixes_applied": all_fixes,
            "problems_before": total_before,
            "problems_after": total_after,
            "improvement": total_before - total_after,
            "success_rate": f"{((total_before - total_after) / max(total_before, 1)) * 100:.1f}%"
        }
        
        # Salvar relatorio
        report_path = self.base_dir / "automation" / "fixes" / f"autofix_report_{int(time.time())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(fix_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[AUTOFIX] Relatorio de correcoes salvo: {report_path}")
        
        # Exibir resultado
        print("\n" + "="*70)
        print("MOTOR DE CORRECAO AUTOMATICA - RESULTADO")
        print("="*70)
        print(f"Problemas Detectados: {total_before}")
        print(f"Problemas Resolvidos: {total_before - total_after}")
        print(f"Problemas Restantes: {total_after}")
        print(f"Taxa de Sucesso: {fix_report['success_rate']}")
        print(f"Correcoes Aplicadas: {len(all_fixes)}")
        print("="*70)
        
        for fix in all_fixes:
            print(f"OK {fix}")
        
        print("="*70)
        print(f"Relatorio completo: {report_path}")
        
        return fix_report

async def main():
    """Funcao principal"""
    engine = AutoFixEngine()
    await engine.apply_all_fixes()

if __name__ == "__main__":
    asyncio.run(main())