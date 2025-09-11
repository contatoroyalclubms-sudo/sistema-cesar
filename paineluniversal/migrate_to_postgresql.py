#!/usr/bin/env python3
"""
Migração completa para PostgreSQL
Cria todas as tabelas necessárias baseado nos models
"""
import os
import sys
from dotenv import load_dotenv

# Adicionar backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Carregar variáveis de ambiente
load_dotenv()

def create_all_tables():
    """Cria todas as tabelas no PostgreSQL"""
    print("🚀 MIGRAÇÃO POSTGRESQL - CRIAÇÃO DE TABELAS")
    print("=" * 60)
    
    try:
        # Importar após carregar variáveis de ambiente
        from backend.app.database import engine, Base
        from backend.app import models  # Isso carrega todos os models
        
        print("📊 Models carregados:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        # Verificar conexão
        print(f"\n🔗 Conectando ao banco: {os.getenv('DATABASE_URL')}")
        
        # Criar todas as tabelas
        print("\n🔨 Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        
        # Verificar tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Tabelas criadas ({len(tables)}):")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        print("\n🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verifica se as tabelas foram criadas corretamente"""
    print("\n🔍 VERIFICAÇÃO DE TABELAS")
    print("=" * 40)
    
    try:
        from sqlalchemy import create_engine, text
        
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Listar tabelas
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """))
            
            tables = [row[0] for row in result]
            print(f"Tabelas encontradas: {len(tables)}")
            
            for table in tables:
                # Contar registros
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                count = count_result.fetchone()[0]
                print(f"  📋 {table}: {count} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Iniciando migração PostgreSQL...")
    
    success = create_all_tables()
    if success:
        verify_tables()
        print("\n✅ Migração PostgreSQL concluída!")
        sys.exit(0)
    else:
        print("\n❌ Migração falhou!")
        sys.exit(1)
