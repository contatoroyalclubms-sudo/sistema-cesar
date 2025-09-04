"""
Correção definitiva para o problema de evento_id NOT NULL
Executa statements SQLite individuais para recriar tabela produtos
"""
import os
import sys
import sqlite3

def fix_produtos_constraint():
    """Corrigir constraint NOT NULL de evento_id executando SQLite diretamente"""
    
    # Caminho do banco de dados
    db_path = os.path.join(os.getcwd(), 'app.db')
    
    try:
        print("🔧 Conectando ao SQLite diretamente...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📝 Executando correção step-by-step...")
        
        # 1. Criar tabela temporária
        print("   Step 1: Criando tabela temporária...")
        cursor.execute("""
        CREATE TABLE produtos_temp (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            tipo VARCHAR(8) NOT NULL,
            preco NUMERIC(10, 2) NOT NULL,
            codigo_barras VARCHAR(50),
            codigo_interno VARCHAR(20),
            estoque_atual INTEGER,
            estoque_minimo INTEGER,
            estoque_maximo INTEGER,
            controla_estoque BOOLEAN,
            status VARCHAR(8),
            categoria VARCHAR(100),
            categoria_id INTEGER,
            imagem_url VARCHAR(500),
            marca VARCHAR(100),
            fornecedor VARCHAR(200),
            preco_custo NUMERIC(10, 2),
            margem_lucro NUMERIC(5, 2),
            unidade_medida VARCHAR(10),
            volume NUMERIC(8, 2),
            teor_alcoolico NUMERIC(4, 2),
            temperatura_ideal VARCHAR(20),
            validade_dias INTEGER,
            ncm VARCHAR(8),
            icms NUMERIC(5, 2),
            ipi NUMERIC(5, 2),
            destaque BOOLEAN,
            promocional BOOLEAN,
            observacoes TEXT,
            evento_id INTEGER,
            empresa_id INTEGER,
            criado_em DATETIME,
            atualizado_em DATETIME
        )
        """)
        
        # 2. Copiar dados
        print("   Step 2: Copiando dados...")
        cursor.execute("INSERT INTO produtos_temp SELECT * FROM produtos")
        
        # 3. Remover tabela original
        print("   Step 3: Removendo tabela original...")
        cursor.execute("DROP TABLE produtos")
        
        # 4. Renomear tabela
        print("   Step 4: Renomeando tabela...")
        cursor.execute("ALTER TABLE produtos_temp RENAME TO produtos")
        
        # 5. Criar índices
        print("   Step 5: Criando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)")
        
        # Commit
        conn.commit()
        print("✅ Correção concluída com sucesso!")
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(produtos)")
        columns = cursor.fetchall()
        evento_id_col = next((col for col in columns if col[1] == 'evento_id'), None)
        
        if evento_id_col:
            not_null = "NOT NULL" if evento_id_col[3] == 1 else "NULL"
            print(f"🔍 evento_id agora permite: {not_null}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na correção: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = fix_produtos_constraint()
    if success:
        print("\n🎉 Banco corrigido! Testando criação de produto...")
        
        # Testar novamente
        sys.path.append(os.getcwd())
        from test_produto_creation import test_produto_creation
        
        if test_produto_creation():
            print("🎊 SUCESSO TOTAL! Produtos podem ser cadastrados sem evento_id")
        else:
            print("⚠️ Banco corrigido mas ainda há outros problemas")
    else:
        print("\n💥 Falha na correção do banco")
