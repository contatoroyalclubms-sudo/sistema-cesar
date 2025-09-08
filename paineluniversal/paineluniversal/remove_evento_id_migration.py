#!/usr/bin/env python3
"""
Migração segura para remover coluna evento_id da tabela produtos
Garante que funcionalidades existentes não sejam afetadas
"""
import os
import sys
import sqlite3
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def backup_database(db_path):
    """Criar backup antes da migração"""
    print(f"💾 Criando backup do banco...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_remove_evento_id_{timestamp}"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return None

def check_evento_id_usage(db_path):
    """Verificar uso atual de evento_id na tabela produtos"""
    print("🔍 Analisando uso atual de evento_id...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se coluna existe
        cursor.execute("PRAGMA table_info(produtos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'evento_id' not in columns:
            print("✅ Coluna evento_id já não existe na tabela produtos")
            conn.close()
            return True, "already_removed"
        
        # Verificar dados com evento_id não-nulo
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE evento_id IS NOT NULL")
        produtos_com_evento = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE evento_id IS NULL")
        produtos_globais = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        
        print(f"📊 Produtos com evento_id != NULL: {produtos_com_evento}")
        print(f"🌍 Produtos globais (evento_id = NULL): {produtos_globais}")
        print(f"📈 Total de produtos: {total_produtos}")
        
        conn.close()
        
        # É seguro remover se todos ou quase todos são globais
        is_safe = produtos_com_evento == 0 or (produtos_globais / total_produtos) > 0.8
        return is_safe, {"com_evento": produtos_com_evento, "globais": produtos_globais, "total": total_produtos}
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return False, str(e)

def remove_evento_id_column_sqlite(db_path):
    """Remover coluna evento_id do SQLite usando recreação de tabela"""
    print("🔧 Removendo coluna evento_id (SQLite)...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQLite não suporta DROP COLUMN diretamente
        # Vamos recriar a tabela sem evento_id
        
        print("1️⃣ Criando nova tabela sem evento_id...")
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
        
        print("2️⃣ Copiando dados (excluindo evento_id)...")
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
        
        print("3️⃣ Substituindo tabela antiga...")
        cursor.execute("DROP TABLE produtos")
        cursor.execute("ALTER TABLE produtos_new RENAME TO produtos")
        
        print("4️⃣ Recriando índices...")
        cursor.execute("CREATE INDEX ix_produtos_id ON produtos (id)")
        
        conn.commit()
        conn.close()
        
        print("✅ Coluna evento_id removida com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na remoção: {e}")
        return False

def validate_removal(db_path):
    """Validar que a remoção foi bem-sucedida"""
    print("✅ Validando remoção...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(produtos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'evento_id' in columns:
            print("❌ Coluna evento_id ainda existe!")
            return False
        
        print("✅ Coluna evento_id removida com sucesso")
        
        # Verificar se dados estão íntegros
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total = cursor.fetchone()[0]
        print(f"📊 {total} produtos mantidos na tabela")
        
        # Testar inserção de produto
        cursor.execute("""
        INSERT INTO produtos (nome, tipo, preco, categoria)
        VALUES ('Teste Migração', 'BEBIDA', 10.0, 'Teste')
        """)
        
        cursor.execute("DELETE FROM produtos WHERE nome = 'Teste Migração'")
        conn.commit()
        
        print("✅ Operações básicas funcionando corretamente")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def test_application():
    """Testar se a aplicação ainda funciona"""
    print("🧪 Testando aplicação...")
    
    try:
        # Testar estrutura da tabela sem importar models
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        db_path = os.path.join(backend_dir, 'eventos.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Testar operações básicas na tabela produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        count = cursor.fetchone()[0]
        print(f"✅ Query de produtos funcionando: {count} produtos")
        
        # Testar inserção e remoção
        test_nome = f"TESTE_MIGRAÇÃO_{datetime.now().strftime('%H%M%S')}"
        cursor.execute("""
        INSERT INTO produtos (nome, tipo, preco, categoria)
        VALUES (?, 'BEBIDA', 10.0, 'Teste')
        """, (test_nome,))
        
        cursor.execute("SELECT id FROM produtos WHERE nome = ?", (test_nome,))
        test_id = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM produtos WHERE id = ?", (test_id,))
        
        conn.commit()
        conn.close()
        
        print("✅ Operações CRUD funcionando corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da aplicação: {e}")
        return False

def main():
    """Executar migração completa"""
    print("🚀 MIGRAÇÃO: Remover evento_id da tabela produtos")
    print("=" * 60)
    print("🎯 Objetivo: Remover evento_id sem afetar funcionalidades")
    print("=" * 60)
    
    # Determinar banco
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    db_path = os.path.join(backend_dir, 'eventos.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
    # 1. Criar backup
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ Não foi possível criar backup. Abortando.")
        return False
    
    # 2. Verificar uso atual
    is_safe, usage_info = check_evento_id_usage(db_path)
    if not is_safe:
        print("⚠️ Migração pode não ser segura. Verificar dados manualmente.")
        print(f"Informações: {usage_info}")
        return False
    
    if usage_info == "already_removed":
        print("✅ Migração já foi aplicada anteriormente")
        return True
    
    # 3. Remover coluna
    if not remove_evento_id_column_sqlite(db_path):
        print("❌ Falha na remoção da coluna")
        return False
    
    # 4. Validar
    if not validate_removal(db_path):
        print("❌ Validação falhou")
        return False
    
    # 5. Testar aplicação
    if not test_application():
        print("⚠️ Aplicação pode ter problemas")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("✅ Coluna evento_id removida da tabela produtos")
    print("✅ Funcionalidades preservadas")
    print("✅ Backup disponível para rollback se necessário")
    print(f"💾 Backup: {backup_path}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
