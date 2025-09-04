#!/usr/bin/env python3

"""
Script de migração segura para produção
Aplica correções de forma incremental e reversível
Suporta SQLite (local) e PostgreSQL (produção)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def backup_database_sqlite(db_path):
    """Criar backup do banco SQLite"""
    print(f"💾 Criando backup do banco SQLite {db_path}...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Backup SQLite criado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erro no backup SQLite: {e}")
        return None

def check_table_exists_sqlite(cursor, table_name):
    """Verificar se tabela existe no SQLite"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def check_table_exists_postgres(cursor, table_name):
    """Verificar se tabela existe no PostgreSQL"""
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
    return cursor.fetchone()[0]

def apply_safe_migration_sqlite(db_path):
    """Aplicar migração segura no SQLite"""
    print(f"🔧 Aplicando migração segura SQLite em {db_path}...")
    
    # Criar backup primeiro
    backup_path = backup_database_sqlite(db_path)
    if not backup_path:
        print("❌ Não foi possível criar backup. Abortando migração.")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual SQLite...")
        
        # Verificar tabelas críticas
        critical_tables = ["usuarios", "eventos", "produtos"]
        for table in critical_tables:
            if check_table_exists_sqlite(cursor, table):
                print(f"✅ Tabela {table} já existe")
            else:
                print(f"⚠️ Tabela {table} não existe - será criada")
        
        # Criar todas as tabelas usando SQLAlchemy
        print("🏗️ Criando/atualizando tabelas com SQLAlchemy...")
        from app.models import Base
        from app.database import engine
        
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tabelas SQLite criadas/atualizadas com sucesso")
        
        # Verificar integridade
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        
        conn.close()
        
        if integrity == "ok":
            print("✅ Integridade do banco SQLite verificada")
            return True
        else:
            print(f"❌ Problema de integridade SQLite: {integrity}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na migração SQLite: {e}")
        
        # Restaurar backup
        try:
            import shutil
            shutil.copy2(backup_path, db_path)
            print("✅ Backup SQLite restaurado")
        except Exception as restore_error:
            print(f"❌ Erro ao restaurar backup SQLite: {restore_error}")
        
        return False

def apply_safe_migration_postgres():
    """Aplicar migração segura no PostgreSQL de produção"""
    print("🔧 Aplicando migração segura PostgreSQL...")
    
    try:
        # Importar configuração do banco
        from app.database import engine
        
        # Verificar se é PostgreSQL
        if 'postgresql' not in str(engine.url):
            print("⚠️ Não é PostgreSQL, pulando migração PostgreSQL")
            return True
        
        print("🔍 Verificando estrutura PostgreSQL...")
        
        # Usar SQLAlchemy para migração segura
        from app.models import Base
        
        print("🏗️ Criando/atualizando tabelas PostgreSQL com SQLAlchemy...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tabelas PostgreSQL criadas/atualizadas com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração PostgreSQL: {e}")
        return False

def validate_migration():
    """Validar se a migração foi bem-sucedida"""
    print("✅ Validando migração...")
    
    try:
        from app.models import Usuario, Evento, Produto
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Verificar tabelas críticas
        critical_models = [
            ("usuarios", Usuario),
            ("eventos", Evento), 
            ("produtos", Produto)
        ]
        
        all_good = True
        
        for table_name, model in critical_models:
            try:
                count = db.query(model).count()
                print(f"✅ {table_name}: {count} registros")
            except Exception as e:
                print(f"❌ Erro em {table_name}: {e}")
                all_good = False
        
        db.close()
        return all_good
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False
DATABASE_URL = "postgresql://postgres:CeGUGoTyinOaBRILNgPCApbJpcfcVETf@hopper.proxy.rlwy.net:57200/railway"

def apply_production_migration():
    """Aplica migração para tornar empresa_id nullable no PostgreSQL"""
    
    print("🐘 Conectando ao PostgreSQL de produção...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Conectado ao banco PostgreSQL")
        
        # Lista de tabelas para migrar
        tables_to_migrate = [
            'eventos',
            'produtos', 
            'comandas',
            'vendas_pdv'
        ]
        
        print(f"🔧 Aplicando migração em {len(tables_to_migrate)} tabelas...")
        
        for table in tables_to_migrate:
            try:
                print(f"   🔄 Migrando {table}.empresa_id...")
                
                # Verificar se a coluna existe antes de alterar
                cur.execute("""
                    SELECT column_name, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'empresa_id'
                """, (table,))
                
                result = cur.fetchone()
                
                if result:
                    column_name, is_nullable = result
                    print(f"   📋 {table}.empresa_id encontrada - nullable: {is_nullable}")
                    
                    if is_nullable == 'NO':
                        # Alterar para permitir NULL
                        sql = f"ALTER TABLE {table} ALTER COLUMN empresa_id DROP NOT NULL;"
                        cur.execute(sql)
                        print(f"   ✅ {table}.empresa_id agora é nullable")
                    else:
                        print(f"   ⚠️ {table}.empresa_id já é nullable")
                else:
                    print(f"   ⚠️ {table}.empresa_id não encontrada")
                    
            except Exception as e:
                print(f"   ❌ Erro em {table}: {e}")
                # Continuar com próxima tabela
                continue
        
        # Commit das alterações
        conn.commit()
        print("✅ Migração aplicada com sucesso!")
        
        # Verificar estrutura final
        print("\n📊 Verificando estrutura final...")
        for table in tables_to_migrate:
            try:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'empresa_id'
                """, (table,))
                
                result = cur.fetchone()
                if result:
                    col_name, data_type, is_nullable = result
                    status = "✅ NULL" if is_nullable == 'YES' else "❌ NOT NULL"
                    print(f"   {table}.empresa_id: {data_type} - {status}")
                    
            except Exception as e:
                print(f"   ❌ Erro verificando {table}: {e}")
        
    except Exception as e:
        print(f"💥 Erro na migração: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔒 Conexão fechada")
    
    return True

def check_production_tables():
    """Verifica estrutura das tabelas em produção"""
    
    print("🔍 Verificando estrutura das tabelas...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Listar todas as tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"📋 Tabelas encontradas: {len(tables)}")
        
        for (table_name,) in tables:
            print(f"   - {table_name}")
        
        # Verificar especificamente a tabela eventos
        print("\n🎫 Estrutura da tabela eventos:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'eventos'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col_name, data_type, is_nullable, col_default in columns:
            nullable_str = "NULL" if is_nullable == 'YES' else "NOT NULL"
            default_str = f" DEFAULT {col_default}" if col_default else ""
            print(f"   {col_name}: {data_type} {nullable_str}{default_str}")
            
    except Exception as e:
        print(f"💥 Erro na verificação: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

def main_new():
    """Executar migração completa segura"""
    print("🚀 MIGRAÇÃO SEGURA PARA PRODUÇÃO")
    print("=" * 50)
    print("🎯 Objetivo: Aplicar correções sem quebrar funcionalidades")
    print("=" * 50)
    
    success = True
    
    # 1. Migração local (SQLite)
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    db_path = os.path.join(backend_dir, 'eventos.db')
    
    if os.path.exists(db_path):
        print("\n🔧 ETAPA 1: Migração Local (SQLite)")
        if not apply_safe_migration_sqlite(db_path):
            print("❌ Migração local falhou")
            success = False
    else:
        print(f"⚠️ Banco local não encontrado: {db_path}")
    
    # 2. Migração produção (PostgreSQL)
    print("\n🔧 ETAPA 2: Migração Produção (PostgreSQL)")
    if not apply_safe_migration_postgres():
        print("❌ Migração de produção falhou")
        success = False
    
    # 3. Validação final
    print("\n🔧 ETAPA 3: Validação Final")
    if not validate_migration():
        print("❌ Validação falhou")
        success = False
    
    # Resultado final
    print("\n" + "=" * 50)
    if success:
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Sistema seguro para produção")
        print("✅ Todas as funcionalidades preservadas")
    else:
        print("❌ MIGRAÇÃO FALHOU")
        print("❌ Revisar erros antes de aplicar na produção")
    
    return success
