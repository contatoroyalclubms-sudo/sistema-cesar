import sqlite3

# Verificar se migração foi bem-sucedida
conn = sqlite3.connect("backend/eventos.db")
cursor = conn.cursor()

print("🔍 Verificando estrutura da tabela após migração...")
cursor.execute("PRAGMA table_info(produtos)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Colunas atuais: {columns}")

if 'evento_id' not in columns:
    print("✅ Coluna evento_id removida com SUCESSO!")
else:
    print("❌ Erro: coluna evento_id ainda existe")

# Verificar quantos produtos temos
cursor.execute("SELECT COUNT(*) FROM produtos")
count = cursor.fetchone()[0]
print(f"📊 Total de produtos na tabela: {count}")

# Testar operação básica
try:
    cursor.execute("SELECT id, nome, tipo, preco FROM produtos LIMIT 3")
    produtos = cursor.fetchall()
    print(f"✅ Query funcionando: encontrados {len(produtos)} produtos")
    for produto in produtos:
        print(f"  - ID: {produto[0]}, Nome: {produto[1]}, Tipo: {produto[2]}, Preço: {produto[3]}")
except Exception as e:
    print(f"❌ Erro na query: {e}")

conn.close()
print("🎉 Validação concluída!")
