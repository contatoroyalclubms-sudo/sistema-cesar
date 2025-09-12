#!/usr/bin/env python
"""
SISTEMA COMPLETO MEEP - AUDITORIA + INTEGRAÇÃO + DASHBOARD
Solução All-in-One para o Painel Universal
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

class MEEPSystemComplete:
    """Sistema completo MEEP com todas as funcionalidades"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.frontend_dir = self.base_dir / "paineluniversal" / "frontend"
        self.backend_dir = self.base_dir / "paineluniversal" / "backend"
        
        # Criar estrutura de diretórios
        self.setup_directories()
        
        # Status dos serviços
        self.services_status = {
            "frontend": False,
            "backend": False,
            "meep_capture": False,
            "auditoria": False
        }
    
    def setup_directories(self):
        """Criar estrutura de diretórios necessária"""
        dirs = [
            "data/captures",
            "data/reports", 
            "data/postman",
            "data/screenshots",
            "data/diffs",
            "data/meep_analytics"
        ]
        
        for dir_path in dirs:
            Path(self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        print("[OK] Estrutura de diretórios criada")
    
    def check_services(self):
        """Verificar status de todos os serviços"""
        print("\n" + "="*60)
        print(" VERIFICANDO SERVIÇOS")
        print("="*60)
        
        # Frontend
        try:
            import requests
            resp = requests.get("http://localhost:5174", timeout=2)
            if resp.status_code == 200:
                self.services_status["frontend"] = True
                print("[OK] Frontend rodando na porta 5174")
        except:
            try:
                resp = requests.get("http://localhost:5173", timeout=2)
                if resp.status_code == 200:
                    self.services_status["frontend"] = True
                    print("[OK] Frontend rodando na porta 5173")
            except:
                print("[ERRO] Frontend não está rodando")
        
        # Backend Auth
        try:
            resp = requests.get("http://localhost:8003/api/health", timeout=2)
            if resp.status_code == 200:
                self.services_status["backend"] = True
                print("[OK] Backend Auth rodando na porta 8003")
        except:
            print("[ERRO] Backend não está rodando")
        
        # MEEP Server
        try:
            resp = requests.get("http://localhost:8004/api/meep/status", timeout=2)
            if resp.status_code == 200:
                self.services_status["meep_capture"] = True
                print("[OK] MEEP Server rodando na porta 8004")
        except:
            print("[AVISO] MEEP Server não está rodando")
        
        return self.services_status
    
    def start_missing_services(self):
        """Iniciar serviços que não estão rodando"""
        print("\n" + "="*60)
        print(" INICIANDO SERVIÇOS FALTANTES")
        print("="*60)
        
        if not self.services_status["frontend"]:
            print("\n[INFO] Iniciando Frontend...")
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.frontend_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            time.sleep(5)
        
        if not self.services_status["backend"]:
            print("\n[INFO] Iniciando Backend Auth...")
            subprocess.Popen(
                ["python", "auth_server.py"],
                cwd=self.backend_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            time.sleep(3)
    
    def run_meep_capture(self):
        """Executar captura MEEP"""
        print("\n" + "="*60)
        print(" EXECUTANDO CAPTURA MEEP")
        print("="*60)
        
        # Verificar se os scripts existem
        scripts = [
            "meep-ultimate-capture.js",
            "meep-reverse-engineering.js",
            "missao-completa-mcp.js"
        ]
        
        for script in scripts:
            script_path = self.base_dir / script
            if script_path.exists():
                print(f"\n[INFO] Executando {script}...")
                try:
                    result = subprocess.run(
                        ["node", str(script_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        print(f"[OK] {script} executado com sucesso")
                    else:
                        print(f"[AVISO] {script} retornou erro")
                except subprocess.TimeoutExpired:
                    print(f"[AVISO] {script} timeout")
                except Exception as e:
                    print(f"[ERRO] Falha ao executar {script}: {e}")
    
    def generate_complete_report(self):
        """Gerar relatório completo do sistema"""
        print("\n" + "="*60)
        print(" GERANDO RELATÓRIO COMPLETO")
        print("="*60)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system": "MEEP Sistema Completo",
            "services": self.services_status,
            "captures": [],
            "analytics": {},
            "urls": {
                "frontend": "http://localhost:5174",
                "login": "http://localhost:5174/login",
                "meep_dashboard": "http://localhost:5174/meep/dashboard",
                "meep_analytics": "http://localhost:5174/meep/analytics",
                "api_docs": "http://localhost:8003/docs",
                "meep_api": "http://localhost:8004/docs"
            },
            "credentials": {
                "cpf": "00000000000",
                "senha": "0000"
            }
        }
        
        # Salvar relatório
        report_file = self.data_dir / "reports" / f"complete_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Relatório salvo em: {report_file}")
        
        # Gerar HTML
        html_content = self.generate_html_report(report)
        html_file = self.data_dir / "reports" / f"complete_report_{int(time.time())}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"[OK] Relatório HTML salvo em: {html_file}")
        
        return report
    
    def generate_html_report(self, report):
        """Gerar relatório HTML bonito"""
        html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEEP Sistema - Relatório Completo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #28a745;
        }
        .status-card.error {
            border-left-color: #dc3545;
        }
        .url-list {
            background: #f1f3f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .url-list a {
            color: #667eea;
            text-decoration: none;
            display: block;
            padding: 5px 0;
        }
        .url-list a:hover {
            text-decoration: underline;
        }
        .credentials {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MEEP Sistema - Relatório Completo</h1>
        <p><strong>Data:</strong> """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """</p>
        
        <h2>Status dos Serviços</h2>
        <div class="status-grid">"""
        
        for service, status in report["services"].items():
            status_class = "" if status else "error"
            status_text = "ONLINE" if status else "OFFLINE"
            status_color = "success" if status else "error"
            html += f"""
            <div class="status-card {status_class}">
                <h3>{service.replace('_', ' ').title()}</h3>
                <p class="{status_color}"><strong>{status_text}</strong></p>
            </div>"""
        
        html += """
        </div>
        
        <h2>URLs do Sistema</h2>
        <div class="url-list">"""
        
        for name, url in report["urls"].items():
            html += f'<a href="{url}" target="_blank">{name.replace("_", " ").title()}: {url}</a>'
        
        html += """
        </div>
        
        <h2>Credenciais de Teste</h2>
        <div class="credentials">
            <p><strong>CPF:</strong> """ + report["credentials"]["cpf"] + """</p>
            <p><strong>Senha:</strong> """ + report["credentials"]["senha"] + """</p>
        </div>
        
        <h2>Como Usar</h2>
        <ol>
            <li>Acesse o <a href="http://localhost:5174/login">Login do Sistema</a></li>
            <li>Use as credenciais acima</li>
            <li>Navegue para o <a href="http://localhost:5174/meep/dashboard">Dashboard MEEP</a></li>
            <li>Explore as funcionalidades de auditoria e analytics</li>
        </ol>
    </div>
</body>
</html>"""
        
        return html
    
    def execute_complete_flow(self):
        """Executar fluxo completo do sistema"""
        print("\n" + "="*60)
        print(" SISTEMA COMPLETO MEEP - EXECUÇÃO TOTAL")
        print("="*60)
        
        # 1. Verificar serviços
        self.check_services()
        
        # 2. Iniciar serviços faltantes
        self.start_missing_services()
        time.sleep(5)
        
        # 3. Verificar novamente
        self.check_services()
        
        # 4. Executar captura MEEP
        self.run_meep_capture()
        
        # 5. Gerar relatórios
        report = self.generate_complete_report()
        
        # 6. Mostrar resumo final
        print("\n" + "="*60)
        print(" RESUMO FINAL")
        print("="*60)
        
        all_ok = all(self.services_status.values())
        
        if all_ok:
            print("\n[OK] SISTEMA 100% FUNCIONAL!")
            print("\nACESSE AGORA:")
            print(f"  Login: {report['urls']['login']}")
            print(f"  Dashboard MEEP: {report['urls']['meep_dashboard']}")
            print(f"\nCREDENCIAIS:")
            print(f"  CPF: {report['credentials']['cpf']}")
            print(f"  Senha: {report['credentials']['senha']}")
        else:
            print("\n[AVISO] Alguns serviços não estão funcionando.")
            print("Verifique os logs acima para mais detalhes.")
        
        print("\n[INFO] Relatórios salvos em ./data/reports/")
        print("[INFO] Screenshots salvos em ./data/screenshots/")
        
        return all_ok

def main():
    """Função principal"""
    system = MEEPSystemComplete()
    success = system.execute_complete_flow()
    
    if success:
        print("\n" + "🎉 "*10)
        print("SUCESSO TOTAL! Sistema MEEP funcionando perfeitamente!")
        print("🎉 "*10)
    else:
        print("\nSistema iniciado com avisos. Verifique os logs.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())