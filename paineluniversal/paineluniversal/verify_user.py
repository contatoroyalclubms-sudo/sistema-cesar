import psycopg2
from psycopg2.extras import DictCursor

try:
    conn = psycopg2.connect(
        host='localhost',
        database='paineluniversal',
        user='painel_user',
        password='painel123'
    )
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT id, nome, email, cpf, tipo FROM usuarios ORDER BY id DESC LIMIT 1')
    user = cur.fetchone()
    print(f'✅ Usuário mais recente: ID={user[0]}, Nome={user[1]}, Email={user[2]}, CPF={user[3]}, Tipo={user[4]}')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
