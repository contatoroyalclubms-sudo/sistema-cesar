#!/usr/bin/env python3
"""
Teste e Configuração de Credenciais Reais MEEP
"""

import os
import sys
import httpx
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Adicionar backend ao path
sys.path.append(str(Path(__file__).parent / "paineluniversal" / "backend"))

print("\n" + "="*60)
print("    TESTE DE CREDENCIAIS MEEP")
print("="*60)

def test_credentials():
    """Testar credenciais MEEP"""
    
    # Carregar configurações
    load_dotenv('.env.meep')
    
    base_url = os.getenv("MEEP_BASE_URL", "https://beta.portal.meep.com.br")
    auth_mode = os.getenv("MEEP_AUTH_MODE", "cookie")
    user = os.getenv("MEEP_USER", "")
    password = os.getenv("MEEP_PASS", "")
    
    print(f"\n[INFO] Configuração atual:")
    print(f"  Base URL: {base_url}")
    print(f"  Auth Mode: {auth_mode}")
    print(f"  User: {user or 'Não configurado'}")
    print(f"  Password: {'*' * len(password) if password else 'Não configurado'}")
    
    if not user or not password:
        print("\n[ERRO] Credenciais não configuradas em .env.meep")
        print("\nPor favor, configure as seguintes variáveis em .env.meep:")
        print("  MEEP_USER=seu-email@meep.com.br")
        print("  MEEP_PASS=sua-senha-segura")
        return False
    
    print("\n[1] Testando conexão com o portal MEEP...")
    
    with httpx.Client() as client:
        try:
            # Testar conexão básica
            response = client.get(base_url, timeout=10)
            if response.status_code < 500:
                print(f"   OK: Portal acessível (status: {response.status_code})")
            else:
                print(f"   ERRO: Portal indisponível (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ERRO: Não foi possível conectar: {e}")
            return False
    
    print("\n[2] Testando autenticação...")
    
    # Testar diferentes métodos de autenticação
    auth_methods = [
        ("cookie", "/api/auth/login"),
        ("session", "/api/login"),
        ("bearer", "/auth/login")
    ]
    
    successful_auth = None
    
    for method, endpoint in auth_methods:
        print(f"\n   Tentando {method} em {endpoint}...")
        
        try:
            with httpx.Client() as client:
                url = f"{base_url}{endpoint}"
                
                # Payload de login
                payload = {
                    "email": user,
                    "password": password,
                    "username": user,  # alguns sistemas usam username
                    "user": user       # outros usam user
                }
                
                response = client.post(
                    url,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   SUCESSO: Autenticação {method} funcionou!")
                    successful_auth = method
                    
                    # Salvar resposta para análise
                    data = response.json()
                    print(f"   Resposta: {list(data.keys())}")
                    
                    # Verificar token/session
                    if "token" in data:
                        print(f"   Token recebido: {data['token'][:20]}...")
                    if "session_id" in data:
                        print(f"   Session ID: {data['session_id'][:20]}...")
                    
                    break
                else:
                    print(f"   Falhou: Status {response.status_code}")
                    if response.text:
                        try:
                            error = response.json()
                            print(f"   Erro: {error}")
                        except:
                            print(f"   Resposta: {response.text[:100]}")
                            
        except Exception as e:
            print(f"   Erro: {e}")
    
    if successful_auth:
        print(f"\n[SUCESSO] Autenticação {successful_auth} funcionou!")
        print("\nAtualizando .env.meep com o método correto...")
        
        # Atualizar arquivo de configuração
        update_env_file(successful_auth)
        return True
    else:
        print("\n[ERRO] Nenhum método de autenticação funcionou")
        print("\nPossíveis causas:")
        print("  1. Credenciais incorretas")
        print("  2. Portal MEEP com API diferente")
        print("  3. Conta sem permissões de API")
        return False

def update_env_file(auth_method):
    """Atualizar arquivo .env.meep com método correto"""
    env_file = Path(".env.meep")
    
    if env_file.exists():
        content = env_file.read_text()
        
        # Atualizar auth mode
        import re
        content = re.sub(
            r'MEEP_AUTH_MODE=.*',
            f'MEEP_AUTH_MODE={auth_method}',
            content
        )
        
        env_file.write_text(content)
        print(f"   Arquivo .env.meep atualizado com auth_mode={auth_method}")

def test_api_access():
    """Testar acesso às APIs após autenticação"""
    print("\n[3] Testando acesso às APIs...")
    
    from app.services.meep_client import MeepClient
    
    client = MeepClient()
    
    if not client.login():
        print("   ERRO: Login falhou com MeepClient")
        return False
    
    # Testar endpoints
    endpoints = [
        ("/api/events", "Eventos"),
        ("/api/users/me", "Perfil do usuário"),
        ("/api/tickets", "Ingressos"),
        ("/api/analytics/summary", "Analytics")
    ]
    
    working_endpoints = []
    
    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"   OK: {name} ({endpoint})")
                working_endpoints.append(endpoint)
            else:
                print(f"   Erro: {name} - Status {response.status_code}")
        except Exception as e:
            print(f"   Erro: {name} - {e}")
    
    client.close()
    
    if working_endpoints:
        print(f"\n[SUCESSO] {len(working_endpoints)} endpoints funcionando")
        return True
    else:
        print("\n[AVISO] Nenhum endpoint acessível")
        return False

def save_production_config():
    """Salvar configuração de produção"""
    print("\n[4] Salvando configuração de produção...")
    
    config = {
        "timestamp": datetime.now().isoformat(),
        "environment": "production",
        "base_url": os.getenv("MEEP_BASE_URL"),
        "auth_mode": os.getenv("MEEP_AUTH_MODE"),
        "endpoints": {
            "login": os.getenv("MEEP_LOGIN_ENDPOINT"),
            "events": os.getenv("MEEP_EVENTS_ENDPOINT"),
            "tickets": os.getenv("MEEP_TICKETS_ENDPOINT"),
            "checkin": os.getenv("MEEP_CHECKIN_ENDPOINT"),
            "analytics": os.getenv("MEEP_ANALYTICS_ENDPOINT")
        },
        "sync": {
            "interval": os.getenv("MEEP_SYNC_INTERVAL", "3600"),
            "batch_size": os.getenv("MEEP_BATCH_SIZE", "100"),
            "retry_attempts": os.getenv("MEEP_RETRY_ATTEMPTS", "3")
        },
        "status": "configured"
    }
    
    config_file = Path("data/config/meep_production.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"   Configuração salva em: {config_file}")
    return config

def main():
    """Executar testes de credenciais"""
    
    print("\nEste script vai:")
    print("  1. Testar conexão com o portal MEEP")
    print("  2. Validar suas credenciais")
    print("  3. Identificar o método de autenticação correto")
    print("  4. Testar acesso às APIs")
    print("  5. Salvar configuração de produção")
    
    # Testar credenciais
    if not test_credentials():
        print("\n[ERRO] Falha na autenticação")
        print("\nPróximos passos:")
        print("  1. Verifique suas credenciais em .env.meep")
        print("  2. Confirme que tem acesso ao portal MEEP")
        print("  3. Entre em contato com o suporte se necessário")
        return False
    
    # Testar acesso às APIs
    if test_api_access():
        print("\n[SUCESSO] APIs acessíveis")
    else:
        print("\n[AVISO] APIs com acesso limitado")
    
    # Salvar configuração
    config = save_production_config()
    
    print("\n" + "="*60)
    print("    CONFIGURAÇÃO COMPLETA")
    print("="*60)
    print("\n CREDENCIAIS VALIDADAS E SISTEMA PRONTO!")
    print("\nAgora você pode:")
    print("  1. Usar a integração MEEP em produção")
    print("  2. Configurar webhooks no portal")
    print("  3. Ativar sincronização automática")
    print("  4. Acessar o dashboard em /api/meep/dashboard")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)