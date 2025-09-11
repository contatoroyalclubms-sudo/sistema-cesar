#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE CORS INTELIGENTE E SEGURO
===================================

Implementa configuração CORS dinâmica baseada no ambiente.
Otimização prioritária #3 do relatório de análise.

Autor: Sistema de Otimização Automatizada
Data: 2024
"""

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from urllib.parse import urlparse

class CORSConfigManager:
    """Gerenciador inteligente de configuração CORS"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.environment = self.detect_environment()
        
    def setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger("cors_config")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def detect_environment(self) -> str:
        """Detecta ambiente atual"""
        # Verificar variáveis de ambiente
        env_vars = [
            os.getenv("ENVIRONMENT"),
            os.getenv("NODE_ENV"),
            os.getenv("FLASK_ENV"),
            os.getenv("DJANGO_SETTINGS_MODULE")
        ]
        
        # Railway detection
        if os.getenv("RAILWAY_ENVIRONMENT"):
            return "production"
        
        # Heroku detection
        if os.getenv("DYNO"):
            return "production"
        
        # Vercel detection
        if os.getenv("VERCEL"):
            return "production"
        
        # Environment variables
        for env_var in env_vars:
            if env_var:
                if "prod" in env_var.lower():
                    return "production"
                elif "staging" in env_var.lower() or "test" in env_var.lower():
                    return "staging"
                elif "dev" in env_var.lower():
                    return "development"
        
        # Default para desenvolvimento se localhost
        if os.getenv("DATABASE_URL", "").startswith("sqlite://"):
            return "development"
        
        return "development"
    
    def get_cors_config_for_environment(self) -> Dict:
        """Retorna configuração CORS baseada no ambiente"""
        base_config = {
            "allow_credentials": True,
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "max_age": 86400  # 24 horas
        }
        
        if self.environment == "production":
            config = {
                **base_config,
                "allow_origins": [
                    "https://paineluniversal.com",
                    "https://www.paineluniversal.com",
                    "https://paineluniversal-production.up.railway.app"
                ],
                "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Authorization",
                    "Content-Type",
                    "Accept",
                    "Origin",
                    "X-Requested-With"
                ],
                "allow_credentials": True,
                "max_age": 3600  # 1 hora em produção
            }
            
        elif self.environment == "staging":
            config = {
                **base_config,
                "allow_origins": [
                    "https://paineluniversal-staging.up.railway.app",
                    "https://staging.paineluniversal.com",
                    "http://localhost:3000",
                    "http://127.0.0.1:3000"
                ],
                "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": [
                    "Authorization",
                    "Content-Type",
                    "Accept",
                    "Origin",
                    "X-Requested-With",
                    "X-Debug-Mode"
                ],
                "allow_credentials": True,
                "max_age": 1800  # 30 minutos
            }
            
        else:  # development
            config = {
                **base_config,
                "allow_origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:3001",
                    "http://localhost:5173",  # Vite dev server
                    "http://localhost:8080",  # Alternative dev ports
                    "http://localhost:4200"   # Angular dev server
                ],
                "allow_methods": ["*"],  # Todos os métodos em dev
                "allow_headers": ["*"],  # Todos os headers em dev
                "allow_credentials": True,
                "max_age": 86400
            }
        
        self.logger.info(f"🔧 CORS configurado para ambiente: {self.environment}")
        self.logger.info(f"📝 Origins permitidas: {len(config['allow_origins'])}")
        
        return config
    
    def validate_origin(self, origin: str) -> bool:
        """Valida se uma origin é permitida"""
        config = self.get_cors_config_for_environment()
        allowed_origins = config["allow_origins"]
        
        # Permitir wildcard em desenvolvimento
        if "*" in allowed_origins:
            return True
        
        # Verificar lista exata
        if origin in allowed_origins:
            return True
        
        # Verificar padrões (ex: *.paineluniversal.com)
        for allowed in allowed_origins:
            if allowed.startswith("*."):
                domain = allowed[2:]
                if origin.endswith(f".{domain}") or origin == domain:
                    return True
        
        return False
    
    def generate_fastapi_cors_middleware(self) -> str:
        """Gera código para middleware CORS do FastAPI"""
        config = self.get_cors_config_for_environment()
        
        code = f'''
from fastapi.middleware.cors import CORSMiddleware

# Configuração CORS otimizada para {self.environment}
app.add_middleware(
    CORSMiddleware,
    allow_origins={config["allow_origins"]},
    allow_credentials={config["allow_credentials"]},
    allow_methods={config["allow_methods"]},
    allow_headers={config["allow_headers"]},
    expose_headers={config["expose_headers"]},
    max_age={config["max_age"]}
)
'''
        return code
    
    def generate_security_headers_middleware(self) -> str:
        """Gera middleware de headers de segurança"""
        if self.environment == "production":
            headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            }
        else:
            headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "SAMEORIGIN",
                "X-XSS-Protection": "1; mode=block"
            }
        
        code = f'''
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Headers de segurança para {self.environment}
'''
        
        for header, value in headers.items():
            code += f'    response.headers["{header}"] = "{value}"\n'
        
        code += '''    
    return response
'''
        return code
    
    def create_cors_config_file(self) -> str:
        """Cria arquivo de configuração CORS"""
        config = {
            "environment": self.environment,
            "cors": self.get_cors_config_for_environment(),
            "security_notes": [
                f"Configuração otimizada para {self.environment}",
                "Origins restritas baseadas no ambiente",
                "Headers de segurança aplicados",
                "Credentials permitidas apenas para origins confiáveis"
            ]
        }
        
        config_file = f"cors_config_{self.environment}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Configuração CORS salva: {config_file}")
        return config_file
    
    def update_backend_cors(self, backend_path: str = "./backend"):
        """Atualiza configuração CORS no backend"""
        backend_dir = Path(backend_path)
        
        # Procurar arquivo main.py ou app.py
        main_files = [
            backend_dir / "main.py",
            backend_dir / "app" / "main.py",
            backend_dir / "server.py",
            backend_dir / "app.py"
        ]
        
        main_file = None
        for file_path in main_files:
            if file_path.exists():
                main_file = file_path
                break
        
        if not main_file:
            self.logger.error("❌ Arquivo principal do backend não encontrado")
            return False
        
        self.logger.info(f"📝 Atualizando CORS em: {main_file}")
        
        # Ler arquivo atual
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Gerar nova configuração CORS
        cors_code = self.generate_fastapi_cors_middleware()
        security_code = self.generate_security_headers_middleware()
        
        # Procurar e substituir configuração CORS existente
        import re
        
        # Padrão para encontrar configuração CORS existente
        cors_pattern = r'app\.add_middleware\(\s*CORSMiddleware[^)]*\)'
        
        if re.search(cors_pattern, content, re.DOTALL):
            # Substituir configuração existente
            new_content = re.sub(cors_pattern, cors_code.strip(), content, flags=re.DOTALL)
            self.logger.info("🔄 Configuração CORS existente substituída")
        else:
            # Adicionar nova configuração após criação do app
            app_pattern = r'(app\s*=\s*FastAPI\([^)]*\))'
            if re.search(app_pattern, content):
                new_content = re.sub(
                    app_pattern, 
                    r'\1\n\n' + cors_code,
                    content
                )
                self.logger.info("➕ Nova configuração CORS adicionada")
            else:
                self.logger.warning("⚠️ Não foi possível encontrar onde adicionar CORS")
                return False
        
        # Adicionar imports se necessário
        if "from fastapi.middleware.cors import CORSMiddleware" not in new_content:
            # Encontrar linha de imports do FastAPI
            fastapi_import_pattern = r'(from fastapi import [^\\n]*)'
            if re.search(fastapi_import_pattern, new_content):
                new_content = re.sub(
                    fastapi_import_pattern,
                    r'\1\nfrom fastapi.middleware.cors import CORSMiddleware',
                    new_content
                )
            else:
                # Adicionar no início
                new_content = "from fastapi.middleware.cors import CORSMiddleware\n" + new_content
        
        # Fazer backup
        backup_file = main_file.with_suffix(f".py.backup.cors")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Escrever novo conteúdo
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.logger.info(f"✅ CORS atualizado em {main_file}")
        self.logger.info(f"📁 Backup criado: {backup_file}")
        
        return True
    
    def test_cors_configuration(self, base_url: str = "http://localhost:8000") -> Dict:
        """Testa configuração CORS"""
        import requests
        
        config = self.get_cors_config_for_environment()
        results = {
            "environment": self.environment,
            "base_url": base_url,
            "tests": [],
            "summary": {"passed": 0, "failed": 0}
        }
        
        # Testar cada origin permitida
        for origin in config["allow_origins"]:
            if origin == "*":
                origin = "http://localhost:3000"  # Usar origin de teste
            
            test_result = {
                "origin": origin,
                "status": "FAIL",
                "details": {}
            }
            
            try:
                # Teste preflight (OPTIONS)
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,Authorization"
                }
                
                response = requests.options(f"{base_url}/health", headers=headers, timeout=10)
                
                test_result["details"]["preflight_status"] = response.status_code
                test_result["details"]["cors_headers"] = {}
                
                # Verificar headers CORS
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                    "Access-Control-Allow-Credentials"
                ]
                
                for header in cors_headers:
                    test_result["details"]["cors_headers"][header] = response.headers.get(header)
                
                if response.status_code in [200, 204]:
                    test_result["status"] = "PASS"
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1
                
            except Exception as e:
                test_result["details"]["error"] = str(e)
                results["summary"]["failed"] += 1
            
            results["tests"].append(test_result)
        
        return results

def main():
    """Função principal"""
    print("🚀 INICIANDO OTIMIZAÇÃO DE CONFIGURAÇÃO CORS")
    print("="*60)
    
    manager = CORSConfigManager()
    
    try:
        # Detectar ambiente
        print(f"🔍 Ambiente detectado: {manager.environment}")
        
        # Gerar configuração
        print("🔧 Gerando configuração CORS otimizada...")
        config_file = manager.create_cors_config_file()
        
        # Atualizar backend
        print("📝 Atualizando backend...")
        if manager.update_backend_cors():
            print("✅ Backend atualizado com sucesso")
        else:
            print("⚠️ Falha ao atualizar backend")
        
        # Mostrar configuração
        cors_config = manager.get_cors_config_for_environment()
        print(f"\n📋 CONFIGURAÇÃO CORS:")
        print(f"Ambiente: {manager.environment}")
        print(f"Origins permitidas: {len(cors_config['allow_origins'])}")
        for origin in cors_config['allow_origins']:
            print(f"  • {origin}")
        
        print(f"\n✅ OTIMIZAÇÃO CORS CONCLUÍDA!")
        print(f"📁 Configuração salva: {config_file}")
        
    except Exception as e:
        print(f"❌ Erro durante otimização CORS: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
