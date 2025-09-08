#!/usr/bin/env python3
"""
Script para tornar empresa_id opcional na tabela usuarios
Para SQLite, precisamos recriar a tabela
"""

from sqlalchemy import create_engine, text
from app.database import settings
import os

def make_empresa_optional():
    """Altera a coluna empresa_id para permitir NULL"""
    
    engine = create_engine(settings.database_url)
    
    with engine.connect() as connection:
        try:
            # Para SQLite, precisamos recriar a tabela
            print("Iniciando migração para tornar empresa_id opcional...")
            
            # 1. Criar tabela temporária com nova estrutura
            connection.execute(text("""
                CREATE TABLE usuarios_temp (
                    id INTEGER PRIMARY KEY,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    senha_hash VARCHAR(255) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    empresa_id INTEGER,  -- NULL permitido agora
                    ultimo_login DATETIME,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME,
                    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
                );
            """))
            
            # 2. Copiar dados da tabela original
            connection.execute(text("""
                INSERT INTO usuarios_temp 
                SELECT * FROM usuarios;
            """))
            
            # 3. Renomear tabelas
            connection.execute(text("DROP TABLE usuarios;"))
            connection.execute(text("ALTER TABLE usuarios_temp RENAME TO usuarios;"))
            
            # 4. Recriar índices
            connection.execute(text("CREATE INDEX ix_usuarios_cpf ON usuarios(cpf);"))
            connection.execute(text("CREATE INDEX ix_usuarios_id ON usuarios(id);"))
            
            connection.commit()
            print("✅ Migração executada com sucesso: empresa_id agora é opcional")
            
        except Exception as e:
            print(f"❌ Erro ao executar migração: {e}")
            connection.rollback()
            raise

if __name__ == "__main__":
    make_empresa_optional()
