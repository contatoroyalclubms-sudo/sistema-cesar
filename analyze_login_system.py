#!/usr/bin/env python3
"""
Análise Completa do Sistema de Login
Verifica compatibilidade entre Frontend, Backend e Banco de Dados
"""

import requests
import json
import sqlite3
import os
from datetime import datetime

class LoginSystemAnalyzer:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "frontend": {"status": "unknown", "errors": []},
            "backend": {"status": "unknown", "errors": []},
            "database": {"status": "unknown", "errors": []},
            "compatibility": {"status": "unknown", "issues": []}
        }
        
    def analyze_backend(self):
        """Analisa todos os backends rodando"""
        print("\n[ANALISANDO BACKENDS...]")
        print("-" * 50)
        
        backends = [
            {"port": 8000, "name": "Main Backend"},
            {"port": 8001, "name": "Alternative Backend"},
            {"port": 8003, "name": "Auth Server"},
        ]
        
        working_backends = []
        
        for backend in backends:
            try:
                # Teste de health
                response = requests.get(f"http://localhost:{backend['port']}/api/health", timeout=2)
                if response.status_code == 200:
                    print(f"[OK] {backend['name']} (porta {backend['port']}): ONLINE")
                    
                    # Teste de login
                    login_response = requests.post(
                        f"http://localhost:{backend['port']}/api/auth/login",
                        json={"cpf": "00000000000", "senha": "0000"},
                        timeout=2
                    )
                    
                    if login_response.status_code == 200:
                        data = login_response.json()
                        if "access_token" in data or "token" in data:
                            print(f"   [OK] Login endpoint funcionando")
                            working_backends.append(backend)
                        else:
                            print(f"   [ERRO] Login nao retorna token")
                            self.report["backend"]["errors"].append(f"Port {backend['port']}: No token in response")
                    else:
                        print(f"   [ERRO] Login falhou: {login_response.status_code}")
                        self.report["backend"]["errors"].append(f"Port {backend['port']}: Login status {login_response.status_code}")
                else:
                    print(f"[ERRO] {backend['name']} (porta {backend['port']}): OFFLINE")
                    
            except requests.exceptions.RequestException as e:
                print(f"[ERRO] {backend['name']} (porta {backend['port']}): NAO ACESSIVEL")
                self.report["backend"]["errors"].append(f"Port {backend['port']}: {str(e)}")
        
        if working_backends:
            self.report["backend"]["status"] = "ok"
            self.report["backend"]["working_ports"] = [b["port"] for b in working_backends]
            print(f"\n[INFO] Backends funcionando: {len(working_backends)}/{len(backends)}")
        else:
            self.report["backend"]["status"] = "error"
            print("\n[ERRO] Nenhum backend funcionando corretamente!")
        
        return working_backends
    
    def analyze_frontend(self):
        """Analisa o frontend"""
        print("\n[ANALISANDO FRONTEND...]")
        print("-" * 50)
        
        try:
            # Verifica se o frontend está rodando
            response = requests.get("http://localhost:5174", timeout=2)
            if response.status_code == 200:
                print("[OK] Frontend rodando na porta 5174")
                self.report["frontend"]["status"] = "ok"
                
                # Verifica configuração de API
                if "localhost:8003" in response.text or "localhost:8000" in response.text:
                    print("[OK] Frontend configurado com URL de API")
                else:
                    print("[AVISO] Configuracao de API nao detectada no HTML")
                    self.report["frontend"]["errors"].append("API URL not detected in HTML")
                    
            else:
                print(f"[ERRO] Frontend retornou status: {response.status_code}")
                self.report["frontend"]["status"] = "error"
                self.report["frontend"]["errors"].append(f"Status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Frontend nao acessivel: {e}")
            self.report["frontend"]["status"] = "error"
            self.report["frontend"]["errors"].append(str(e))
            
        # Verifica se porta 5173 também está sendo usada
        try:
            response = requests.get("http://localhost:5173", timeout=1)
            if response.status_code == 200:
                print("[AVISO] Frontend tambem rodando na porta 5173")
                self.report["frontend"]["additional_ports"] = [5173]
        except:
            pass
    
    def analyze_database(self):
        """Analisa o banco de dados"""
        print("\n[ANALISANDO BANCO DE DADOS...]")
        print("-" * 50)
        
        db_path = "C:\\Users\\User\\OneDrive\\Desktop\\sistema-v6-novo\\paineluniversal\\paineluniversal\\backend\\eventos.db"
        
        if not os.path.exists(db_path):
            print(f"[ERRO] Banco de dados nao encontrado: {db_path}")
            self.report["database"]["status"] = "error"
            self.report["database"]["errors"].append("Database file not found")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Lista todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            
            print(f"[INFO] Tabelas encontradas: {len(tables)}")
            
            # Verifica tabela usuarios
            if "usuarios" in table_names:
                print("[OK] Tabela 'usuarios' existe")
                
                # Verifica estrutura
                cursor.execute("PRAGMA table_info(usuarios)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                print(f"   Colunas: {', '.join(column_names)}")
                
                # Verifica campos essenciais
                essential_fields = ["id", "cpf"]
                missing = [f for f in essential_fields if f not in column_names]
                
                if not missing:
                    print("   [OK] Campos essenciais presentes")
                    
                    # Conta usuários
                    cursor.execute("SELECT COUNT(*) FROM usuarios")
                    count = cursor.fetchone()[0]
                    print(f"   [INFO] Total de usuarios: {count}")
                    
                    # Verifica usuário admin
                    cursor.execute("SELECT cpf, nome FROM usuarios WHERE cpf = '00000000000'")
                    admin = cursor.fetchone()
                    if admin:
                        print(f"   [OK] Usuario admin encontrado: {admin[1] if len(admin) > 1 else 'CPF: ' + admin[0]}")
                    else:
                        print("   [ERRO] Usuario admin (00000000000) nao encontrado")
                        self.report["database"]["errors"].append("Admin user not found")
                    
                    self.report["database"]["status"] = "ok"
                    self.report["database"]["user_count"] = count
                else:
                    print(f"   [ERRO] Campos faltando: {missing}")
                    self.report["database"]["status"] = "error"
                    self.report["database"]["errors"].append(f"Missing fields: {missing}")
            else:
                print("[ERRO] Tabela 'usuarios' nao existe")
                self.report["database"]["status"] = "error"
                self.report["database"]["errors"].append("Users table missing")
                
            conn.close()
            
        except Exception as e:
            print(f"[ERRO] Erro ao acessar banco: {e}")
            self.report["database"]["status"] = "error"
            self.report["database"]["errors"].append(str(e))
    
    def check_compatibility(self):
        """Verifica compatibilidade entre componentes"""
        print("\n[VERIFICANDO COMPATIBILIDADE...]")
        print("-" * 50)
        
        issues = []
        
        # Verifica se frontend e backend estão ok
        if self.report["frontend"]["status"] == "ok" and self.report["backend"]["status"] == "ok":
            print("[OK] Frontend e Backend compativeis")
            
            # Testa comunicação real
            try:
                # Simula request do frontend para backend
                backend_port = self.report["backend"]["working_ports"][0] if "working_ports" in self.report["backend"] else 8003
                
                response = requests.post(
                    f"http://localhost:{backend_port}/api/auth/login",
                    json={"cpf": "00000000000", "senha": "0000"},
                    headers={"Origin": "http://localhost:5174"}
                )
                
                if response.status_code == 200:
                    print("[OK] Comunicacao Frontend-Backend funcionando")
                else:
                    print(f"[ERRO] Comunicacao falhou: {response.status_code}")
                    issues.append(f"Communication failed: {response.status_code}")
                    
            except Exception as e:
                print(f"[ERRO] Erro na comunicacao: {e}")
                issues.append(f"Communication error: {str(e)}")
        else:
            if self.report["frontend"]["status"] != "ok":
                issues.append("Frontend not working")
            if self.report["backend"]["status"] != "ok":
                issues.append("Backend not working")
        
        # Verifica compatibilidade backend-database
        if self.report["backend"]["status"] == "ok" and self.report["database"]["status"] == "ok":
            print("[OK] Backend e Database compativeis")
        else:
            if self.report["database"]["status"] != "ok":
                issues.append("Database issues")
        
        if issues:
            self.report["compatibility"]["status"] = "error"
            self.report["compatibility"]["issues"] = issues
            print(f"\n[ERRO] Problemas de compatibilidade encontrados: {len(issues)}")
        else:
            self.report["compatibility"]["status"] = "ok"
            print("\n[OK] Sistema totalmente compativel!")
    
    def generate_fixes(self):
        """Gera correções sugeridas"""
        print("\n[CORRECOES SUGERIDAS...]")
        print("-" * 50)
        
        fixes = []
        
        # Backend fixes
        if self.report["backend"]["status"] != "ok":
            fixes.append("BACKEND:")
            fixes.append("  1. Verificar se auth_server.py está rodando na porta 8003")
            fixes.append("  2. Executar: cd backend && python auth_server.py")
            fixes.append("  3. Verificar se as credenciais estão corretas: CPF 00000000000, senha 0000")
        
        # Frontend fixes
        if self.report["frontend"]["status"] != "ok":
            fixes.append("FRONTEND:")
            fixes.append("  1. Verificar se o frontend está rodando: cd frontend && npm run dev")
            fixes.append("  2. Verificar src/lib/api.ts está apontando para porta correta (8003)")
            fixes.append("  3. Limpar cache: rm -rf node_modules/.vite")
        
        # Database fixes
        if self.report["database"]["status"] != "ok":
            if "user_count" in self.report["database"] and self.report["database"]["user_count"] == 0:
                fixes.append("DATABASE:")
                fixes.append("  1. Criar usuário admin no banco")
                fixes.append("  2. Executar: cd backend && python create_admin_user.py")
        
        # Compatibility fixes
        if self.report["compatibility"]["status"] != "ok":
            fixes.append("COMPATIBILIDADE:")
            fixes.append("  1. Verificar CORS no backend")
            fixes.append("  2. Verificar que frontend usa http://localhost:8003 como API_URL")
            fixes.append("  3. Verificar que os endpoints /api/auth/login existem")
        
        if fixes:
            for fix in fixes:
                print(fix)
        else:
            print("[OK] Nenhuma correcao necessaria!")
        
        return fixes
    
    def save_report(self):
        """Salva relatório em arquivo"""
        with open("login_compatibility_report.json", "w") as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n[INFO] Relatorio salvo em: login_compatibility_report.json")
    
    def run_full_analysis(self):
        """Executa análise completa"""
        print("=" * 60)
        print("ANALISE COMPLETA DO SISTEMA DE LOGIN")
        print("=" * 60)
        
        self.analyze_backend()
        self.analyze_frontend()
        self.analyze_database()
        self.check_compatibility()
        
        fixes = self.generate_fixes()
        self.report["suggested_fixes"] = fixes
        
        # Resumo final
        print("\n" + "=" * 60)
        print("RESUMO FINAL")
        print("=" * 60)
        
        components = ["frontend", "backend", "database", "compatibility"]
        for component in components:
            status = self.report[component]["status"]
            emoji = "[OK]" if status == "ok" else "[ERRO]"
            print(f"{emoji} {component.upper()}: {status.upper()}")
        
        # Taxa de sucesso
        ok_count = sum(1 for c in components if self.report[c]["status"] == "ok")
        success_rate = (ok_count / len(components)) * 100
        
        print(f"\n[INFO] Taxa de Compatibilidade: {success_rate:.0f}%")
        
        if success_rate == 100:
            print("\n[SUCESSO] SISTEMA TOTALMENTE FUNCIONAL!")
        elif success_rate >= 75:
            print("\n[AVISO] Sistema parcialmente funcional - correcoes menores necessarias")
        else:
            print("\n[ERRO] Sistema com problemas criticos - correcoes urgentes necessarias")
        
        self.save_report()
        
        return self.report

if __name__ == "__main__":
    analyzer = LoginSystemAnalyzer()
    report = analyzer.run_full_analysis()