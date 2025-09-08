print("Migração iniciada")
import sqlite3
print("SQLite importado")

conn = sqlite3.connect("backend/eventos.db")
print("Conectado ao banco")

cursor = conn.cursor()
cursor.execute("PRAGMA table_info(produtos)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Colunas atuais: {columns}")

if 'evento_id' in columns:
    print("Evento_id encontrado, removendo...")
    
    # Remover tabela temporária se existir
    cursor.execute("DROP TABLE IF EXISTS produtos_temp")
    
    # Criar nova tabela
    cursor.execute("""
    CREATE TABLE produtos_temp (
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
        atualizado_em DATETIME
    )
    """)
    
    # Copiar dados (sem evento_id)
    cursor.execute("""
    INSERT INTO produtos_temp SELECT 
        id, nome, descricao, tipo, preco, codigo_interno,
        estoque_atual, estoque_minimo, estoque_maximo, controla_estoque,
        status, categoria, imagem_url, empresa_id, criado_em, atualizado_em
    FROM produtos
    """)
    
    # Substituir
    cursor.execute("DROP TABLE produtos")
    cursor.execute("ALTER TABLE produtos_temp RENAME TO produtos")
    
    conn.commit()
    print("Tabela recriada sem evento_id")
else:
    print("Evento_id já foi removido")

conn.close()
print("Migração concluída")
