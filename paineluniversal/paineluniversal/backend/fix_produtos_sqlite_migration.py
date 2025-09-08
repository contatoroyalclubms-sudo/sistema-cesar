"""
Migração SQLite para tornar evento_id nullable na tabela produtos
"""
import os
import sys
sys.path.append(os.getcwd())
from app.database import get_db
from sqlalchemy import text

def fix_produtos_evento_id_sqlite():
    """Tornar evento_id nullable na tabela produtos usando abordagem SQLite"""
    db = next(get_db())
    
    try:
        print("🔧 Iniciando migração SQLite para produtos.evento_id...")
        
        # 1. Criar nova tabela com evento_id nullable
        sql_create_new_table = """
        CREATE TABLE produtos_new (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            tipo VARCHAR(8) NOT NULL,
            preco NUMERIC(10, 2) NOT NULL,
            codigo_barras VARCHAR(50),
            codigo_interno VARCHAR(20),
            estoque_atual INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 0,
            estoque_maximo INTEGER DEFAULT 1000,
            controla_estoque BOOLEAN DEFAULT 1,
            status VARCHAR(8) DEFAULT 'ATIVO',
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
            evento_id INTEGER NULL,  -- ✅ AGORA É NULLABLE
            empresa_id INTEGER,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME,
            FOREIGN KEY (evento_id) REFERENCES eventos(id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );
        """
        
        print("📝 Criando nova tabela produtos_new...")
        db.execute(text(sql_create_new_table))
        
        # 2. Copiar dados da tabela antiga para nova (definindo evento_id como NULL se necessário)
        sql_copy_data = """
        INSERT INTO produtos_new (
            id, nome, descricao, tipo, preco, codigo_barras, codigo_interno,
            estoque_atual, estoque_minimo, estoque_maximo, controla_estoque,
            status, categoria, categoria_id, imagem_url, marca, fornecedor,
            preco_custo, margem_lucro, unidade_medida, volume, teor_alcoolico,
            temperatura_ideal, validade_dias, ncm, icms, ipi, destaque,
            promocional, observacoes, evento_id, empresa_id, criado_em, atualizado_em
        )
        SELECT 
            id, nome, descricao, tipo, preco, codigo_barras, codigo_interno,
            estoque_atual, estoque_minimo, estoque_maximo, controla_estoque,
            status, categoria, categoria_id, imagem_url, marca, fornecedor,
            preco_custo, margem_lucro, unidade_medida, volume, teor_alcoolico,
            temperatura_ideal, validade_dias, ncm, icms, ipi, destaque,
            promocional, observacoes, NULL as evento_id, empresa_id, criado_em, atualizado_em
        FROM produtos;
        """
        
        print("📦 Copiando dados para nova tabela (evento_id = NULL)...")
        db.execute(text(sql_copy_data))
        
        # 3. Renomear tabela antiga
        sql_rename_old = "ALTER TABLE produtos RENAME TO produtos_old;"
        print("🔄 Renomeando tabela antiga para produtos_old...")
        db.execute(text(sql_rename_old))
        
        # 4. Renomear nova tabela para produtos
        sql_rename_new = "ALTER TABLE produtos_new RENAME TO produtos;"
        print("🔄 Renomeando nova tabela para produtos...")
        db.execute(text(sql_rename_new))
        
        # 5. Recriar índices importantes
        sql_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome);",
            "CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo);",
            "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);",
            "CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);",
            "CREATE INDEX IF NOT EXISTS idx_produtos_evento_id ON produtos(evento_id);",
            "CREATE INDEX IF NOT EXISTS idx_produtos_empresa_id ON produtos(empresa_id);"
        ]
        
        print("🔗 Recriando índices...")
        for sql_index in sql_indexes:
            db.execute(text(sql_index))
        
        # 6. Confirmar alterações
        db.commit()
        
        print("✅ Migração concluída com sucesso!")
        
        # 7. Verificar a estrutura
        sql_check = """
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='produtos';
        """
        
        result = db.execute(text(sql_check)).fetchone()
        if result:
            print(f"🔍 Nova estrutura da tabela:")
            print(result[0])
        
        print("\n🎉 SUCESSO: evento_id agora é NULLABLE na tabela produtos!")
        print("📋 Produtos podem ser criados sem evento_id obrigatório")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {str(e)}")
        db.rollback()
        
        # Tentar limpar tabela temporária se existir
        try:
            db.execute(text("DROP TABLE IF EXISTS produtos_new;"))
            db.commit()
        except:
            pass
        
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = fix_produtos_evento_id_sqlite()
    if success:
        print("\n🚀 Migração bem-sucedida! Teste criar um produto agora.")
    else:
        print("\n💥 Falha na migração! Verifique os logs acima.")
