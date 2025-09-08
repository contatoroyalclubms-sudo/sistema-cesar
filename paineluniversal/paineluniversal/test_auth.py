import sqlite3
from passlib.context import CryptContext

# Configurar o mesmo contexto do backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

conn = sqlite3.connect('eventos.db')
cursor = conn.cursor()

# Buscar o usuário
cpf = '06601206154'
cursor.execute('SELECT cpf, senha_hash, tipo FROM usuarios WHERE cpf = ?', (cpf,))
user = cursor.fetchone()

if user:
    print(f'✅ Usuário encontrado: CPF = {user[0]}, Tipo = {user[2]}')
    print(f'Hash da senha no banco: {user[1][:50]}...')
    
    # Testar a senha
    senha_teste = '101112'
    if pwd_context.verify(senha_teste, user[1]):
        print('✅ Senha verificada com sucesso!')
    else:
        print('❌ Senha não confere!')
        
        # Criar nova senha com a mesma lógica
        nova_hash = pwd_context.hash(senha_teste)
        print(f'Nova hash gerada: {nova_hash[:50]}...')
        
        # Atualizar no banco
        cursor.execute('UPDATE usuarios SET senha_hash = ? WHERE cpf = ?', (nova_hash, cpf))
        conn.commit()
        print('✅ Hash atualizada no banco!')
else:
    print('❌ Usuário não encontrado')

conn.close()
