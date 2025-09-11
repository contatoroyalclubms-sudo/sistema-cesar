#!/usr/bin/env python3
"""
Teste simples de conexão PostgreSQL
"""
import asyncio
import asyncpg
import os
import sys

async def test_connection():
    database_url = "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway"
    
    try:
        print("Tentando conectar ao PostgreSQL...", flush=True)
        conn = await asyncpg.connect(database_url)
        print("Conectado com sucesso!", flush=True)
        
        # Verificar se tabela produtos existe
        exists = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'produtos')")
        print(f"Tabela produtos existe: {exists}", flush=True)
        
        if exists:
            # Verificar se coluna evento_id existe
            has_evento_id = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'produtos' 
                    AND column_name = 'evento_id'
                )
            """)
            print(f"Coluna evento_id existe: {has_evento_id}", flush=True)
            
            # Contar produtos
            count = await conn.fetchval("SELECT COUNT(*) FROM produtos")
            print(f"Total de produtos: {count}", flush=True)
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"ERRO: {e}", flush=True)
        return False

if __name__ == "__main__":
    print("=== TESTE DE CONEXÃO POSTGRESQL ===", flush=True)
    success = asyncio.run(test_connection())
    print(f"Resultado: {'SUCESSO' if success else 'FALHA'}", flush=True)
