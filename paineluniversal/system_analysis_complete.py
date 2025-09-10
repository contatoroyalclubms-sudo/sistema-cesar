#!/usr/bin/env python3
"""
Sistema Universal V6 - Análise Completa do Sistema
Verifica tudo que falta implementar sem alterar nada
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class SystemAnalyzer:
    def __init__(self):
        self.base_path = Path.cwd()
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "system_version": "v6",
            "analysis_results": {}
        }
        
    def check_python_environment(self) -> Dict[str, Any]:
        """Verifica ambiente Python e dependências"""
        result = {
            "python_version": sys.version,
            "poetry_available": False,
            "pip_available": False,
            "virtual_env": os.environ.get("VIRTUAL_ENV", None) is not None,
            "dependencies_status": {}
        }
        
        # Check Poetry
        try:
            poetry_version = subprocess.run(
                ["poetry", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if poetry_version.returncode == 0:
                result["poetry_available"] = True
                result["poetry_version"] = poetry_version.stdout.strip()
        except:
            pass
            
        # Check pip
        try:
            pip_version = subprocess.run(
                ["pip", "--version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if pip_version.returncode == 0:
                result["pip_available"] = True
                result["pip_version"] = pip_version.stdout.strip()
        except:
            pass
            
        return result
        
    def check_node_environment(self) -> Dict[str, Any]:
        """Verifica ambiente Node.js"""
        result = {
            "node_version": None,
            "npm_version": None,
            "yarn_available": False,
            "node_modules_exists": False
        }
        
        try:
            node_version = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if node_version.returncode == 0:
                result["node_version"] = node_version.stdout.strip()
        except:
            pass
            
        try:
            npm_version = subprocess.run(
                ["npm", "--version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if npm_version.returncode == 0:
                result["npm_version"] = npm_version.stdout.strip()
        except:
            pass
            
        # Check node_modules
        frontend_path = self.base_path / "frontend" / "node_modules"
        result["node_modules_exists"] = frontend_path.exists()
        
        return result
        
    def analyze_backend_structure(self) -> Dict[str, Any]:
        """Analisa estrutura do backend"""
        backend_path = self.base_path / "backend"
        
        result = {
            "exists": backend_path.exists(),
            "main_files": {},
            "routers": [],
            "services": [],
            "models_count": 0,
            "endpoints_estimate": 0,
            "database": {
                "sqlite_exists": False,
                "postgresql_configured": False
            }
        }
        
        if not backend_path.exists():
            return result
            
        # Check main files
        main_files = [
            "app/main.py",
            "app/models.py", 
            "app/schemas.py",
            "app/auth.py",
            "app/database.py",
            "pyproject.toml",
            ".env"
        ]
        
        for file in main_files:
            file_path = backend_path / file
            result["main_files"][file] = file_path.exists()
            
        # Count routers
        routers_path = backend_path / "app" / "routers"
        if routers_path.exists():
            result["routers"] = [f.name for f in routers_path.glob("*.py") if f.name != "__init__.py"]
            result["endpoints_estimate"] = len(result["routers"]) * 5  # Estimate 5 endpoints per router
            
        # Count services
        services_path = backend_path / "app" / "services"
        if services_path.exists():
            result["services"] = [f.name for f in services_path.glob("*.py") if f.name != "__init__.py"]
            
        # Check database
        result["database"]["sqlite_exists"] = (backend_path / "eventos.db").exists()
        
        # Check for PostgreSQL config in .env
        env_file = backend_path / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                result["database"]["postgresql_configured"] = "DATABASE_URL" in content and "postgresql" in content
                
        return result
        
    def analyze_frontend_structure(self) -> Dict[str, Any]:
        """Analisa estrutura do frontend"""
        frontend_path = self.base_path / "frontend"
        
        result = {
            "exists": frontend_path.exists(),
            "main_files": {},
            "components": [],
            "contexts": [],
            "build_exists": False,
            "dist_exists": False,
            "dependencies_count": 0
        }
        
        if not frontend_path.exists():
            return result
            
        # Check main files
        main_files = [
            "src/main.tsx",
            "src/App.tsx",
            "src/lib/api.ts",
            "src/lib/utils.ts",
            "package.json",
            "vite.config.ts",
            "tsconfig.json",
            "tailwind.config.js"
        ]
        
        for file in main_files:
            file_path = frontend_path / file
            result["main_files"][file] = file_path.exists()
            
        # Count components
        components_path = frontend_path / "src" / "components"
        if components_path.exists():
            result["components"] = [d.name for d in components_path.iterdir() if d.is_dir()]
            
        # Count contexts
        contexts_path = frontend_path / "src" / "contexts"
        if contexts_path.exists():
            result["contexts"] = [f.name for f in contexts_path.glob("*.tsx")]
            
        # Check build
        result["build_exists"] = (frontend_path / "build").exists()
        result["dist_exists"] = (frontend_path / "dist").exists()
        
        # Count dependencies
        package_json = frontend_path / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                result["dependencies_count"] = len(deps) + len(dev_deps)
                
        return result
        
    def check_missing_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identifica funcionalidades faltantes baseado na análise V6"""
        missing = {
            "critical": [
                {
                    "name": "2FA Authentication",
                    "description": "Two-factor authentication not implemented",
                    "estimated_days": 3,
                    "priority": "HIGH",
                    "files_to_modify": ["app/auth.py", "app/models.py", "app/schemas.py"]
                },
                {
                    "name": "Automated Backup",
                    "description": "No automated PostgreSQL backup system",
                    "estimated_days": 2,
                    "priority": "CRITICAL",
                    "files_to_create": ["scripts/backup.sh", "app/services/backup.py"]
                },
                {
                    "name": "CI/CD Pipeline",
                    "description": "No GitHub Actions workflow",
                    "estimated_days": 3,
                    "priority": "HIGH",
                    "files_to_create": [".github/workflows/ci.yml", ".github/workflows/deploy.yml"]
                }
            ],
            "important": [
                {
                    "name": "Message Queue System",
                    "description": "RabbitMQ/Kafka not configured, Celery missing",
                    "estimated_days": 2,
                    "priority": "MEDIUM",
                    "files_to_create": ["app/celery.py", "app/tasks.py"]
                },
                {
                    "name": "APM Monitoring",
                    "description": "No New Relic/Datadog integration",
                    "estimated_days": 2,
                    "priority": "MEDIUM",
                    "files_to_modify": ["app/main.py"]
                },
                {
                    "name": "Test Coverage",
                    "description": "Coverage below 50%, missing integration tests",
                    "estimated_days": 5,
                    "priority": "MEDIUM",
                    "files_to_create": ["tests/test_integration/", "tests/test_load/"]
                },
                {
                    "name": "Advanced Caching",
                    "description": "Redis underutilized, no query cache",
                    "estimated_days": 2,
                    "priority": "MEDIUM",
                    "files_to_modify": ["app/database.py", "app/cache.py"]
                }
            ],
            "features": [
                {
                    "name": "PIX Integration",
                    "description": "Manual only, no dynamic QR codes",
                    "estimated_days": 3,
                    "priority": "HIGH",
                    "files_to_create": ["app/services/pix.py", "app/routers/pix.py"]
                },
                {
                    "name": "i18n Support",
                    "description": "Portuguese only, no localization",
                    "estimated_days": 3,
                    "priority": "LOW",
                    "files_to_create": ["locales/", "app/i18n.py"]
                },
                {
                    "name": "Webhooks System",
                    "description": "Not configurable via UI",
                    "estimated_days": 2,
                    "priority": "LOW",
                    "files_to_create": ["app/webhooks.py", "app/routers/webhooks.py"]
                },
                {
                    "name": "Audit Trail",
                    "description": "Basic logging only, no compliance features",
                    "estimated_days": 2,
                    "priority": "MEDIUM",
                    "files_to_create": ["app/audit.py", "app/models/audit.py"]
                },
                {
                    "name": "CDN Integration",
                    "description": "Assets served locally, no image optimization",
                    "estimated_days": 1,
                    "priority": "LOW",
                    "files_to_modify": ["vite.config.ts", "nginx.conf"]
                }
            ]
        }
        
        return missing
        
    def check_security_issues(self) -> Dict[str, Any]:
        """Verifica problemas de segurança"""
        issues = {
            "env_files_exposed": [],
            "default_credentials": [],
            "missing_security_headers": True,
            "cors_too_permissive": False,
            "jwt_expiry_too_long": False
        }
        
        # Check for exposed env files
        env_patterns = [".env", ".env.local", ".env.production"]
        for pattern in env_patterns:
            for env_file in self.base_path.rglob(pattern):
                if not any(part.startswith('.') for part in env_file.parts[:-1]):
                    issues["env_files_exposed"].append(str(env_file.relative_to(self.base_path)))
                    
        # Check for default credentials in code
        code_files = list(self.base_path.rglob("*.py")) + list(self.base_path.rglob("*.ts")) + list(self.base_path.rglob("*.tsx"))
        
        default_patterns = [
            ("admin", "admin123"),
            ("00000000000", "admin123"),
            ("test", "test123")
        ]
        
        for file in code_files[:50]:  # Limit to first 50 files for performance
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for user, pwd in default_patterns:
                        if user in content and pwd in content:
                            issues["default_credentials"].append({
                                "file": str(file.relative_to(self.base_path)),
                                "credentials": f"{user}:{pwd}"
                            })
            except:
                pass
                
        return issues
        
    def estimate_completion(self) -> Dict[str, Any]:
        """Estima o percentual de conclusão do sistema"""
        backend = self.analyze_backend_structure()
        frontend = self.analyze_frontend_structure()
        missing = self.check_missing_features()
        
        # Calculate completion based on existing vs missing
        total_features = 50  # Based on V6 analysis
        missing_count = len(missing["critical"]) + len(missing["important"]) + len(missing["features"])
        implemented_count = total_features - missing_count
        
        completion = {
            "overall_percentage": round((implemented_count / total_features) * 100, 2),
            "backend_ready": all(backend["main_files"].values()) if backend["exists"] else False,
            "frontend_ready": all(frontend["main_files"].values()) if frontend["exists"] else False,
            "database_ready": backend["database"]["sqlite_exists"] or backend["database"]["postgresql_configured"],
            "production_ready": False,  # Missing critical features
            "estimated_days_to_complete": sum([
                sum(f["estimated_days"] for f in missing["critical"]),
                sum(f["estimated_days"] for f in missing["important"]),
                sum(f["estimated_days"] for f in missing["features"])
            ])
        }
        
        return completion
        
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo"""
        print("[SEARCH] Iniciando analise completa do Sistema Universal V6...")
        
        print("[PYTHON] Verificando ambiente Python...")
        self.report["analysis_results"]["python_env"] = self.check_python_environment()
        
        print("[NODE] Verificando ambiente Node.js...")
        self.report["analysis_results"]["node_env"] = self.check_node_environment()
        
        print("[BACKEND] Analisando estrutura do backend...")
        self.report["analysis_results"]["backend"] = self.analyze_backend_structure()
        
        print("[FRONTEND] Analisando estrutura do frontend...")
        self.report["analysis_results"]["frontend"] = self.analyze_frontend_structure()
        
        print("[MISSING] Identificando funcionalidades faltantes...")
        self.report["analysis_results"]["missing_features"] = self.check_missing_features()
        
        print("[SECURITY] Verificando problemas de seguranca...")
        self.report["analysis_results"]["security"] = self.check_security_issues()
        
        print("[STATS] Calculando estimativa de conclusao...")
        self.report["analysis_results"]["completion"] = self.estimate_completion()
        
        return self.report
        
    def save_report(self, filename: str = "system_analysis_report.json"):
        """Salva relatório em arquivo JSON"""
        report_path = self.base_path / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"[OK] Relatorio salvo em: {report_path}")
        return report_path
        
    def print_summary(self):
        """Imprime resumo da análise"""
        completion = self.report["analysis_results"]["completion"]
        missing = self.report["analysis_results"]["missing_features"]
        
        print("\n" + "="*60)
        print(" RESUMO DA ANALISE - SISTEMA UNIVERSAL V6")
        print("="*60)
        
        print(f"\n[OK] Completude Geral: {completion['overall_percentage']}%")
        print(f"[INFO] Backend Pronto: {'Sim' if completion['backend_ready'] else 'Nao'}")
        print(f"[INFO] Frontend Pronto: {'Sim' if completion['frontend_ready'] else 'Nao'}")
        print(f"[INFO] Banco de Dados: {'Configurado' if completion['database_ready'] else 'Nao configurado'}")
        print(f"[INFO] Pronto para Producao: {'Sim' if completion['production_ready'] else 'Nao'}")
        
        print(f"\n[TIME] Tempo estimado para 100%: {completion['estimated_days_to_complete']} dias")
        
        print("\n[CRITICAL] Funcionalidades Criticas Faltantes:")
        for feature in missing["critical"]:
            print(f"   - {feature['name']} ({feature['estimated_days']} dias)")
            
        print("\n[IMPORTANT] Funcionalidades Importantes Faltantes:")
        for feature in missing["important"]:
            print(f"   - {feature['name']} ({feature['estimated_days']} dias)")
            
        print("\n[FEATURES] Outras Funcionalidades Faltantes:")
        for feature in missing["features"]:
            print(f"   - {feature['name']} ({feature['estimated_days']} dias)")
            
        security = self.report["analysis_results"]["security"]
        if security["env_files_exposed"]:
            print(f"\n[WARNING] ALERTA: {len(security['env_files_exposed'])} arquivos .env expostos!")
        if security["default_credentials"]:
            print(f"[WARNING] ALERTA: {len(security['default_credentials'])} credenciais padrao encontradas!")
            
        print("\n" + "="*60)
        
if __name__ == "__main__":
    analyzer = SystemAnalyzer()
    analyzer.generate_report()
    analyzer.save_report()
    analyzer.print_summary()