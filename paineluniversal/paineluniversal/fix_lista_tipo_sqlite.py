#!/usr/bin/env python3
"""
Migração local para corrigir nome da coluna na tabela listas (SQLite).
Renomeia tipo_usuario para tipo.
"""

import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_lista_tipo_column_sqlite():
    """Corrige nome da coluna tipo_usuario para tipo na tabela listas (SQLite)"""
    
    db_path = "eventos.db"
    
    if not os.path.exists(db_path):
        logger.error(f"❌ Banco de dados {db_path} não encontrado!")
        return False
    
    connection = None
    cursor = None
    
    try:
        # Conectar ao SQLite
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Verificar se a coluna tipo_usuario existe
        cursor.execute("PRAGMA table_info(listas)")
        columns = cursor.fetchall()
        
        has_tipo_usuario = any(col[1] == 'tipo_usuario' for col in columns)
        has_tipo = any(col[1] == 'tipo' for col in columns)
        
        if has_tipo_usuario and not has_tipo:
            logger.info("✅ Coluna tipo_usuario encontrada. Iniciando migração...")
            
            # No SQLite, não podemos renomear colunas diretamente
            # Vamos criar uma nova tabela, copiar os dados e renomear
            
            # 1. Criar nova tabela com nome correto
            cursor.execute("""
                CREATE TABLE listas_new (
                    id INTEGER PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    preco DECIMAL(10,2) DEFAULT 0,
                    limite_vendas INTEGER,
                    vendas_realizadas INTEGER DEFAULT 0,
                    ativa BOOLEAN DEFAULT 1,
                    evento_id INTEGER NOT NULL,
                    promoter_id INTEGER,
                    descricao TEXT,
                    codigo_cupom VARCHAR(50),
                    desconto_percentual DECIMAL(5,2) DEFAULT 0,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evento_id) REFERENCES eventos (id),
                    FOREIGN KEY (promoter_id) REFERENCES usuarios (id)
                )
            """)
            
            # 2. Copiar dados da tabela antiga para a nova
            cursor.execute("""
                INSERT INTO listas_new (
                    id, nome, tipo, preco, limite_vendas, vendas_realizadas,
                    ativa, evento_id, promoter_id, descricao, codigo_cupom,
                    desconto_percentual, criado_em
                )
                SELECT 
                    id, nome, tipo_usuario, preco, limite_vendas, vendas_realizadas,
                    ativa, evento_id, promoter_id, descricao, codigo_cupom,
                    desconto_percentual, criado_em
                FROM listas
            """)
            
            # 3. Remover tabela antiga
            cursor.execute("DROP TABLE listas")
            
            # 4. Renomear nova tabela
            cursor.execute("ALTER TABLE listas_new RENAME TO listas")
            
            connection.commit()
            logger.info("✅ Migração SQLite concluída! Coluna renomeada de tipo_usuario para tipo.")
            
        elif has_tipo and not has_tipo_usuario:
            logger.info("✅ Coluna 'tipo' já existe. Migração não necessária.")
            
        else:
            logger.error("❌ Estado inconsistente das colunas!")
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
    logger.info("🔧 Iniciando correção da coluna tipo na tabela listas (SQLite)...")
    
    if fix_lista_tipo_column_sqlite():
        logger.info("✅ Migração concluída com sucesso!")
    else:
        logger.error("❌ Falha na migração!")
