#!/usr/bin/env python3
"""
Migração para corrigir nome da coluna na tabela listas.
Renomeia tipo_usuario para tipo.
"""

import psycopg2
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_lista_tipo_column():
    """Corrige nome da coluna tipo_usuario para tipo na tabela listas"""
    
    connection = None
    cursor = None
    
    try:
        # Conectar ao PostgreSQL com novas credenciais
        connection = psycopg2.connect(
            host="aws-0-sa-east-1.pooler.supabase.com",
            port=6543,
            database="postgres",
            user="postgres.ufqhqmlvkqogdgdmfzqx",
            password="YNtcgNOWiuxpJgWB"
        )
        
        cursor = connection.cursor()
        
        # Verificar se a coluna tipo_usuario existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'listas' AND column_name = 'tipo_usuario'
        """)
        
        if cursor.fetchone():
            logger.info("✅ Coluna tipo_usuario encontrada. Iniciando migração...")
            
            # Renomear a coluna
            cursor.execute("""
                ALTER TABLE listas RENAME COLUMN tipo_usuario TO tipo;
            """)
            
            connection.commit()
            logger.info("✅ Coluna renomeada de tipo_usuario para tipo com sucesso!")
            
        else:
            logger.info("ℹ️  Coluna tipo_usuario não encontrada, verificando se 'tipo' já existe...")
            
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'listas' AND column_name = 'tipo'
            """)
            
            if cursor.fetchone():
                logger.info("✅ Coluna 'tipo' já existe. Migração não necessária.")
            else:
                logger.error("❌ Nem 'tipo_usuario' nem 'tipo' foram encontradas!")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    logger.info("🔧 Iniciando correção da coluna tipo na tabela listas...")
    
    if fix_lista_tipo_column():
        logger.info("✅ Migração concluída com sucesso!")
    else:
        logger.error("❌ Falha na migração!")
