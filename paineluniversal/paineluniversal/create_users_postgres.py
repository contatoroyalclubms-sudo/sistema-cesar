import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime

# Configuração da conexão
DB_CONFIG = {
    'host': 'localhost',
    'database': 'paineluniversal',
    'user': 'painel_user',
    'password': 'painel123',
    'port': 5432
}

try:
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("✅ Conectado ao PostgreSQL")
    
    # Verificar se tabela usuarios existe
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'usuarios'
    """)
    
    if not cursor.fetchone():
        print("Criando tabela usuarios...")
        cursor.execute("""
            CREATE TABLE usuarios (
                id SERIAL PRIMARY KEY,
                cpf VARCHAR(14) NOT NULL UNIQUE,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                senha_hash VARCHAR(255) NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                ativo BOOLEAN DEFAULT true,
                ultimo_login TIMESTAMP WITH TIME ZONE,
                criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP WITH TIME ZONE
            )
        """)
        conn.commit()
        print("✅ Tabela usuarios criada")
    
    # Deletar usuários existentes se houver
    cursor.execute("DELETE FROM usuarios WHERE cpf IN (%s, %s)", ('06601206154', '00000000000'))
    conn.commit()
    
    # Gerar hashes das senhas
    hash_101112 = bcrypt.hashpw('101112'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    hash_0000 = bcrypt.hashpw('0000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    now = datetime.now()
    
    # Inserir usuário principal para testes
    cursor.execute("""
        INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo, criado_em, atualizado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, ('06601206154', 'Admin Teste', 'admin@teste.com', '11999999999', hash_101112, 'admin', True, now, now))
    
    # Inserir usuário padrão
    cursor.execute("""
        INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo, criado_em, atualizado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, ('00000000000', 'Admin Demo', 'admin@demo.com', '11999999999', hash_0000, 'admin', True, now, now))
    
    conn.commit()
    
    print("✅ Usuários criados no PostgreSQL:")
    print("   CPF: 06601206154, Senha: 101112")
    print("   CPF: 00000000000, Senha: 0000")
    
    # Verificar usuários criados
    cursor.execute("SELECT cpf, nome, tipo FROM usuarios ORDER BY cpf")
    usuarios = cursor.fetchall()
    
    print("\nUsuários na tabela:")
    for user in usuarios:
        print(f"   {user['cpf']} - {user['nome']} ({user['tipo']})")
        
except Exception as e:
    print(f"Erro: {e}")
finally:
    if 'conn' in locals():
        conn.close()
