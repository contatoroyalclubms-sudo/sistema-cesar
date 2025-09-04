"""
Script SQLite para corrigir a constraint NOT NULL na coluna evento_id
da tabela produtos usando recriação de tabela
"""
import os
import sys
sys.path.append(os.getcwd())
from app.database import get_db
from sqlalchemy import text

def fix_produtos_sqlite():
    """Corrigir evento_id para opcional via recriação de tabela SQLite"""
    db = next(get_db())
    
    try:
        print("🔧 Iniciando correção SQLite para tabela produtos...")
        
        # 1. Criar tabela temporária com estrutura correta
        sql_create_temp = """
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
            evento_id INTEGER,  -- ✅ SEM NOT NULL
            empresa_id INTEGER,
            criado_em DATETIME,
            atualizado_em DATETIME
        );
        """
        
        print("📝 Criando tabela temporária...")
        db.execute(text(sql_create_temp))
        
        # 2. Copiar dados existentes
        sql_copy_data = """
        INSERT INTO produtos_temp 
        SELECT * FROM produtos;
        """
        
        print("📋 Copiando dados existentes...")
        db.execute(text(sql_copy_data))
        
        # 3. Remover tabela original
        print("🗑️ Removendo tabela original...")
        db.execute(text("DROP TABLE produtos;"))
        
        # 4. Renomear tabela temporária
        print("🔄 Renomeando tabela temporária...")
        db.execute(text("ALTER TABLE produtos_temp RENAME TO produtos;"))
        
        # 5. Recriar índices (se necessário)
        sql_indexes = """
        CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome);
        CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo);
        CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);
        """
        
        print("🔍 Recriando índices...")
        db.execute(text(sql_indexes))
        
        db.commit()
        print("✅ Correção SQLite concluída! evento_id agora é opcional")
        
        # Verificar resultado
        result = db.execute(text("PRAGMA table_info(produtos);")).fetchall()
        evento_id_info = next((col for col in result if col[1] == 'evento_id'), None)
        if evento_id_info:
            not_null_status = "NOT NULL" if evento_id_info[3] == 1 else "NULL"
            print(f"🔍 Verificação: evento_id agora permite {not_null_status}")
        
    except Exception as e:
        print(f"❌ Erro ao executar correção SQLite: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = fix_produtos_sqlite()
    if success:
        print("\n🎉 Correção SQLite bem-sucedida! Produtos podem ser criados sem evento_id")
    else:
        print("\n💥 Falha na correção SQLite!")
