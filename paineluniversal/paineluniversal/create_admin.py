import sqlite3
from passlib.context import CryptContext
from datetime import datetime

# Configurar o mesmo contexto do backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

conn = sqlite3.connect('eventos.db')
cursor = conn.cursor()

# Criar usuário admin padrão
cpf = '00000000000'
senha = '0000'
senha_hash = pwd_context.hash(senha)
now = datetime.now().isoformat()

# Deletar se existir
cursor.execute('DELETE FROM usuarios WHERE cpf = ?', (cpf,))

# Inserir novo usuário
cursor.execute('''
    INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo, criado_em, atualizado_em)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (cpf, 'Admin Padrão', 'admin@demo.com', '11999999999', senha_hash, 'admin', True, now, now))

conn.commit()
print(f'✅ Usuário admin padrão criado! CPF: {cpf}, Senha: {senha}')

# Verificar
cursor.execute('SELECT id, cpf, nome, tipo FROM usuarios WHERE cpf = ?', (cpf,))
user = cursor.fetchone()
if user:
    print(f'✅ Confirmado - ID: {user[0]}, CPF: {user[1]}, Nome: {user[2]}, Tipo: {user[3]}')

# Testar a senha
if pwd_context.verify(senha, senha_hash):
    print('✅ Senha testada e confirmada!')
else:
    print('❌ Erro na verificação da senha!')

conn.close()
