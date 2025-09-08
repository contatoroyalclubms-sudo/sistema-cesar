#!/usr/bin/env python3
"""
Migração final de produtos com mapeamento correto de colunas
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def migrate_produtos_final():
    """Migra produtos com mapeamento correto de colunas"""
    print("📦 MIGRAÇÃO FINAL - PRODUTOS")
    print("=" * 40)
    
    try:
        import psycopg2
        
        # Conectar bancos
        sqlite_conn = sqlite3.connect("paineluniversal.db")
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        pg_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        pg_cursor = pg_conn.cursor()
        
        # Obter produtos do SQLite
        sqlite_cursor.execute("SELECT * FROM produtos")
        produtos = sqlite_cursor.fetchall()
        
        print(f"📊 {len(produtos)} produtos para migrar")
        
        migrated = 0
        
        for produto in produtos:
            try:
                # Mapear colunas SQLite → PostgreSQL
                data = {
                    'id': produto['id'],
                    'nome': produto['nome'],
                    'descricao': produto['descricao'],
                    'tipo_usuario': produto['tipo'] or 'cliente',  # Mapear 'tipo' → 'tipo_usuario'
                    'preco': produto['preco'],
                    'codigo_interno': produto['codigo_interno'],
                    'estoque_atual': produto['estoque_atual'],
                    'estoque_minimo': produto['estoque_minimo'],
                    'estoque_maximo': produto['estoque_maximo'],
                    'controla_estoque': bool(produto['controla_estoque']),
                    'status': produto['status'],
                    'categoria': produto['categoria'],
                    'imagem_url': produto['imagem_url'],
                    'empresa_id': produto['empresa_id'],
                    'criado_em': produto['criado_em'],
                    'atualizado_em': produto['atualizado_em']
                    # Não incluir evento_id pois foi removido no PostgreSQL
                }
                
                # Limpar valores None problemáticos
                if data['tipo_usuario'] is None:
                    data['tipo_usuario'] = 'cliente'
                
                # Inserir no PostgreSQL
                columns = list(data.keys())
                values = list(data.values())
                placeholders = ', '.join(['%s'] * len(values))
                
                insert_sql = f"""
                    INSERT INTO produtos ({', '.join(columns)}) 
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO UPDATE SET
                    {', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col != 'id'])}
                """
                
                pg_cursor.execute(insert_sql, values)
                migrated += 1
                print(f"  ✅ Produto: {data['nome']}")
                
            except Exception as e:
                print(f"  ❌ Erro no produto {produto['nome']}: {e}")
                continue
        
        pg_conn.commit()
        
        # Verificação
        pg_cursor.execute("SELECT COUNT(*) FROM produtos")
        total = pg_cursor.fetchone()[0]
        
        print(f"\n🎉 {migrated} produtos migrados")
        print(f"📊 Total no PostgreSQL: {total}")
        
        sqlite_conn.close()
        pg_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    migrate_produtos_final()
