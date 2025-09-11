import sqlite3

print('🔍 Verificando tabelas existentes...')
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('📋 Tabelas encontradas:')
for table in tables:
    print(f'  - {table[0]}')
    
print(f'\n📊 Total: {len(tables)} tabelas')
conn.close()
