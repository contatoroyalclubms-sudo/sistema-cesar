#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE PERFORMANCE OTIMIZADA
===================================

Verifica e valida todas as otimizações implementadas.
Relatório completo de performance e funcionalidade.

Autor: Sistema de Otimização Automatizada
Data: 2024
"""

import os
import sys
import time
import json
import requests
import psutil
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class PerformanceValidator:
    """Validador completo de performance e otimizações"""
    
    def __init__(self):
        self.start_time = time.time()
        self.logger = self.setup_logging()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "performance": {},
            "optimizations": {},
            "recommendations": []
        }
        
    def setup_logging(self) -> logging.Logger:
        """Configura sistema de logs"""
        logger = logging.getLogger("performance_validator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def test_system_resources(self) -> Dict[str, Any]:
        """Testa recursos do sistema"""
        self.logger.info("🔍 Testando recursos do sistema...")
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            resources = {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": cpu_count,
                    "status": "ok" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "usage_percent": memory_percent,
                    "available_gb": round(memory_available_gb, 2),
                    "status": "ok" if memory_percent < 80 else "high"
                },
                "disk": {
                    "usage_percent": round(disk_percent, 2),
                    "free_gb": round(disk_free_gb, 2),
                    "status": "ok" if disk_percent < 90 else "high"
                }
            }
            
            self.logger.info(f"✅ Recursos do sistema verificados")
            return resources
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar recursos: {e}")
            return {"error": str(e)}
    
    def test_database_connection(self) -> Dict[str, Any]:
        """Testa conexão com banco de dados"""
        self.logger.info("🔍 Testando conexão com banco de dados...")
        
        try:
            # Testar SQLite
            sqlite_path = Path("eventos.db")
            sqlite_result = {}
            
            if sqlite_path.exists():
                start_time = time.time()
                
                conn = sqlite3.connect(str(sqlite_path))
                cursor = conn.cursor()
                
                # Teste básico
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Teste de performance
                cursor.execute("SELECT COUNT(*) FROM usuarios;")
                user_count = cursor.fetchone()[0]
                
                conn.close()
                
                sqlite_result = {
                    "status": "connected",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "tables_count": len(tables),
                    "users_count": user_count,
                    "file_size_mb": round(sqlite_path.stat().st_size / (1024*1024), 2)
                }
                
                self.logger.info(f"✅ SQLite conectado - {user_count} usuários")
            else:
                sqlite_result = {"status": "file_not_found"}
            
            # Testar PostgreSQL (se configurado)
            postgres_result = {}
            try:
                import psycopg2
                
                # Ler configuração do .env
                env_path = Path(".env")
                postgres_config = {}
                
                if env_path.exists():
                    with open(env_path, 'r') as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if key.startswith('POSTGRES_'):
                                    postgres_config[key] = value.strip('"')
                
                if postgres_config:
                    start_time = time.time()
                    
                    conn = psycopg2.connect(
                        host=postgres_config.get('POSTGRES_HOST', 'localhost'),
                        port=postgres_config.get('POSTGRES_PORT', '5432'),
                        database=postgres_config.get('POSTGRES_DB', 'postgres'),
                        user=postgres_config.get('POSTGRES_USER', 'postgres'),
                        password=postgres_config.get('POSTGRES_PASSWORD', '')
                    )
                    
                    cursor = conn.cursor()
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
                    table_count = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    postgres_result = {
                        "status": "connected",
                        "response_time_ms": round((time.time() - start_time) * 1000, 2),
                        "version": version,
                        "tables_count": table_count
                    }
                    
                    self.logger.info(f"✅ PostgreSQL conectado - {table_count} tabelas")
                else:
                    postgres_result = {"status": "not_configured"}
                    
            except ImportError:
                postgres_result = {"status": "psycopg2_not_installed"}
            except Exception as e:
                postgres_result = {"status": "connection_failed", "error": str(e)}
            
            return {
                "sqlite": sqlite_result,
                "postgresql": postgres_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar banco: {e}")
            return {"error": str(e)}
    
    def test_server_endpoints(self) -> Dict[str, Any]:
        """Testa endpoints do servidor"""
        self.logger.info("🔍 Testando endpoints do servidor...")
        
        base_url = "http://localhost:8000"
        endpoints = [
            {"path": "/", "name": "root"},
            {"path": "/health", "name": "health"},
            {"path": "/api/usuarios", "name": "usuarios_api"},
            {"path": "/api/produtos", "name": "produtos_api"},
            {"path": "/login", "name": "login_page"},
            {"path": "/dashboard", "name": "dashboard_page"}
        ]
        
        results = {}
        server_running = False
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                
                response = requests.get(
                    f"{base_url}{endpoint['path']}", 
                    timeout=10,
                    allow_redirects=False
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                results[endpoint['name']] = {
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "content_length": len(response.content),
                    "status": "ok" if response.status_code < 400 else "error"
                }
                
                server_running = True
                self.logger.info(f"✅ {endpoint['name']}: {response.status_code} ({response_time}ms)")
                
            except requests.exceptions.ConnectionError:
                results[endpoint['name']] = {
                    "status": "connection_refused",
                    "error": "Servidor não está rodando"
                }
                
            except Exception as e:
                results[endpoint['name']] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "server_running": server_running,
            "endpoints": results
        }
    
    def test_cors_configuration(self) -> Dict[str, Any]:
        """Testa configuração CORS"""
        self.logger.info("🔍 Testando configuração CORS...")
        
        try:
            # Verificar arquivo de configuração CORS
            cors_config_files = [
                "cors_config_development.json",
                "cors_config_production.json",
                "cors_config.json"
            ]
            
            cors_configs = {}
            
            for config_file in cors_config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        cors_configs[config_file] = json.load(f)
            
            # Testar CORS via requisição
            cors_test = {}
            try:
                headers = {
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
                
                response = requests.options(
                    "http://localhost:8000/api/usuarios",
                    headers=headers,
                    timeout=5
                )
                
                cors_headers = {
                    key: value for key, value in response.headers.items()
                    if key.lower().startswith('access-control')
                }
                
                cors_test = {
                    "status_code": response.status_code,
                    "cors_headers": cors_headers,
                    "allows_origin": 'access-control-allow-origin' in response.headers
                }
                
                self.logger.info("✅ CORS testado via requisição")
                
            except Exception as e:
                cors_test = {"error": str(e)}
            
            return {
                "config_files": cors_configs,
                "runtime_test": cors_test
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar CORS: {e}")
            return {"error": str(e)}
    
    def analyze_optimization_files(self) -> Dict[str, Any]:
        """Analisa arquivos de otimização criados"""
        self.logger.info("🔍 Analisando arquivos de otimização...")
        
        optimization_files = [
            "healthcheck_monitor.py",
            "database_config_optimizer.py", 
            "cors_optimizer.py",
            "authenticated_api_tester.py",
            "auto_server_manager.py"
        ]
        
        analysis = {}
        
        for file_name in optimization_files:
            file_path = Path(file_name)
            
            if file_path.exists():
                stat = file_path.stat()
                
                # Contar linhas de código
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    
                    # Análise básica do código
                    class_count = content.count('class ')
                    function_count = content.count('def ')
                    import_count = content.count('import ')
                    
                analysis[file_name] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "lines_of_code": lines,
                    "classes": class_count,
                    "functions": function_count,
                    "imports": import_count,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                self.logger.info(f"✅ {file_name}: {lines} linhas, {class_count} classes")
            else:
                analysis[file_name] = {"exists": False}
        
        return analysis
    
    def calculate_performance_score(self) -> Dict[str, Any]:
        """Calcula score de performance geral"""
        self.logger.info("🔍 Calculando score de performance...")
        
        try:
            score = 100
            factors = []
            
            # Recursos do sistema
            if "system_resources" in self.results["tests"]:
                resources = self.results["tests"]["system_resources"]
                
                if isinstance(resources, dict) and "cpu" in resources:
                    cpu_usage = resources["cpu"].get("usage_percent", 0)
                    memory_usage = resources["memory"].get("usage_percent", 0)
                    disk_usage = resources["disk"].get("usage_percent", 0)
                    
                    if cpu_usage > 80:
                        score -= 20
                        factors.append("CPU alto (>80%)")
                    elif cpu_usage > 60:
                        score -= 10
                        factors.append("CPU moderado (>60%)")
                    
                    if memory_usage > 80:
                        score -= 20
                        factors.append("Memória alta (>80%)")
                    elif memory_usage > 60:
                        score -= 10
                        factors.append("Memória moderada (>60%)")
                    
                    if disk_usage > 90:
                        score -= 15
                        factors.append("Disco quase cheio (>90%)")
                    elif disk_usage > 80:
                        score -= 5
                        factors.append("Disco alto (>80%)")
            
            # Servidor funcionando
            if "server_endpoints" in self.results["tests"]:
                endpoints = self.results["tests"]["server_endpoints"]
                
                if endpoints.get("server_running"):
                    score += 10
                    factors.append("Servidor rodando (+10)")
                else:
                    score -= 30
                    factors.append("Servidor offline (-30)")
                
                # Verificar endpoints funcionando
                endpoint_results = endpoints.get("endpoints", {})
                working_endpoints = sum(1 for ep in endpoint_results.values() 
                                      if isinstance(ep, dict) and ep.get("status") == "ok")
                
                if working_endpoints >= 4:
                    score += 10
                    factors.append(f"Endpoints funcionando: {working_endpoints} (+10)")
                elif working_endpoints >= 2:
                    score += 5
                    factors.append(f"Endpoints funcionando: {working_endpoints} (+5)")
                else:
                    score -= 10
                    factors.append(f"Poucos endpoints funcionando: {working_endpoints} (-10)")
            
            # Banco de dados
            if "database" in self.results["tests"]:
                db = self.results["tests"]["database"]
                
                sqlite_working = (isinstance(db.get("sqlite"), dict) and 
                                db["sqlite"].get("status") == "connected")
                postgres_working = (isinstance(db.get("postgresql"), dict) and 
                                  db["postgresql"].get("status") == "connected")
                
                if postgres_working:
                    score += 15
                    factors.append("PostgreSQL conectado (+15)")
                elif sqlite_working:
                    score += 10
                    factors.append("SQLite conectado (+10)")
                else:
                    score -= 20
                    factors.append("Banco não conectado (-20)")
            
            # Otimizações implementadas
            if "optimization_files" in self.results["tests"]:
                files = self.results["tests"]["optimization_files"]
                implemented = sum(1 for f in files.values() 
                                if isinstance(f, dict) and f.get("exists"))
                
                if implemented >= 4:
                    score += 15
                    factors.append(f"Otimizações implementadas: {implemented} (+15)")
                elif implemented >= 2:
                    score += 10
                    factors.append(f"Otimizações implementadas: {implemented} (+10)")
                else:
                    score += 5
                    factors.append(f"Otimizações implementadas: {implemented} (+5)")
            
            # Garantir que score esteja entre 0 e 100
            score = max(0, min(100, score))
            
            # Classificação
            if score >= 90:
                classification = "Excelente"
            elif score >= 80:
                classification = "Bom"
            elif score >= 70:
                classification = "Regular"
            elif score >= 60:
                classification = "Ruim"
            else:
                classification = "Crítico"
            
            return {
                "score": score,
                "classification": classification,
                "factors": factors
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular score: {e}")
            return {"score": 0, "classification": "Erro", "factors": [str(e)]}
    
    def generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos testes"""
        recommendations = []
        
        try:
            # Verificar recursos do sistema
            if "system_resources" in self.results["tests"]:
                resources = self.results["tests"]["system_resources"]
                
                if isinstance(resources, dict):
                    if resources.get("cpu", {}).get("usage_percent", 0) > 80:
                        recommendations.append("⚠️ CPU alta - considere otimizar processos ou aumentar recursos")
                    
                    if resources.get("memory", {}).get("usage_percent", 0) > 80:
                        recommendations.append("⚠️ Memória alta - considere adicionar mais RAM ou otimizar código")
                    
                    if resources.get("disk", {}).get("usage_percent", 0) > 90:
                        recommendations.append("⚠️ Disco quase cheio - limpe arquivos desnecessários")
            
            # Verificar servidor
            if "server_endpoints" in self.results["tests"]:
                endpoints = self.results["tests"]["server_endpoints"]
                
                if not endpoints.get("server_running"):
                    recommendations.append("🚨 Servidor não está rodando - execute auto_server_manager.py")
                
                endpoint_results = endpoints.get("endpoints", {})
                for name, result in endpoint_results.items():
                    if isinstance(result, dict) and result.get("status") == "error":
                        recommendations.append(f"⚠️ Endpoint {name} com erro - verificar logs")
            
            # Verificar banco
            if "database" in self.results["tests"]:
                db = self.results["tests"]["database"]
                
                postgres_status = db.get("postgresql", {}).get("status")
                sqlite_status = db.get("sqlite", {}).get("status")
                
                if postgres_status == "not_configured":
                    recommendations.append("💡 PostgreSQL não configurado - execute database_config_optimizer.py")
                elif postgres_status == "connection_failed":
                    recommendations.append("⚠️ PostgreSQL com erro - verificar configuração e conectividade")
                
                if sqlite_status == "file_not_found":
                    recommendations.append("⚠️ Arquivo SQLite não encontrado - verificar inicialização do banco")
            
            # Verificar otimizações
            if "optimization_files" in self.results["tests"]:
                files = self.results["tests"]["optimization_files"]
                
                missing_files = [name for name, info in files.items() 
                               if isinstance(info, dict) and not info.get("exists")]
                
                if missing_files:
                    recommendations.append(f"📝 Arquivos de otimização ausentes: {', '.join(missing_files)}")
            
            # Recomendações de performance
            performance_score = self.results["performance"].get("score", 0)
            
            if performance_score < 70:
                recommendations.append("🔧 Score baixo - implemente mais otimizações prioritárias")
            elif performance_score < 90:
                recommendations.append("⚡ Score bom - considere otimizações avançadas")
            else:
                recommendations.append("🎉 Excelente performance - sistema otimizado!")
            
            # Recomendações gerais
            recommendations.extend([
                "📊 Execute monitoramento contínuo com healthcheck_monitor.py",
                "🔐 Configure autenticação robusta se ainda não feito",
                "📈 Monitore logs regularmente para identificar problemas",
                "🔄 Mantenha backups automáticos configurados"
            ])
            
        except Exception as e:
            recommendations.append(f"❌ Erro ao gerar recomendações: {e}")
        
        return recommendations
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de validação"""
        self.logger.info("🚀 INICIANDO VALIDAÇÃO COMPLETA DE PERFORMANCE")
        self.logger.info("="*60)
        
        # Executar testes
        self.results["tests"]["system_resources"] = self.test_system_resources()
        self.results["tests"]["database"] = self.test_database_connection()
        self.results["tests"]["server_endpoints"] = self.test_server_endpoints()
        self.results["tests"]["cors_configuration"] = self.test_cors_configuration()
        self.results["tests"]["optimization_files"] = self.analyze_optimization_files()
        
        # Calcular performance
        self.results["performance"] = self.calculate_performance_score()
        
        # Gerar recomendações
        self.results["recommendations"] = self.generate_recommendations()
        
        # Tempo total
        total_time = round(time.time() - self.start_time, 2)
        self.results["execution_time_seconds"] = total_time
        
        self.logger.info(f"✅ Validação completa em {total_time}s")
        
        return self.results
    
    def save_report(self, filename: str = "performance_validation_report.json"):
        """Salva relatório em arquivo"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📁 Relatório salvo: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print("📊 RESUMO DA VALIDAÇÃO DE PERFORMANCE")
        print("="*60)
        
        # Performance Score
        performance = self.results.get("performance", {})
        score = performance.get("score", 0)
        classification = performance.get("classification", "Desconhecido")
        
        print(f"\n🎯 SCORE GERAL: {score}/100 ({classification})")
        
        # Status dos testes
        print(f"\n📋 STATUS DOS TESTES:")
        
        tests = self.results.get("tests", {})
        
        # Recursos do sistema
        resources = tests.get("system_resources", {})
        if isinstance(resources, dict) and "cpu" in resources:
            cpu = resources["cpu"]["usage_percent"]
            memory = resources["memory"]["usage_percent"]
            disk = resources["disk"]["usage_percent"]
            print(f"   💻 Sistema: CPU {cpu}%, RAM {memory}%, Disco {disk}%")
        
        # Servidor
        server = tests.get("server_endpoints", {})
        server_status = "🟢 Online" if server.get("server_running") else "🔴 Offline"
        print(f"   🌐 Servidor: {server_status}")
        
        # Banco de dados
        db = tests.get("database", {})
        if isinstance(db, dict):
            sqlite_ok = db.get("sqlite", {}).get("status") == "connected"
            postgres_ok = db.get("postgresql", {}).get("status") == "connected"
            
            if postgres_ok:
                print(f"   🗄️ Banco: PostgreSQL conectado")
            elif sqlite_ok:
                print(f"   🗄️ Banco: SQLite conectado")
            else:
                print(f"   🗄️ Banco: Não conectado")
        
        # Otimizações
        opt_files = tests.get("optimization_files", {})
        if isinstance(opt_files, dict):
            implemented = sum(1 for f in opt_files.values() 
                            if isinstance(f, dict) and f.get("exists"))
            total = len(opt_files)
            print(f"   ⚡ Otimizações: {implemented}/{total} implementadas")
        
        # Principais recomendações
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            print(f"\n🔧 PRINCIPAIS RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        # Tempo de execução
        exec_time = self.results.get("execution_time_seconds", 0)
        print(f"\n⏱️ Tempo de execução: {exec_time}s")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    print("🔍 VERIFICADOR DE PERFORMANCE OTIMIZADA")
    print("="*60)
    print("Validando todas as otimizações implementadas...")
    print()
    
    validator = PerformanceValidator()
    
    try:
        # Executar todos os testes
        results = validator.run_all_tests()
        
        # Salvar relatório
        validator.save_report()
        
        # Mostrar resumo
        validator.print_summary()
        
        return 0 if results["performance"]["score"] >= 70 else 1
        
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
