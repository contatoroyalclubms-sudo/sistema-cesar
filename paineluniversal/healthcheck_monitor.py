#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE HEALTHCHECK E MONITORAMENTO ROBUSTO
==============================================

Implementa monitoramento contínuo, auto-restart e alertas para o Painel Universal.
Otimização prioritária #1 do relatório de análise.

Autor: Sistema de Otimização Automatizada
Data: 2024
"""

import asyncio
import json
import time
import psutil
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class HealthcheckMonitor:
    """Monitor robusto de healthcheck com auto-restart e alertas"""
    
    def __init__(self, config_file: str = "healthcheck_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "total_checks": 0,
            "failed_checks": 0,
            "restarts_performed": 0,
            "last_restart": None,
            "uptime_percentage": 100.0,
            "alerts_sent": 0
        }
        
    def load_config(self) -> Dict:
        """Carrega configuração do healthcheck"""
        default_config = {
            "endpoints": {
                "primary": "http://localhost:8000",
                "railway": "https://paineluniversal-production.up.railway.app",
                "health_path": "/health",
                "timeout": 10
            },
            "monitoring": {
                "check_interval": 30,  # segundos
                "failure_threshold": 3,  # falhas consecutivas
                "restart_cooldown": 300,  # 5 minutos entre restarts
                "max_restarts_hour": 3
            },
            "server": {
                "start_command": "python server.py",
                "working_directory": "./backend",
                "process_name": "server.py",
                "startup_wait": 15
            },
            "alerts": {
                "enabled": True,
                "webhook_url": None,
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_addresses": []
                }
            },
            "logging": {
                "level": "INFO",
                "file": "healthcheck.log",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            else:
                # Create default config file
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                print(f"📁 Arquivo de configuração criado: {self.config_file}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar configuração: {e}")
            
        return default_config
    
    def setup_logging(self):
        """Configura sistema de logs"""
        log_config = self.config["logging"]
        
        # Configurar logger
        self.logger = logging.getLogger("healthcheck")
        self.logger.setLevel(getattr(logging, log_config["level"]))
        
        # Handler para arquivo
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_config["file"],
            maxBytes=log_config["max_size_mb"] * 1024 * 1024,
            backupCount=log_config["backup_count"]
        )
        
        # Handler para console
        console_handler = logging.StreamHandler()
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def check_health(self, url: str) -> Dict:
        """Verifica saúde de um endpoint"""
        start_time = time.time()
        result = {
            "url": url,
            "status": "FAIL",
            "response_time": 0,
            "status_code": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.get(
                f"{url}{self.config['endpoints']['health_path']}",
                timeout=self.config['endpoints']['timeout']
            )
            
            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = "OK"
                self.logger.debug(f"✅ Health check OK: {url}")
            else:
                result["error"] = f"HTTP {response.status_code}"
                self.logger.warning(f"⚠️ Health check failed: {url} - {result['error']}")
                
        except requests.exceptions.RequestException as e:
            result["response_time"] = time.time() - start_time
            result["error"] = str(e)
            self.logger.warning(f"❌ Health check error: {url} - {result['error']}")
        
        return result
    
    def is_server_running(self) -> bool:
        """Verifica se o processo do servidor está rodando"""
        try:
            process_name = self.config["server"]["process_name"]
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process_name in ' '.join(proc.info['cmdline'] or []):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar processo: {e}")
            return False
    
    def start_server(self) -> bool:
        """Inicia o servidor"""
        try:
            server_config = self.config["server"]
            
            self.logger.info("🚀 Iniciando servidor...")
            
            # Mudar para diretório correto
            working_dir = Path(server_config["working_directory"]).resolve()
            
            # Iniciar processo
            process = subprocess.Popen(
                server_config["start_command"].split(),
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar inicialização
            time.sleep(server_config["startup_wait"])
            
            # Verificar se está rodando
            if self.is_server_running():
                self.logger.info("✅ Servidor iniciado com sucesso")
                self.stats["restarts_performed"] += 1
                self.stats["last_restart"] = datetime.now().isoformat()
                return True
            else:
                self.logger.error("❌ Falha ao iniciar servidor")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Para o servidor"""
        try:
            process_name = self.config["server"]["process_name"]
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process_name in ' '.join(proc.info['cmdline'] or []):
                    proc.terminate()
                    proc.wait(timeout=10)
                    self.logger.info(f"🛑 Processo {proc.pid} terminado")
                    return True
                    
            return True  # Se não encontrou processo, consideramos "parado"
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao parar servidor: {e}")
            return False
    
    def restart_server(self) -> bool:
        """Reinicia o servidor"""
        self.logger.info("🔄 Reiniciando servidor...")
        
        # Parar servidor atual
        if not self.stop_server():
            self.logger.error("❌ Falha ao parar servidor")
            return False
        
        # Aguardar um pouco
        time.sleep(5)
        
        # Iniciar servidor
        return self.start_server()
    
    def send_alert(self, message: str, level: str = "WARNING"):
        """Envia alerta configurado"""
        if not self.config["alerts"]["enabled"]:
            return
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "stats": self.stats
        }
        
        # Webhook
        webhook_url = self.config["alerts"]["webhook_url"]
        if webhook_url:
            try:
                requests.post(webhook_url, json=alert_data, timeout=10)
                self.logger.info(f"📬 Alerta enviado via webhook: {level}")
            except Exception as e:
                self.logger.error(f"❌ Erro ao enviar webhook: {e}")
        
        # Email
        email_config = self.config["alerts"]["email"]
        if email_config["enabled"] and email_config["to_addresses"]:
            try:
                msg = MIMEMultipart()
                msg['From'] = email_config["username"]
                msg['To'] = ", ".join(email_config["to_addresses"])
                msg['Subject'] = f"[Painel Universal] {level}: {message}"
                
                body = f"""
Alerta do Sistema de Monitoramento:

Nível: {level}
Mensagem: {message}
Timestamp: {alert_data['timestamp']}

Estatísticas:
- Total de verificações: {self.stats['total_checks']}
- Verificações falhas: {self.stats['failed_checks']}
- Restarts realizados: {self.stats['restarts_performed']}
- Uptime: {self.stats['uptime_percentage']:.2f}%
- Último restart: {self.stats['last_restart'] or 'Nunca'}

Sistema de Monitoramento Painel Universal
"""
                
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)
                server.quit()
                
                self.logger.info(f"📧 Alerta enviado via email: {level}")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao enviar email: {e}")
        
        self.stats["alerts_sent"] += 1
    
    def update_stats(self, health_result: Dict):
        """Atualiza estatísticas"""
        self.stats["total_checks"] += 1
        
        if health_result["status"] != "OK":
            self.stats["failed_checks"] += 1
        
        # Calcular uptime
        total = self.stats["total_checks"]
        failed = self.stats["failed_checks"]
        self.stats["uptime_percentage"] = ((total - failed) / total) * 100 if total > 0 else 100.0
    
    def save_stats(self):
        """Salva estatísticas em arquivo"""
        try:
            stats_file = "healthcheck_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estatísticas: {e}")
    
    async def monitor_loop(self):
        """Loop principal de monitoramento"""
        self.logger.info("🚀 Iniciando monitoramento de healthcheck...")
        
        consecutive_failures = 0
        last_restart_time = 0
        restarts_this_hour = 0
        hour_start = time.time()
        
        while True:
            try:
                # Reset contador de restarts por hora
                if time.time() - hour_start > 3600:
                    restarts_this_hour = 0
                    hour_start = time.time()
                
                # Verificar health do endpoint primário
                primary_url = self.config["endpoints"]["primary"]
                health_result = self.check_health(primary_url)
                self.update_stats(health_result)
                
                if health_result["status"] == "OK":
                    consecutive_failures = 0
                    if self.stats["total_checks"] % 100 == 0:  # Log a cada 100 checks
                        self.logger.info(f"📊 Status: OK - Uptime: {self.stats['uptime_percentage']:.2f}%")
                else:
                    consecutive_failures += 1
                    self.logger.warning(f"⚠️ Falha {consecutive_failures}/{self.config['monitoring']['failure_threshold']}")
                    
                    # Verificar se deve reiniciar
                    failure_threshold = self.config["monitoring"]["failure_threshold"]
                    restart_cooldown = self.config["monitoring"]["restart_cooldown"]
                    max_restarts = self.config["monitoring"]["max_restarts_hour"]
                    
                    if (consecutive_failures >= failure_threshold and 
                        time.time() - last_restart_time > restart_cooldown and
                        restarts_this_hour < max_restarts):
                        
                        self.logger.error("❌ Limite de falhas atingido - Tentando restart")
                        self.send_alert(f"Servidor com falhas - Tentando restart automático", "CRITICAL")
                        
                        if self.restart_server():
                            consecutive_failures = 0
                            last_restart_time = time.time()
                            restarts_this_hour += 1
                            self.send_alert("Servidor reiniciado com sucesso", "INFO")
                        else:
                            self.send_alert("FALHA CRÍTICA: Não foi possível reiniciar servidor", "CRITICAL")
                
                # Salvar estatísticas periodicamente
                if self.stats["total_checks"] % 50 == 0:
                    self.save_stats()
                
                # Aguardar próximo check
                await asyncio.sleep(self.config["monitoring"]["check_interval"])
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no loop de monitoramento: {e}")
                await asyncio.sleep(30)  # Aguardar em caso de erro
    
    def generate_report(self) -> Dict:
        """Gera relatório de status"""
        uptime_hours = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds() / 3600
        
        report = {
            "system_status": "OK" if self.stats["uptime_percentage"] > 95 else "DEGRADED" if self.stats["uptime_percentage"] > 80 else "CRITICAL",
            "uptime_hours": round(uptime_hours, 2),
            "uptime_percentage": round(self.stats["uptime_percentage"], 2),
            "total_checks": self.stats["total_checks"],
            "failed_checks": self.stats["failed_checks"],
            "restarts_performed": self.stats["restarts_performed"],
            "last_restart": self.stats["last_restart"],
            "alerts_sent": self.stats["alerts_sent"],
            "avg_checks_per_hour": round(self.stats["total_checks"] / max(uptime_hours, 1), 2),
            "generated_at": datetime.now().isoformat()
        }
        
        return report

async def main():
    """Função principal"""
    monitor = HealthcheckMonitor()
    
    try:
        # Verificar se servidor está rodando
        if not monitor.is_server_running():
            print("⚠️ Servidor não está rodando - Tentando iniciar...")
            if monitor.start_server():
                print("✅ Servidor iniciado com sucesso")
            else:
                print("❌ Falha ao iniciar servidor")
                return
        
        # Iniciar monitoramento
        await monitor.monitor_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento finalizado")
    finally:
        monitor.save_stats()
        report = monitor.generate_report()
        print("\n📊 RELATÓRIO FINAL:")
        print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
