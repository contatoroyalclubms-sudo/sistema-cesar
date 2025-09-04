#!/usr/bin/env python3
"""
Script para remover a coluna empresa_id da tabela usuarios
"""
import sqlite3
import os

def remove_empresa_id_column():
    """Remove a coluna empresa_id da tabela usuarios"""
    
    db_path = 'eventos.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual da tabela usuarios...")
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        
        print("Colunas atuais:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar se a coluna empresa_id existe
        has_empresa_id = any(col[1] == 'empresa_id' for col in columns)
        
        if not has_empresa_id:
            print("✅ A coluna empresa_id já não existe na tabela usuarios")
            return True
        
        print("\n🔄 Removendo coluna empresa_id...")
        
        # 1. Criar nova tabela sem a coluna empresa_id
        cursor.execute('''
            CREATE TABLE usuarios_new (
                id INTEGER PRIMARY KEY,
                cpf VARCHAR(14) UNIQUE NOT NULL,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                senha_hash VARCHAR(255) NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                ultimo_login DATETIME,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Copiar dados (excluindo empresa_id)
        cursor.execute('''
            INSERT INTO usuarios_new (id, cpf, nome, email, telefone, senha_hash, tipo, ativo, ultimo_login, criado_em, atualizado_em)
            SELECT id, cpf, nome, email, telefone, senha_hash, tipo, ativo, ultimo_login, criado_em, atualizado_em
            FROM usuarios
        ''')
        
        # 3. Verificar se os dados foram copiados corretamente
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count_old = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios_new")
        count_new = cursor.fetchone()[0]
        
        if count_old != count_new:
            raise Exception(f"Erro na cópia: {count_old} registros originais, {count_new} registros copiados")
        
        # 4. Remover tabela antiga
        cursor.execute('DROP TABLE usuarios')
        
        # 5. Renomear nova tabela
        cursor.execute('ALTER TABLE usuarios_new RENAME TO usuarios')
        
        # 6. Verificar estrutura final
        cursor.execute("PRAGMA table_info(usuarios)")
        new_columns = cursor.fetchall()
        
        print("\n✅ Nova estrutura da tabela usuarios:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Commit das alterações
        conn.commit()
        print(f"\n🎉 Coluna empresa_id removida com sucesso!")
        print(f"📊 {count_new} registros preservados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover coluna empresa_id: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando remoção da coluna empresa_id da tabela usuarios...")
    success = remove_empresa_id_column()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou!")
