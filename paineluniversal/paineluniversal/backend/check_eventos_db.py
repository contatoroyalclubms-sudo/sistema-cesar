import sqlite3

print('🔍 Verificando banco eventos.db...')
try:
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('📋 Tabelas encontradas:')
    for table in tables:
        print(f'  - {table[0]}')
        
    # Verificar especificamente a tabela usuarios
    table_names = [t[0] for t in tables]
    if 'usuarios' in table_names:
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        count = cursor.fetchone()[0]
        print(f'\n👥 {count} usuários na tabela usuarios')
        
        # Verificar schema da tabela usuarios
        cursor.execute('PRAGMA table_info(usuarios)')
        columns = cursor.fetchall()
        print('\n📋 Colunas da tabela usuarios:')
        for col in columns:
            nullable = "nullable" if col[3] == 0 else "not null"
            print(f'  - {col[1]} ({col[2]}) - {nullable}')
            
        # Verificar se tem empresa_id
        has_empresa_id = any(col[1] == 'empresa_id' for col in columns)
        print(f'\n🏢 Tem empresa_id? {has_empresa_id}')
    else:
        print('\n❌ Tabela usuarios não encontrada!')
    
    conn.close()
    print('\n✅ Verificação concluída')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
