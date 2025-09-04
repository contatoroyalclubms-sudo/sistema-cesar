#!/usr/bin/env python3
"""
🔧 CORREÇÃO URGENTE: Migração tipo -> tipo_usuario
Corrigir inconsistência de schema entre bancos
"""

import sqlite3
import os
import shutil
from datetime import datetime

def create_backup(db_path):
    """Criar backup antes da migração"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path

def migrate_tipo_to_tipo_usuario(db_path):
    """Migrar coluna tipo para tipo_usuario"""
    print(f"\n🔧 Migrando {db_path}...")
    
    try:
        # Criar backup
        backup_path = create_backup(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura atual
        cursor.execute("PRAGMA table_info(usuarios);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        has_tipo = 'tipo' in column_names
        has_tipo_usuario = 'tipo_usuario' in column_names
        
        print(f"   📊 Estado atual: tipo={has_tipo}, tipo_usuario={has_tipo_usuario}")
        
        if has_tipo and not has_tipo_usuario:
            print("   🔄 Adicionando coluna tipo_usuario...")
            
            # Adicionar nova coluna
            cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo_usuario VARCHAR(20);")
            
            # Copiar dados de tipo para tipo_usuario
            cursor.execute("UPDATE usuarios SET tipo_usuario = tipo;")
            
            # Verificar se migração funcionou
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario IS NULL;")
            null_count = cursor.fetchone()[0]
            
            if null_count == 0:
                print("   ✅ Dados migrados com sucesso!")
                
                # Opcional: remover coluna antiga tipo (SQLite não suporta DROP COLUMN diretamente)
                # Por segurança, vamos manter ambas as colunas por enquanto
                print("   ℹ️ Mantendo coluna 'tipo' para compatibilidade")
                
                # Verificar alguns registros
                cursor.execute("SELECT id, nome, tipo, tipo_usuario FROM usuarios LIMIT 3;")
                users = cursor.fetchall()
                print("   👥 Verificação de dados:")
                for user in users:
                    print(f"      ID {user[0]}: {user[1]} | tipo='{user[2]}' | tipo_usuario='{user[3]}'")
                    
            else:
                print(f"   ❌ Erro: {null_count} registros com tipo_usuario NULL")
                
        elif has_tipo_usuario and not has_tipo:
            print("   ✅ Já tem tipo_usuario, adicionando tipo para compatibilidade...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo VARCHAR(8);")
            cursor.execute("UPDATE usuarios SET tipo = tipo_usuario;")
            
        elif has_tipo and has_tipo_usuario:
            print("   ✅ Já tem ambas as colunas!")
            
        else:
            print("   ❌ Nenhuma coluna de tipo encontrada!")
            
        conn.commit()
        conn.close()
        print(f"   ✅ Migração concluída para {db_path}")
        
    except Exception as e:
        print(f"   ❌ Erro na migração de {db_path}: {e}")
        # Restaurar backup em caso de erro
        if 'backup_path' in locals():
            shutil.copy2(backup_path, db_path)
            print(f"   🔄 Backup restaurado")

def main():
    """Executar migração em todos os bancos"""
    print("🚀 MIGRAÇÃO URGENTE: tipo -> tipo_usuario")
    print("=" * 50)
    
    databases = [
        "paineluniversal.db",
        "backend/eventos.db"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            migrate_tipo_to_tipo_usuario(db_path)
        else:
            print(f"❌ Banco não encontrado: {db_path}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("1. Testar login novamente")
    print("2. Verificar se backend retorna dados corretos")
    print("3. Confirmar frontend recebe usuário na resposta")

if __name__ == "__main__":
    main()
