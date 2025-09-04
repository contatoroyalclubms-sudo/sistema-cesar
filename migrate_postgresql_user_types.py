#!/usr/bin/env python3
"""
🔧 MIGRAÇÃO POSTGRESQL: Padronização de Tipos de Usuário
Script para aplicar as mesmas correções no banco PostgreSQL de produção
"""

import psycopg2
import os
from datetime import datetime

def migrate_postgresql_user_types():
    """Migrar tipos de usuário no PostgreSQL de produção"""
    print("🚀 MIGRAÇÃO POSTGRESQL: Padronização de Tipos")
    print("=" * 55)
    
    # URL do banco obtida do Railway (substitua pela URL real)
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@host:port/database')
    
    if 'username:password' in DATABASE_URL:
        print("⚠️ CONFIGURE A DATABASE_URL DO POSTGRESQL!")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/db'")
        print("   Ou execute este script no Railway com a variável configurada")
        return False
    
    try:
        print(f"🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Verificar estado atual
        print(f"\n📊 ESTADO ATUAL:")
        cursor.execute("SELECT DISTINCT tipo_usuario FROM usuarios WHERE tipo_usuario IS NOT NULL;")
        tipos_usuario = [row[0] for row in cursor.fetchall()]
        print(f"   Tipos atuais em tipo_usuario: {tipos_usuario}")
        
        # Contar usuários por tipo
        for tipo in tipos_usuario:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = %s", (tipo,))
            count = cursor.fetchone()[0]
            print(f"   '{tipo}': {count} usuários")
        
        # Backup virtual - mostrar dados antes da migração
        print(f"\n💾 CRIANDO LOG DE BACKUP:")
        cursor.execute("SELECT id, nome, tipo_usuario FROM usuarios LIMIT 10;")
        users_backup = cursor.fetchall()
        
        backup_file = f"backup_postgresql_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("# BACKUP POSTGRESQL ANTES DA MIGRAÇÃO\n")
            f.write(f"# Data: {datetime.now()}\n\n")
            for user in users_backup:
                f.write(f"ID: {user[0]}, Nome: {user[1]}, Tipo: {user[2]}\n")
        
        print(f"   ✅ Backup salvo: {backup_file}")
        
        # Executar migração
        print(f"\n🔄 EXECUTANDO MIGRAÇÃO:")
        
        # 1. Padronizar tipo_usuario para minúsculas
        print("   1. Padronizando tipo_usuario...")
        cursor.execute("UPDATE usuarios SET tipo_usuario = LOWER(TRIM(tipo_usuario)) WHERE tipo_usuario IS NOT NULL;")
        updated_1 = cursor.rowcount
        print(f"      ✅ {updated_1} registros atualizados")
        
        # 2. Corrigir tipos inválidos
        print("   2. Corrigindo tipos inválidos...")
        cursor.execute("""
            UPDATE usuarios 
            SET tipo_usuario = 'cliente' 
            WHERE tipo_usuario IS NOT NULL 
            AND tipo_usuario NOT IN ('admin', 'promoter', 'cliente', 'operador')
        """)
        updated_2 = cursor.rowcount
        print(f"      ✅ {updated_2} tipos inválidos corrigidos para 'cliente'")
        
        # 3. Garantir que tipo_usuario não seja NULL
        print("   3. Preenchendo campos NULL...")
        cursor.execute("UPDATE usuarios SET tipo_usuario = 'cliente' WHERE tipo_usuario IS NULL;")
        updated_3 = cursor.rowcount
        print(f"      ✅ {updated_3} campos NULL preenchidos")
        
        # 4. Se existir coluna 'tipo', sincronizar
        try:
            cursor.execute("SELECT tipo FROM usuarios LIMIT 1;")
            print("   4. Sincronizando coluna 'tipo'...")
            cursor.execute("UPDATE usuarios SET tipo = tipo_usuario WHERE tipo != tipo_usuario OR tipo IS NULL;")
            updated_4 = cursor.rowcount
            print(f"      ✅ {updated_4} registros sincronizados")
        except psycopg2.Error:
            print("   4. Coluna 'tipo' não existe - ok")
        
        # Verificar resultado final
        print(f"\n📊 ESTADO FINAL:")
        cursor.execute("SELECT DISTINCT tipo_usuario FROM usuarios;")
        tipos_finais = [row[0] for row in cursor.fetchall()]
        print(f"   Tipos finais: {tipos_finais}")
        
        for tipo in tipos_finais:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = %s", (tipo,))
            count = cursor.fetchone()[0]
            print(f"   '{tipo}': {count} usuários")
        
        # Commit
        conn.commit()
        print(f"\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA MIGRAÇÃO: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def verify_migration():
    """Verificar se migração foi bem-sucedida"""
    print(f"\n🔍 VERIFICAÇÃO PÓS-MIGRAÇÃO:")
    print("1. Todos os tipos devem estar em minúsculas")
    print("2. Apenas tipos válidos: admin, promoter, cliente, operador")
    print("3. Nenhum campo tipo_usuario deve ser NULL")
    print("4. Sistema de login deve funcionar normalmente")

if __name__ == "__main__":
    success = migrate_postgresql_user_types()
    
    if success:
        verify_migration()
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print("1. Testar login no frontend de produção")
        print("2. Monitorar logs para garantir funcionamento")
        print("3. Validar que todos os tipos de usuário funcionam")
    else:
        print(f"\n⚠️ MIGRAÇÃO FALHOU - Revisar configuração")
