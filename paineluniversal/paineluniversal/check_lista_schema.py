#!/usr/bin/env python3
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_lista_table():
    """Verificar esquema da tabela listas"""
    try:
        # Conectar ao banco SQLite local
        conn = sqlite3.connect('eventos.db')
        cursor = conn.cursor()
        
        # Verificar esquema da tabela listas
        cursor.execute("PRAGMA table_info(listas)")
        columns = cursor.fetchall()
        
        logger.info("📋 Colunas da tabela listas:")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Verificar se existe coluna tipo
        has_tipo = any(col[1] == 'tipo' for col in columns)
        has_tipo_usuario = any(col[1] == 'tipo_usuario' for col in columns)
        
        logger.info(f"🔍 Coluna 'tipo': {'✅ EXISTS' if has_tipo else '❌ NOT FOUND'}")
        logger.info(f"🔍 Coluna 'tipo_usuario': {'✅ EXISTS' if has_tipo_usuario else '❌ NOT FOUND'}")
        
        conn.close()
        return has_tipo, has_tipo_usuario
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar esquema: {e}")
        return False, False

if __name__ == "__main__":
    logger.info("🔧 Verificando esquema da tabela listas...")
    check_lista_table()
