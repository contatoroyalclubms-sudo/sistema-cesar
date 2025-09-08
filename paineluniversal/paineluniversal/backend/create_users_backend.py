import sqlite3
from passlib.context import CryptContext
from datetime import datetime

# Configurar contexto de hash
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Conectar ao banco do backend
conn = sqlite3.connect('eventos.db')
cursor = conn.cursor()

# Verificar se tabela existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
if not cursor.fetchone():
    print('Criando tabela usuarios...')
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf VARCHAR(14) NOT NULL UNIQUE,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            telefone VARCHAR(20),
            senha_hash VARCHAR(255) NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            ultimo_login DATETIME,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME
        )
    ''')

# Gerar hash da senha
hash_0000 = pwd_context.hash('0000')
hash_101112 = pwd_context.hash('101112')

# Inserir usuários
try:
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('00000000000', 'Admin Demo', 'admin@demo.com', '11999999999', hash_0000, 'admin', 1))
    
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('06601206154', 'Admin Teste', 'admin@teste.com', '11999999999', hash_101112, 'admin', 1))
    
    conn.commit()
    print('✅ Usuários criados no banco do backend!')
    
    # Verificar
    cursor.execute('SELECT cpf, nome FROM usuarios')
    users = cursor.fetchall()
    for cpf, nome in users:
        print(f'   {cpf} - {nome}')
        
except Exception as e:
    print(f'Erro: {e}')
finally:
    conn.close()
