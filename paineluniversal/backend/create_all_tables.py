#!/usr/bin/env python3
"""
Script para criar todas as tabelas do banco de dados
"""
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(__file__))

def create_all_tables():
    print("🏗️ CRIANDO TABELAS DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Importar os modelos e o engine
        print("1️⃣ Importando modelos...")
        from app.models import Base
        from app.database import engine
        
        print("2️⃣ Criando todas as tabelas...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Todas as tabelas foram criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        print("\n3️⃣ Verificando tabelas criadas...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📋 {len(tables)} tabelas encontradas:")
        for table in sorted(tables):
            print(f"  ✅ {table}")
            
        # Verificar especificamente a tabela usuarios
        if 'usuarios' in tables:
            print("\n4️⃣ Verificando estrutura da tabela usuarios...")
            columns = inspector.get_columns('usuarios')
            print("📋 Colunas da tabela usuarios:")
            for col in columns:
                nullable = "nullable" if col['nullable'] else "not null"
                print(f"  - {col['name']} ({col['type']}) - {nullable}")
                
            # Verificar se tem empresa_id
            has_empresa_id = any(col['name'] == 'empresa_id' for col in columns)
            print(f"\n🏢 Tabela usuarios tem empresa_id? {has_empresa_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_all_tables()
    if success:
        print("\n🎉 Banco de dados configurado com sucesso!")
    else:
        print("\n❌ Erro na configuração do banco de dados!")
        sys.exit(1)
