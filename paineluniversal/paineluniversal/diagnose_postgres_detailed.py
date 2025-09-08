#!/usr/bin/env python3
"""
Diagnóstico avançado de conexão PostgreSQL
"""
import os
import sys
import socket
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_detailed_connection():
    """Teste detalhado de conectividade"""
    print("🔍 DIAGNÓSTICO AVANÇADO POSTGRESQL")
    print("=" * 50)
    
    # 1. Teste de conectividade de rede
    print("1. Testando conectividade de rede...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("✅ Porta 5432 acessível")
        else:
            print(f"❌ Porta 5432 inacessível (código: {result})")
            return False
    except Exception as e:
        print(f"❌ Erro na conectividade: {e}")
        return False
    
    # 2. Teste com diferentes hosts
    hosts_to_test = ['localhost', '127.0.0.1', '::1']
    
    for host in hosts_to_test:
        print(f"\n2. Testando host: {host}")
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=5432,
                database="paineluniversal",
                user="postgres", 
                password="postgres",
                connect_timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            print(f"✅ Conexão bem-sucedida com {host}")
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"❌ Erro operacional com {host}: {e}")
        except Exception as e:
            print(f"❌ Erro geral com {host}: {e}")
    
    # 3. Verificar configuração PostgreSQL
    print(f"\n3. Verificando configuração...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    
    return False

if __name__ == "__main__":
    success = test_detailed_connection()
    if success:
        print("\n🎉 Conexão PostgreSQL funcionando!")
    else:
        print("\n❌ Problema na conexão PostgreSQL")
        print("\n💡 Possíveis soluções:")
        print("- Verificar se PostgreSQL permite conexões locais")
        print("- Verificar arquivo pg_hba.conf")
        print("- Verificar se a senha está correta")
    
    sys.exit(0 if success else 1)
