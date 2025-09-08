#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO: Schema do Banco de Dados
Verificar estrutura real das tabelas vs modelos do código
"""

import sqlite3
import os
import sys

# Adicionar caminho do backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def diagnose_database_schema():
    """Diagnosticar estrutura atual do banco"""
    print("🔍 DIAGNÓSTICO DO SCHEMA DO BANCO DE DADOS")
    print("=" * 60)
    
    db_paths = [
        "paineluniversal.db",
        "backend/paineluniversal.db", 
        "eventos.db",
        "backend/eventos.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n📁 Banco encontrado: {db_path}")
            analyze_database(db_path)
        else:
            print(f"\n❌ Banco não encontrado: {db_path}")

def analyze_database(db_path):
    """Analisar estrutura de um banco específico"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"   📋 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"      • {table[0]}")
        
        # Verificar especificamente a tabela usuarios
        if any('usuarios' in str(table) for table in tables):
            print(f"\n   👤 ESTRUTURA DA TABELA USUARIOS:")
            cursor.execute("PRAGMA table_info(usuarios);")
            columns = cursor.fetchall()
            
            print(f"      📊 Colunas ({len(columns)}):")
            for col in columns:
                col_id, name, type_info, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                primary = " (PRIMARY KEY)" if pk else ""
                default_val = f" DEFAULT {default}" if default else ""
                print(f"         {col_id}: {name} | {type_info} | {nullable}{default_val}{primary}")
            
            # Verificar se campo tipo_usuario existe
            column_names = [col[1] for col in columns]
            has_tipo_usuario = 'tipo_usuario' in column_names
            has_tipo = 'tipo' in column_names
            
            print(f"\n   🔍 VERIFICAÇÃO DE CAMPOS:")
            print(f"      tipo_usuario: {'✅' if has_tipo_usuario else '❌'}")
            print(f"      tipo: {'✅' if has_tipo else '❌'}")
            
            if not has_tipo_usuario and not has_tipo:
                print(f"      ⚠️ PROBLEMA: Nenhum campo de tipo encontrado!")
                # Procurar por campos similares
                tipo_fields = [col for col in column_names if 'tipo' in col.lower()]
                if tipo_fields:
                    print(f"      🔍 Campos similares: {tipo_fields}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            count = cursor.fetchone()[0]
            print(f"      📊 Registros na tabela: {count}")
            
            if count > 0:
                # Mostrar alguns registros (sem senhas)
                safe_columns = [col for col in column_names if 'senha' not in col.lower() and 'password' not in col.lower()]
                safe_columns_str = ', '.join(safe_columns)
                cursor.execute(f"SELECT {safe_columns_str} FROM usuarios LIMIT 3;")
                users = cursor.fetchall()
                
                print(f"      👥 Alguns usuários:")
                for user in users:
                    user_data = dict(zip(safe_columns, user))
                    print(f"         ID {user_data.get('id', 'N/A')}: {user_data.get('nome', 'N/A')} ({user_data.get('cpf', 'N/A')})")
                    if 'tipo_usuario' in user_data:
                        print(f"            Tipo: {user_data['tipo_usuario']}")
                    elif 'tipo' in user_data:
                        print(f"            Tipo: {user_data['tipo']}")
        else:
            print(f"   ❌ Tabela 'usuarios' não encontrada!")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao analisar {db_path}: {e}")

def check_models_vs_database():
    """Comparar modelos do código com banco real"""
    print(f"\n🔍 COMPARAÇÃO: MODELOS vs BANCO")
    print("=" * 40)
    
    try:
        # Importar modelos do backend
        from app.models import Usuario
        from sqlalchemy import inspect
        
        print(f"📝 MODELO USUARIO (código):")
        # Obter colunas definidas no modelo
        mapper = inspect(Usuario)
        for column in mapper.columns:
            print(f"   • {column.name}: {column.type}")
            
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}")

def suggest_migration():
    """Sugerir comando de migração"""
    print(f"\n🔧 SUGESTÕES DE CORREÇÃO:")
    print("=" * 30)
    print("1. Se a coluna tipo_usuario não existe:")
    print("   ALTER TABLE usuarios ADD COLUMN tipo_usuario VARCHAR(20) DEFAULT 'cliente';")
    print("")
    print("2. Se existe coluna 'tipo' mas não 'tipo_usuario':")
    print("   ALTER TABLE usuarios ADD COLUMN tipo_usuario VARCHAR(20);")
    print("   UPDATE usuarios SET tipo_usuario = tipo;")
    print("")
    print("3. Recriar a tabela com schema correto:")
    print("   - Fazer backup dos dados")
    print("   - Recriar tabela com schema atualizado")
    print("   - Restaurar dados")

if __name__ == "__main__":
    diagnose_database_schema()
    check_models_vs_database()
    suggest_migration()
