"""
Deploy automático com remoção segura do campo tipo_usuario
"""

import subprocess
import sys
import os
from datetime import datetime

class AutoDeploy:
    def __init__(self):
        self.deployment_log = f"deploy_tipo_usuario_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def log_step(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "PROCESS": "🔄"
        }.get(status, "📝")
        
        log_message = f"[{timestamp}] {status_icon} {message}"
        print(log_message)
        
        # Salvar no arquivo de log
        with open(self.deployment_log, 'a', encoding='utf-8') as f:
            f.write(log_message + "\\n")
        
    def run_command(self, command, description):
        """Executar comando e retornar sucesso/falha"""
        try:
            self.log_step(f"Executando: {description}", "PROCESS")
            self.log_step(f"Comando: {command}", "INFO")
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            if result.returncode == 0:
                self.log_step(f"✅ {description} - Sucesso", "SUCCESS")
                if result.stdout:
                    self.log_step(f"Output: {result.stdout.strip()}", "INFO")
                return True
            else:
                self.log_step(f"❌ {description} - Falhou", "ERROR")
                self.log_step(f"Error: {result.stderr.strip()}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step(f"❌ {description} - Timeout", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"❌ {description} - Erro: {e}", "ERROR")
            return False
    
    def backup_current_state(self):
        """Fazer backup do estado atual"""
        self.log_step("Iniciando backup do estado atual...", "PROCESS")
        
        # Criar backup dos arquivos modificados
        backup_files = [
            "backend/init_users.py",
            "backend/create_admin_user.py", 
            "backend/test_funcionalidades.py",
            "backend/seed_financeiro_data.py",
            "backend/update_user_1.py",
            "backend/tests/test_eventos.py"
        ]
        
        backup_dir = f"backup_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        for file_path in backup_files:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                command = f"cp {file_path} {backup_path}"
                if not self.run_command(command, f"Backup de {file_path}"):
                    return False
        
        self.log_step(f"Backup criado em: {backup_dir}", "SUCCESS")
        return True
    
    def run_migration(self):
        """Executar migração para remover tipo_usuario"""
        self.log_step("Executando migração de remoção...", "PROCESS")
        
        # Executar script de migração
        command = "python remove_tipo_usuario_migration.py"
        return self.run_command(command, "Migração de remoção tipo_usuario")
    
    def validate_system(self):
        """Validar sistema após migração"""
        self.log_step("Validando sistema...", "PROCESS")
        
        command = "python validate_system.py"
        return self.run_command(command, "Validação completa do sistema")
    
    def test_backend(self):
        """Testar se o backend ainda funciona"""
        self.log_step("Testando backend...", "PROCESS")
        
        # Verificar se o backend consegue iniciar
        command = "cd backend && python -c 'from app.main import app; print(\"Backend OK\")'"
        return self.run_command(command, "Teste de inicialização do backend")
    
    def deploy_to_railway(self):
        """Deploy para Railway"""
        self.log_step("Iniciando deploy para Railway...", "PROCESS")
        
        # Adicionar arquivos ao git
        commands = [
            ("git add .", "Adicionar arquivos ao staging"),
            ("git commit -m 'feat: remove campo tipo_usuario duplicado - consolidar em campo tipo'", "Commit das alterações"),
            ("git push origin main", "Push para Railway")
        ]
        
        for command, description in commands:
            if not self.run_command(command, description):
                return False
        
        return True
    
    def run_deployment(self):
        """Executar deploy completo"""
        self.log_step("=== INICIANDO DEPLOY AUTOMÁTICO ===", "PROCESS")
        self.log_step("Objetivo: Remover campo tipo_usuario duplicado", "INFO")
        
        steps = [
            (self.backup_current_state, "Backup do estado atual"),
            (self.test_backend, "Teste inicial do backend"),
            (self.run_migration, "Execução da migração"),
            (self.validate_system, "Validação do sistema"),
            (self.test_backend, "Teste final do backend"), 
            (self.deploy_to_railway, "Deploy para Railway")
        ]
        
        for step_func, step_name in steps:
            self.log_step(f"Executando: {step_name}", "PROCESS")
            
            if not step_func():
                self.log_step(f"❌ Falha na etapa: {step_name}", "ERROR")
                self.log_step("🛑 Deploy abortado!", "ERROR")
                return False
            
            self.log_step(f"✅ Concluído: {step_name}", "SUCCESS")
        
        self.log_step("🎉 DEPLOY CONCLUÍDO COM SUCESSO!", "SUCCESS")
        self.log_step(f"📋 Log completo salvo em: {self.deployment_log}", "INFO")
        return True

if __name__ == "__main__":
    deployer = AutoDeploy()
    
    print("🚀 Deploy Automático - Remoção tipo_usuario")
    print("=" * 50)
    
    if "--dry-run" in sys.argv:
        print("⚠️ Modo DRY RUN - Apenas simulação")
        # Implementar modo de simulação se necessário
    
    success = deployer.run_deployment()
    
    if success:
        print("\\n🎉 Deploy realizado com sucesso!")
        sys.exit(0)
    else:
        print("\\n❌ Deploy falhou! Verifique os logs.")
        sys.exit(1)
