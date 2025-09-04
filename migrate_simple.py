import os
import sqlite3
import shutil
from datetime import datetime

def main():
    print("🚀 Removendo coluna evento_id da tabela produtos")
    
    # Localizar banco
    db_path = "backend/eventos.db"
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backend/eventos.db.backup_remove_evento_id_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    
    # Conectar banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se coluna existe
    cursor.execute("PRAGMA table_info(produtos)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'evento_id' not in columns:
        print("✅ Coluna evento_id já não existe")
        conn.close()
        return
    
    print("🔧 Removendo coluna evento_id...")
    
    # Criar nova tabela sem evento_id
    cursor.execute("""
    CREATE TABLE produtos_new (
        id INTEGER PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        descricao TEXT,
        tipo VARCHAR(50) NOT NULL,
        preco DECIMAL(10,2) NOT NULL,
        codigo_interno VARCHAR(20),
        estoque_atual INTEGER DEFAULT 0,
        estoque_minimo INTEGER DEFAULT 0,
        estoque_maximo INTEGER DEFAULT 1000,
        controla_estoque BOOLEAN DEFAULT 1,
        status VARCHAR(50) DEFAULT 'ATIVO',
        categoria VARCHAR(100),
        imagem_url VARCHAR(500),
        empresa_id INTEGER,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        atualizado_em DATETIME,
        FOREIGN KEY (empresa_id) REFERENCES empresas (id)
    )
    """)
    
    # Copiar dados
    cursor.execute("""
    INSERT INTO produtos_new (
        id, nome, descricao, tipo, preco, codigo_interno,
        estoque_atual, estoque_minimo, estoque_maximo, controla_estoque,
        status, categoria, imagem_url, empresa_id, criado_em, atualizado_em
    )
    SELECT 
        id, nome, descricao, tipo, preco, codigo_interno,
        estoque_atual, estoque_minimo, estoque_maximo, controla_estoque,
        status, categoria, imagem_url, empresa_id, criado_em, atualizado_em
    FROM produtos
    """)
    
    # Substituir tabela
    cursor.execute("DROP TABLE produtos")
    cursor.execute("ALTER TABLE produtos_new RENAME TO produtos")
    
    # Criar índice
    cursor.execute("CREATE INDEX ix_produtos_id ON produtos (id)")
    
    conn.commit()
    
    # Validar
    cursor.execute("PRAGMA table_info(produtos)")
    new_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM produtos")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    if 'evento_id' not in new_columns:
        print("✅ Coluna evento_id removida com sucesso!")
        print(f"✅ {count} produtos mantidos na tabela")
    else:
        print("❌ Erro: coluna ainda existe")
    
    print(f"💾 Backup disponível: {backup_path}")

if __name__ == "__main__":
    main()
