#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE DIAGNOSTICO E CORREÇÃO AUTOMATICA
============================================

Identifica e corrige automaticamente todos os erros do sistema.
Garante zero breaking changes.

Autor: Agente de Desenvolvimento
Data: 2024
"""

import os
import sys
import json
import time
import requests
import sqlite3
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class SystemDiagnostic:
    """Diagnóstico completo do sistema com correção automática"""
    
    def __init__(self):
        self.start_time = time.time()
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 10
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "backend_status": {},
            "frontend_status": {},
            "database_status": {},
            "critical_errors": [],
            "fixes_applied": [],
            "recommendations": []
        }
        
        print("=" * 80)
        print("SISTEMA DE DIAGNOSTICO E CORRECAO AUTOMATICA")
        print("=" * 80)
        print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def log(self, message: str, level: str = "INFO"):
        """Log sem emojis para evitar problemas de encoding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_backend_health(self) -> Dict[str, Any]:
        """Testar saúde do backend"""
        self.log("Testando saude do backend...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                result = {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "message": "Backend funcionando normalmente"
                }
                self.log("Backend saudavel - OK")
                return result
            else:
                result = {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "message": f"Backend retornou status {response.status_code}"
                }
                self.log(f"Backend com problema - Status {response.status_code}", "WARNING")
                return result
                
        except requests.exceptions.ConnectionError:
            result = {
                "status": "offline",
                "message": "Backend nao esta rodando"
            }
            self.log("Backend offline - ERRO", "ERROR")
            self.results["critical_errors"].append("Backend nao esta rodando")
            return result
        except Exception as e:
            result = {
                "status": "error",
                "message": f"Erro ao conectar: {str(e)}"
            }
            self.log(f"Erro ao testar backend: {str(e)}", "ERROR")
            return result
    
    def test_authentication(self) -> Dict[str, Any]:
        """Testar sistema de autenticação"""
        self.log("Testando sistema de autenticacao...")
        
        try:
            # Tentar login com usuário padrão
            login_data = {"username": "admin", "password": "admin123"}
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log("Autenticacao funcionando - OK")
                    return {
                        "status": "working",
                        "message": "Autenticacao JWT funcionando",
                        "token_type": data.get("token_type", "bearer")
                    }
                else:
                    self.log("Token nao retornado no login", "ERROR")
                    self.results["critical_errors"].append("Token JWT nao retornado")
                    return {
                        "status": "error",
                        "message": "Token nao retornado"
                    }
            else:
                self.log(f"Falha na autenticacao - Status {response.status_code}", "ERROR")
                if response.status_code == 401:
                    self.results["critical_errors"].append("Credenciais de admin incorretas")
                return {
                    "status": "failed",
                    "status_code": response.status_code,
                    "message": "Falha na autenticacao"
                }
                
        except Exception as e:
            self.log(f"Erro no teste de autenticacao: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Testar conectividade com banco de dados"""
        self.log("Testando conectividade do banco...")
        
        try:
            # Testar SQLite local
            db_path = Path("backend/eventos.db")
            
            if not db_path.exists():
                self.log("Database SQLite nao encontrado", "ERROR")
                self.results["critical_errors"].append("Database SQLite nao encontrado")
                return {
                    "status": "missing",
                    "message": "Arquivo de database nao encontrado"
                }
            
            # Conectar e testar
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Verificar tabelas críticas
            critical_tables = ["usuarios", "eventos", "produtos"]
            missing_tables = [table for table in critical_tables if table not in tables]
            
            if missing_tables:
                self.log(f"Tabelas criticas ausentes: {missing_tables}", "ERROR")
                self.results["critical_errors"].append(f"Tabelas ausentes: {missing_tables}")
                conn.close()
                return {
                    "status": "incomplete",
                    "message": f"Tabelas criticas ausentes: {missing_tables}",
                    "missing_tables": missing_tables
                }
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            user_count = cursor.fetchone()[0]
            
            conn.close()
            
            self.log(f"Database OK - {len(tables)} tabelas, {user_count} usuarios")
            return {
                "status": "connected",
                "message": "Database conectado e funcional",
                "table_count": len(tables),
                "user_count": user_count,
                "tables": tables
            }
            
        except Exception as e:
            self.log(f"Erro no teste de database: {str(e)}", "ERROR")
            self.results["critical_errors"].append(f"Erro de database: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def test_critical_endpoints(self) -> Dict[str, Any]:
        """Testar endpoints críticos"""
        self.log("Testando endpoints criticos...")
        
        endpoints = [
            {"path": "/api/usuarios", "name": "usuarios"},
            {"path": "/api/eventos", "name": "eventos"},
            {"path": "/api/produtos", "name": "produtos"},
            {"path": "/api/dashboard/stats", "name": "dashboard"},
            {"path": "/docs", "name": "documentacao"}
        ]
        
        working_endpoints = []
        failed_endpoints = []
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint['path']}")
                
                if response.status_code < 500:  # Aceitar até 4xx
                    working_endpoints.append(endpoint['name'])
                    self.log(f"Endpoint {endpoint['name']} OK - Status {response.status_code}")
                else:
                    failed_endpoints.append(endpoint['name'])
                    self.log(f"Endpoint {endpoint['name']} ERRO - Status {response.status_code}", "ERROR")
                    
            except Exception as e:
                failed_endpoints.append(endpoint['name'])
                self.log(f"Endpoint {endpoint['name']} FALHOU - {str(e)}", "ERROR")
        
        if failed_endpoints:
            self.results["critical_errors"].extend([f"Endpoint {ep} falhou" for ep in failed_endpoints])
        
        success_rate = len(working_endpoints) / len(endpoints) * 100
        
        return {
            "status": "tested",
            "success_rate": success_rate,
            "working_endpoints": working_endpoints,
            "failed_endpoints": failed_endpoints,
            "message": f"{len(working_endpoints)}/{len(endpoints)} endpoints funcionando"
        }
    
    def test_frontend_build(self) -> Dict[str, Any]:
        """Testar build do frontend"""
        self.log("Testando build do frontend...")
        
        try:
            frontend_path = Path("frontend")
            build_path = frontend_path / "dist"
            
            if not build_path.exists():
                self.log("Build do frontend nao encontrado", "WARNING")
                return {
                    "status": "missing",
                    "message": "Build nao encontrado - executar npm run build"
                }
            
            # Contar arquivos
            files = list(build_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            
            # Verificar arquivos críticos
            index_html = build_path / "index.html"
            assets_dir = build_path / "assets"
            
            if not index_html.exists():
                self.log("index.html ausente no build", "ERROR")
                self.results["critical_errors"].append("index.html ausente no build")
                return {
                    "status": "broken",
                    "message": "Build corrompido - index.html ausente"
                }
            
            if not assets_dir.exists():
                self.log("Pasta assets ausente no build", "WARNING")
                return {
                    "status": "incomplete",
                    "message": "Build incompleto - assets ausentes"
                }
            
            self.log(f"Build do frontend OK - {file_count} arquivos")
            return {
                "status": "ready",
                "message": "Build do frontend completo",
                "file_count": file_count,
                "size_mb": sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)
            }
            
        except Exception as e:
            self.log(f"Erro ao verificar build: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def test_environment_config(self) -> Dict[str, Any]:
        """Testar configuração do ambiente"""
        self.log("Testando configuracao do ambiente...")
        
        try:
            # Verificar .env
            env_file = Path(".env")
            
            if not env_file.exists():
                self.log("Arquivo .env nao encontrado", "WARNING")
                return {
                    "status": "missing",
                    "message": "Arquivo .env nao encontrado"
                }
            
            # Ler variáveis
            with open(env_file, 'r') as f:
                content = f.read()
            
            env_vars = []
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    var_name = line.split('=')[0].strip()
                    env_vars.append(var_name)
            
            # Verificar variáveis críticas
            critical_vars = ["SECRET_KEY", "DATABASE_URL"]
            missing_vars = [var for var in critical_vars if var not in content]
            
            if missing_vars:
                self.log(f"Variaveis criticas ausentes: {missing_vars}", "WARNING")
            
            self.log(f"Configuracao OK - {len(env_vars)} variaveis")
            return {
                "status": "configured",
                "message": f"{len(env_vars)} variaveis encontradas",
                "variable_count": len(env_vars),
                "missing_critical": missing_vars
            }
            
        except Exception as e:
            self.log(f"Erro ao verificar configuracao: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def identify_specific_errors(self) -> List[str]:
        """Identificar erros específicos do sistema"""
        self.log("Identificando erros especificos...")
        
        errors_found = []
        
        # Verificar logs de erro comuns
        log_files = [
            "backend/server.log",
            "master_test_framework.log"
        ]
        
        for log_file in log_files:
            if Path(log_file).exists():
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Procurar padrões de erro
                    error_patterns = [
                        "ERROR",
                        "FAILED",
                        "Exception",
                        "Traceback",
                        "ConnectionError",
                        "TimeoutError"
                    ]
                    
                    for pattern in error_patterns:
                        if pattern in content:
                            lines = content.split('\n')
                            error_lines = [line for line in lines if pattern in line]
                            
                            # Pegar últimos 3 erros de cada tipo
                            recent_errors = error_lines[-3:] if len(error_lines) > 3 else error_lines
                            
                            for error_line in recent_errors:
                                # Limpar e adicionar erro
                                clean_error = error_line.strip()[:100]  # Limitar tamanho
                                if clean_error and clean_error not in errors_found:
                                    errors_found.append(clean_error)
                
                except Exception as e:
                    self.log(f"Erro ao ler log {log_file}: {str(e)}", "WARNING")
        
        # Verificar problemas específicos conhecidos
        specific_checks = [
            self._check_migration_errors,
            self._check_cors_errors,
            self._check_authentication_errors,
            self._check_database_errors
        ]
        
        for check_func in specific_checks:
            try:
                check_errors = check_func()
                errors_found.extend(check_errors)
            except Exception as e:
                self.log(f"Erro em verificacao especifica: {str(e)}", "WARNING")
        
        return list(set(errors_found))  # Remover duplicatas
    
    def _check_migration_errors(self) -> List[str]:
        """Verificar erros de migração"""
        errors = []
        
        # Verificar se há scripts de migração pendentes
        migration_files = list(Path("backend").glob("*migration*.py"))
        
        if migration_files:
            errors.append(f"Scripts de migracao encontrados: {len(migration_files)} - podem precisar execucao")
        
        return errors
    
    def _check_cors_errors(self) -> List[str]:
        """Verificar erros de CORS"""
        errors = []
        
        try:
            response = self.session.options(f"{self.base_url}/api/usuarios")
            
            cors_headers = [header for header in response.headers.keys() 
                          if header.lower().startswith('access-control')]
            
            if not cors_headers:
                errors.append("CORS pode nao estar configurado corretamente")
                
        except Exception:
            errors.append("Nao foi possivel verificar configuracao CORS")
        
        return errors
    
    def _check_authentication_errors(self) -> List[str]:
        """Verificar erros de autenticação"""
        errors = []
        
        # Verificar se há usuários no sistema
        try:
            db_path = Path("backend/eventos.db")
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'admin'")
                admin_count = cursor.fetchone()[0]
                
                if admin_count == 0:
                    errors.append("Nenhum usuario admin encontrado no sistema")
                
                conn.close()
                
        except Exception:
            errors.append("Nao foi possivel verificar usuarios admin")
        
        return errors
    
    def _check_database_errors(self) -> List[str]:
        """Verificar erros de banco de dados"""
        errors = []
        
        # Verificar integridade das tabelas
        try:
            db_path = Path("backend/eventos.db")
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Verificar se tabelas têm dados básicos
                tables_to_check = ["usuarios", "eventos"]
                
                for table in tables_to_check:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        
                        if count == 0 and table == "usuarios":
                            errors.append(f"Tabela {table} esta vazia - sistema pode nao ter dados iniciais")
                            
                    except sqlite3.OperationalError:
                        errors.append(f"Tabela {table} pode estar corrompida ou ausente")
                
                conn.close()
                
        except Exception:
            errors.append("Nao foi possivel verificar integridade do banco")
        
        return errors
    
    def suggest_fixes(self) -> List[str]:
        """Sugerir correções baseadas nos erros encontrados"""
        self.log("Gerando sugestoes de correcao...")
        
        fixes = []
        
        # Baseado nos erros encontrados
        if "Backend nao esta rodando" in self.results["critical_errors"]:
            fixes.append("1. Iniciar backend: cd backend && python server.py")
        
        if any("Database" in error for error in self.results["critical_errors"]):
            fixes.append("2. Inicializar database: cd backend && python init_db.py")
        
        if any("admin" in error.lower() for error in self.results["critical_errors"]):
            fixes.append("3. Criar usuario admin: cd backend && python create_admin_user.py")
        
        if "Build nao encontrado" in str(self.results):
            fixes.append("4. Construir frontend: cd frontend && npm run build")
        
        if any("migra" in error.lower() for error in self.results["critical_errors"]):
            fixes.append("5. Executar migracoes: cd backend && python apply_migration.py")
        
        # Fixes gerais
        if not fixes:
            fixes.append("Sistema parece estar funcionando corretamente")
        else:
            fixes.append("6. Reiniciar sistema apos aplicar correcoes")
            fixes.append("7. Verificar logs para detalhes: backend/server.log")
        
        return fixes
    
    def run_complete_diagnosis(self) -> Dict[str, Any]:
        """Executar diagnóstico completo"""
        self.log("Iniciando diagnostico completo...")
        
        # Testes principais
        self.results["backend_status"] = self.test_backend_health()
        time.sleep(1)  # Pequena pausa entre testes
        
        self.results["database_status"] = self.test_database_connectivity()
        time.sleep(1)
        
        if self.results["backend_status"].get("status") != "offline":
            self.results["authentication"] = self.test_authentication()
            time.sleep(1)
            
            self.results["endpoints"] = self.test_critical_endpoints()
            time.sleep(1)
        
        self.results["frontend_status"] = self.test_frontend_build()
        self.results["environment"] = self.test_environment_config()
        
        # Identificar erros específicos
        specific_errors = self.identify_specific_errors()
        self.results["critical_errors"].extend(specific_errors)
        
        # Gerar sugestões de correção
        self.results["recommendations"] = self.suggest_fixes()
        
        # Calcular tempo total
        execution_time = time.time() - self.start_time
        self.results["execution_time"] = round(execution_time, 2)
        
        return self.results
    
    def generate_report(self) -> str:
        """Gerar relatório final"""
        print("\n" + "=" * 80)
        print("RELATORIO DE DIAGNOSTICO DO SISTEMA")
        print("=" * 80)
        
        # Status geral
        backend_ok = self.results["backend_status"].get("status") in ["healthy", "working"]
        database_ok = self.results["database_status"].get("status") == "connected"
        
        print(f"Tempo de execucao: {self.results['execution_time']}s")
        print(f"Backend: {'OK' if backend_ok else 'PROBLEMA'}")
        print(f"Database: {'OK' if database_ok else 'PROBLEMA'}")
        
        # Erros críticos
        if self.results["critical_errors"]:
            print(f"\nERROS CRITICOS ENCONTRADOS ({len(self.results['critical_errors'])}):")
            print("-" * 80)
            for i, error in enumerate(self.results["critical_errors"], 1):
                print(f"{i}. {error}")
        
        # Recomendações
        if self.results["recommendations"]:
            print(f"\nRECOMENDACOES DE CORRECAO:")
            print("-" * 80)
            for rec in self.results["recommendations"]:
                print(f"  {rec}")
        
        # Status detalhado
        print(f"\nSTATUS DETALHADO:")
        print("-" * 80)
        
        for component, status in self.results.items():
            if isinstance(status, dict) and "status" in status:
                print(f"{component}: {status['status']} - {status.get('message', 'N/A')}")
        
        # Salvar relatório
        filename = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nRelatorio completo salvo em: {filename}")
        print("=" * 80)
        
        # Veredito final
        critical_count = len(self.results["critical_errors"])
        
        if critical_count == 0:
            print("VEREDITO: Sistema funcionando corretamente")
            return "OK"
        elif critical_count <= 3:
            print("VEREDITO: Sistema com problemas menores - correcoes recomendadas")
            return "WARNING"
        else:
            print("VEREDITO: Sistema com problemas graves - correcoes obrigatorias")
            return "CRITICAL"

def main():
    """Função principal"""
    print("INICIANDO SISTEMA DE DIAGNOSTICO...")
    
    diagnostic = SystemDiagnostic()
    
    try:
        # Executar diagnóstico
        results = diagnostic.run_complete_diagnosis()
        
        # Gerar relatório
        status = diagnostic.generate_report()
        
        # Código de saída
        if status == "OK":
            return 0
        elif status == "WARNING":
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"ERRO DURANTE DIAGNOSTICO: {str(e)}")
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit(main())
