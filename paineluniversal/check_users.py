import sqlite3
import sys

try:
    # Conectar ao banco
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    
    # Verificar usuários na tabela
    cursor.execute("SELECT cpf, nome, tipo_usuario FROM usuarios ORDER BY cpf")
    usuarios = cursor.fetchall()
    
    print(f"Total de usuários encontrados: {len(usuarios)}")
    print("=" * 50)
    
    for cpf, nome, tipo in usuarios:
        print(f"CPF: {cpf}")
        print(f"Nome: {nome}")
        print(f"Tipo: {tipo}")
        print("-" * 30)
    
    # Verificar especificamente o usuário 00000000000
    cursor.execute("SELECT * FROM usuarios WHERE cpf = '00000000000'")
    user = cursor.fetchone()
    
    if user:
        print("\nDetalhes do usuário CPF 00000000000:")
        print(f"ID: {user[0]}")
        print(f"CPF: {user[1]}")
        print(f"Nome: {user[2]}")
        print(f"Email: {user[3]}")
        print(f"Tipo: {user[4]}")
        print(f"Hash da senha: {user[5][:20]}...") # Só primeiros 20 caracteres
    else:
        print("\nUsuário com CPF 00000000000 NÃO ENCONTRADO!")
        
    conn.close()
    
except Exception as e:
    print(f"Erro ao verificar banco: {e}")
    sys.exit(1)
