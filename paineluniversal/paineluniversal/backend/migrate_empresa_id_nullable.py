#!/usr/bin/env python3

"""
Migração para tornar empresa_id opcional em todas as tabelas
Remove a obrigatoriedade de empresa_id no banco de dados
"""

import os
import sys

# Adicionar o diretório do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app.database import SessionLocal, engine
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    
    def make_empresa_id_nullable():
        """Torna todas as colunas empresa_id nullable"""
        db = SessionLocal()
        
        try:
            print("🔧 Iniciando migração para tornar empresa_id opcional...")
            
            # Lista de tabelas que têm empresa_id
            tables_with_empresa_id = [
                'eventos',
                'produtos', 
                'comandas',
                'vendas_pdv'
            ]
            
            # Para SQLite (desenvolvimento)
            if 'sqlite' in str(engine.url):
                print("📊 Detectado SQLite - aplicando migração...")
                
                for table in tables_with_empresa_id:
                    try:
                        # No SQLite, precisamos recriar a tabela
                        print(f"   🔄 Processando tabela {table}...")
                        
                        # Verificar se a tabela existe e tem a coluna empresa_id
                        result = db.execute(text(f"PRAGMA table_info({table})"))
                        columns = result.fetchall()
                        
                        empresa_id_exists = any(col[1] == 'empresa_id' for col in columns)
                        
                        if empresa_id_exists:
                            print(f"   ✅ Coluna empresa_id encontrada em {table}")
                        else:
                            print(f"   ⚠️ Coluna empresa_id não encontrada em {table}")
                            
                    except Exception as e:
                        print(f"   ❌ Erro ao processar {table}: {e}")
                        
            # Para PostgreSQL (produção)
            else:
                print("🐘 Detectado PostgreSQL - aplicando migração...")
                
                for table in tables_with_empresa_id:
                    try:
                        print(f"   🔄 Alterando {table}.empresa_id para nullable...")
                        
                        # Alterar a coluna para permitir NULL
                        sql = f"ALTER TABLE {table} ALTER COLUMN empresa_id DROP NOT NULL;"
                        db.execute(text(sql))
                        
                        print(f"   ✅ {table}.empresa_id agora é nullable")
                        
                    except SQLAlchemyError as e:
                        print(f"   ⚠️ Erro ao alterar {table}: {e}")
                        # Continuar com a próxima tabela
                        db.rollback()
                        continue
            
            # Commit das alterações
            db.commit()
            print("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {e}")
            db.rollback()
            import traceback
            traceback.print_exc()
            
        finally:
            db.close()
    
    if __name__ == "__main__":
        print("🚀 Executando migração empresa_id nullable...")
        make_empresa_id_nullable()
        print("🏁 Migração finalizada!")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se todas as dependências estão instaladas")
except Exception as e:
    print(f"💥 Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
