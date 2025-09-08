#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE INICIALIZAÇÃO AUTOMÁTICA DO SERVIDOR
===============================================

Inicializa o servidor com auto-restart e monitoramento.
Otimização crítica #1 do relatório de análise.

Autor: Sistema de Otimização Automatizada
Data: 2024
"""

import os
import sys
import time
import subprocess
import logging
import signal
import psutil
from pathlib import Path
from typing import Optional

class ServerManager:
    """Gerenciador de servidor com auto-restart"""
    
    def __init__(self, backend_path: str = "./backend"):
        self.backend_path = Path(backend_path).resolve()
        self.server_process: Optional[subprocess.Popen] = None
        self.logger = self.setup_logging()
        self.should_restart = True
        
        # Configurações
        self.server_script = "server.py"
        self.max_restart_attempts = 5
        self.restart_delay = 10  # segundos
        
    def setup_logging(self) -> logging.Logger:
        """Configura sistema de logs"""
        logger = logging.getLogger("server_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler
            file_handler = logging.FileHandler("server_manager.log")
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def find_server_script(self) -> Optional[Path]:
        """Encontra o script do servidor"""
        possible_scripts = [
            self.backend_path / "server.py",
            self.backend_path / "main.py",
            self.backend_path / "app.py",
            self.backend_path / "run.py"
        ]
        
        for script in possible_scripts:
            if script.exists():
                self.logger.info(f"📍 Script do servidor encontrado: {script}")
                return script
        
        self.logger.error("❌ Script do servidor não encontrado")
        return None
    
    def is_port_in_use(self, port: int = 8000) -> bool:
        """Verifica se a porta está em uso"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except Exception:
            return False
    
    def kill_existing_servers(self, port: int = 8000):
        """Mata servidores existentes na porta"""
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline'] or []
                    cmdline_str = ' '.join(cmdline).lower()
                    
                    # Verificar se é um servidor Python na porta
                    if ('python' in cmdline_str and 
                        ('server.py' in cmdline_str or 
                         'uvicorn' in cmdline_str or
                         ':8000' in cmdline_str)):
                        
                        self.logger.info(f"🔪 Matando processo existente: PID {proc.info['pid']}")
                        psutil.Process(proc.info['pid']).terminate()
                        killed_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao matar processos: {e}")
        
        if killed_count > 0:
            self.logger.info(f"✅ {killed_count} processos terminados")
            time.sleep(3)  # Aguardar processos terminarem
    
    def start_server(self) -> bool:
        """Inicia o servidor"""
        try:
            server_script = self.find_server_script()
            if not server_script:
                return False
            
            # Matar servidores existentes
            self.kill_existing_servers()
            
            # Verificar se porta ainda está em uso
            if self.is_port_in_use(8000):
                self.logger.warning("⚠️ Porta 8000 ainda está em uso")
                time.sleep(5)
            
            self.logger.info(f"🚀 Iniciando servidor: {server_script}")
            
            # Iniciar processo
            self.server_process = subprocess.Popen(
                [sys.executable, server_script.name],
                cwd=server_script.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Aguardar inicialização
            self.logger.info("⏳ Aguardando inicialização do servidor...")
            time.sleep(15)
            
            # Verificar se está rodando
            if self.server_process.poll() is None:
                self.logger.info("✅ Servidor iniciado com sucesso")
                return True
            else:
                stdout, stderr = self.server_process.communicate(timeout=5)
                self.logger.error(f"❌ Servidor falhou ao iniciar:")
                self.logger.error(f"STDOUT: {stdout}")
                self.logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self):
        """Para o servidor"""
        if self.server_process:
            try:
                self.logger.info("🛑 Parando servidor...")
                
                # Tentar terminar graciosamente
                self.server_process.terminate()
                
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Forçar kill se não parou
                    self.logger.warning("⚠️ Forçando parada do servidor...")
                    self.server_process.kill()
                    self.server_process.wait()
                
                self.logger.info("✅ Servidor parado")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao parar servidor: {e}")
            
            finally:
                self.server_process = None
    
    def is_server_healthy(self) -> bool:
        """Verifica se o servidor está saudável"""
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def monitor_and_restart(self):
        """Monitora servidor e reinicia se necessário"""
        restart_attempts = 0
        
        # Configurar handler para sinais
        def signal_handler(signum, frame):
            self.logger.info("📡 Sinal recebido - Parando monitoramento...")
            self.should_restart = False
            self.stop_server()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.logger.info("👁️ Iniciando monitoramento de servidor...")
        
        while self.should_restart and restart_attempts < self.max_restart_attempts:
            # Verificar se processo ainda existe
            if self.server_process and self.server_process.poll() is not None:
                self.logger.warning("⚠️ Processo do servidor morreu")
                
                # Ler logs de erro
                try:
                    stdout, stderr = self.server_process.communicate(timeout=5)
                    if stderr:
                        self.logger.error(f"STDERR: {stderr}")
                except Exception:
                    pass
                
                self.server_process = None
            
            # Verificar saúde do servidor
            if not self.is_server_healthy():
                if self.server_process:
                    self.logger.warning("⚠️ Servidor não está saudável - Reiniciando...")
                    self.stop_server()
                else:
                    self.logger.warning("⚠️ Servidor não está rodando - Iniciando...")
                
                restart_attempts += 1
                self.logger.info(f"🔄 Tentativa de restart {restart_attempts}/{self.max_restart_attempts}")
                
                if self.start_server():
                    restart_attempts = 0  # Reset contador em caso de sucesso
                    self.logger.info("✅ Servidor reiniciado com sucesso")
                else:
                    self.logger.error(f"❌ Falha na tentativa {restart_attempts}")
                    if restart_attempts < self.max_restart_attempts:
                        self.logger.info(f"⏳ Aguardando {self.restart_delay}s antes da próxima tentativa...")
                        time.sleep(self.restart_delay)
            
            # Aguardar antes da próxima verificação
            time.sleep(30)
        
        if restart_attempts >= self.max_restart_attempts:
            self.logger.error("❌ Máximo de tentativas de restart atingido - Abortando")
        
        self.logger.info("🛑 Monitoramento finalizado")

def main():
    """Função principal"""
    print("🚀 SISTEMA DE INICIALIZAÇÃO AUTOMÁTICA DO SERVIDOR")
    print("="*60)
    
    manager = ServerManager()
    
    try:
        # Iniciar servidor
        if manager.start_server():
            print("✅ Servidor iniciado com sucesso")
            print("👁️ Iniciando monitoramento contínuo...")
            print("💡 Pressione Ctrl+C para parar")
            
            # Iniciar monitoramento
            manager.monitor_and_restart()
        else:
            print("❌ Falha ao iniciar servidor")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        manager.stop_server()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        manager.stop_server()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
