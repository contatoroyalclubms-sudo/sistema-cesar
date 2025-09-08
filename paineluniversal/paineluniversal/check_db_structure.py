import sqlite3

try:
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = cursor.fetchall()
    
    print("Estrutura da tabela 'usuarios':")
    print("=" * 40)
    for col in colunas:
        print(f"{col[1]} ({col[2]}) - NOT NULL: {col[3]} - DEFAULT: {col[4]}")
    
    print("\n" + "=" * 40)
    
    # Verificar todos os usuários com todas as colunas disponíveis
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    
    print(f"\nTotal de usuários: {len(usuarios)}")
    for i, user in enumerate(usuarios):
        print(f"\nUsuário {i+1}:")
        for j, col in enumerate(colunas):
            print(f"  {col[1]}: {user[j]}")
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
