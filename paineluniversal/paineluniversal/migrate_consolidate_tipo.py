#!/usr/bin/env python3
"""
Migração para consolidar campos tipo e tipo_usuario
Remove redundância e corrige inconsistências de dados

FASE 1: Sincronizar dados (tipo_usuario = tipo)
FASE 2: Preparar remoção de tipo_usuario (futuro)
"""

import os
import sys
import sqlite3
import time
from datetime import datetime

# Adicionar backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.app.database import get_db, settings
    from backend.app.models import Usuario
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("⚠️ SQLAlchemy não disponível, usando apenas SQLite direto")

def migrate_sqlite_direct():
    """Migração direta no SQLite local"""
    print("\n🔧 MIGRAÇÃO SQLITE LOCAL")
    print("=" * 40)
    
    try:
        # Conectar ao banco SQLite
        db_path = "paineluniversal.db"
        if not os.path.exists(db_path):
            print(f"❌ Banco SQLite não encontrado: {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estado atual
        print("📋 Estado antes da migração:")
        cursor.execute("""
            SELECT id, cpf, nome, tipo, tipo_usuario 
            FROM usuarios 
            ORDER BY id
        """)
        
        usuarios = cursor.fetchall()
        inconsistencias = 0
        
        for user in usuarios:
            user_id, cpf, nome, tipo, tipo_usuario = user
            print(f"  ID {user_id}: {nome[:20]} - tipo='{tipo}' tipo_usuario='{tipo_usuario}'")
            if tipo and tipo_usuario and tipo.lower() != tipo_usuario.lower():
                inconsistencias += 1
        
        print(f"\n🔍 Encontradas {inconsistencias} inconsistências")
        
        if inconsistencias == 0:
            print("✅ Nenhuma correção necessária no SQLite")
            return True
        
        # Corrigir inconsistências - priorizar campo 'tipo'
        print("\n🔄 Corrigindo inconsistências...")
        cursor.execute("""
            UPDATE usuarios 
            SET tipo_usuario = LOWER(tipo)
            WHERE tipo IS NOT NULL 
            AND tipo != ''
            AND (tipo_usuario IS NULL 
                 OR tipo_usuario = '' 
                 OR LOWER(tipo) != LOWER(tipo_usuario))
        """)
        
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros atualizados")
        
        # Verificar resultado
        print("\n📋 Estado após migração:")
        cursor.execute("""
            SELECT id, cpf, nome, tipo, tipo_usuario 
            FROM usuarios 
            ORDER BY id
        """)
        
        usuarios_updated = cursor.fetchall()
        for user in usuarios_updated:
            user_id, cpf, nome, tipo, tipo_usuario = user
            print(f"  ID {user_id}: {nome[:20]} - tipo='{tipo}' tipo_usuario='{tipo_usuario}'")
        
        conn.commit()
        conn.close()
        print("✅ Migração SQLite concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração SQLite: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def migrate_sqlalchemy():
    """Migração usando SQLAlchemy (funciona com PostgreSQL e SQLite)"""
    print("\n🔧 MIGRAÇÃO SQLALCHEMY")
    print("=" * 40)
    
    if not SQLALCHEMY_AVAILABLE:
        print("❌ SQLAlchemy não disponível")
        return False
    
    try:
        db = next(get_db())
        
        # Verificar estado atual
        print("📋 Estado antes da migração:")
        usuarios = db.query(Usuario).order_by(Usuario.id).all()
        
        inconsistencias = 0
        for usuario in usuarios:
            print(f"  ID {usuario.id}: {usuario.nome[:20]} - tipo='{usuario.tipo}' tipo_usuario='{usuario.tipo_usuario}'")
            if (usuario.tipo and usuario.tipo_usuario and 
                usuario.tipo.lower() != usuario.tipo_usuario.lower()):
                inconsistencias += 1
        
        print(f"\n🔍 Encontradas {inconsistencias} inconsistências")
        
        if inconsistencias == 0:
            print("✅ Nenhuma correção necessária via SQLAlchemy")
            db.close()
            return True
        
        # Corrigir inconsistências
        print("\n🔄 Corrigindo inconsistências...")
        
        # Usar SQL direto para máxima compatibilidade
        if 'postgresql' in settings.database_url.lower():
            # PostgreSQL
            result = db.execute(text("""
                UPDATE usuarios 
                SET tipo_usuario = LOWER(tipo)
                WHERE tipo IS NOT NULL 
                AND tipo != ''
                AND (tipo_usuario IS NULL 
                     OR tipo_usuario = '' 
                     OR LOWER(tipo) != LOWER(tipo_usuario))
            """))
        else:
            # SQLite
            result = db.execute(text("""
                UPDATE usuarios 
                SET tipo_usuario = LOWER(tipo)
                WHERE tipo IS NOT NULL 
                AND tipo != ''
                AND (tipo_usuario IS NULL 
                     OR tipo_usuario = '' 
                     OR LOWER(tipo) != LOWER(tipo_usuario))
            """))
        
        rows_updated = result.rowcount
        print(f"✅ {rows_updated} registros atualizados")
        
        db.commit()
        
        # Verificar resultado
        print("\n📋 Estado após migração:")
        usuarios_updated = db.query(Usuario).order_by(Usuario.id).all()
        for usuario in usuarios_updated:
            print(f"  ID {usuario.id}: {usuario.nome[:20]} - tipo='{usuario.tipo}' tipo_usuario='{usuario.tipo_usuario}'")
        
        db.close()
        print("✅ Migração SQLAlchemy concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração SQLAlchemy: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def main():
    """Executar migração completa"""
    print("🚀 MIGRAÇÃO DE CONSOLIDAÇÃO DE CAMPOS TIPO")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    
    # Tentar migração SQLite direta primeiro
    if migrate_sqlite_direct():
        success_count += 1
    
    # Tentar migração SQLAlchemy (PostgreSQL/SQLite)
    if migrate_sqlalchemy():
        success_count += 1
    
    print(f"\n{'='*50}")
    if success_count > 0:
        print("🎉 Migração concluída com sucesso!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Testar login de usuários admin")
        print("2. Verificar permissões no sistema")
        print("3. Deploy das alterações de código")
        print("4. Monitorar sistema por inconsistências")
    else:
        print("❌ Falha na migração")
        print("\n💡 AÇÕES RECOMENDADAS:")
        print("1. Verificar conexões de banco")
        print("2. Executar migração manual se necessário")
        print("3. Contatar suporte técnico")
    
    return success_count > 0

if __name__ == "__main__":
    main()
