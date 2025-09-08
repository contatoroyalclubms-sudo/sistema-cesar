#!/usr/bin/env python3
"""
Migração para SQLite: Recrear tabela usuarios sem constraint NOT NULL em empresa_id
"""
from sqlalchemy import text
from app.database import engine

def recreate_usuarios_table():
    """Recria tabela usuarios permitindo empresa_id NULL"""
    
    try:
        print("Iniciando migracao da tabela usuarios...")
        
        with engine.begin() as conn:
            # 1. Criar tabela temporária com nova estrutura
            print("Criando tabela temporaria...")
            conn.execute(text("""
                CREATE TABLE usuarios_temp (
                    id INTEGER PRIMARY KEY,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    senha_hash VARCHAR(255) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    empresa_id INTEGER,
                    ultimo_login DATETIME,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME,
                    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
                )
            """))
            
            # 2. Copiar dados existentes
            print("Copiando dados existentes...")
            conn.execute(text("""
                INSERT INTO usuarios_temp (
                    id, cpf, nome, email, telefone, senha_hash, tipo, 
                    ativo, empresa_id, ultimo_login, criado_em, atualizado_em
                )
                SELECT 
                    id, cpf, nome, email, telefone, senha_hash, tipo, 
                    ativo, empresa_id, ultimo_login, criado_em, atualizado_em
                FROM usuarios
            """))
            
            # 3. Remover tabela original
            print("Removendo tabela original...")
            conn.execute(text("DROP TABLE usuarios"))
            
            # 4. Renomear tabela temporária
            print("Renomeando tabela temporaria...")
            conn.execute(text("ALTER TABLE usuarios_temp RENAME TO usuarios"))
            
            # 5. Recriar índices
            print("Recriando indices...")
            conn.execute(text("CREATE UNIQUE INDEX ix_usuarios_cpf ON usuarios (cpf)"))
            conn.execute(text("CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email)"))
            conn.execute(text("CREATE INDEX ix_usuarios_id ON usuarios (id)"))
            
        print("Migracao concluida com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a migracao: {e}")
        return False

if __name__ == "__main__":
    recreate_usuarios_table()