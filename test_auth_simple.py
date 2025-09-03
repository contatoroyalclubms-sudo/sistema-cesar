import sys
import os
import sqlite3

# Testar diretamente no banco
conn = sqlite3.connect('backend/eventos.db')
cursor = conn.cursor()

print("=== VERIFICAÇÃO DIRETA NO BANCO ===")
cursor.execute("SELECT cpf, nome FROM usuarios WHERE cpf = '00000000000'")
result = cursor.fetchone()
if result:
    print(f"✅ Usuário encontrado: {result[0]} - {result[1]}")
else:
    print("❌ Usuário não encontrado")
    
print("\nTodos os usuários:")
cursor.execute("SELECT cpf, nome FROM usuarios")
all_users = cursor.fetchall()
for cpf, nome in all_users:
    print(f"   {cpf} - {nome}")

conn.close()

# Agora testar com SQLAlchemy
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.auth_functions import autenticar_usuario, verificar_senha
from backend.app.database import SessionLocal
from backend.app.models import Usuario

# Criar sessão do banco
db = SessionLocal()

try:
    print("=== TESTE DE AUTENTICAÇÃO DIRETA ===\n")
    
    # Buscar usuário direto no banco
    usuario = db.query(Usuario).filter(Usuario.cpf == "00000000000").first()
    
    if usuario:
        print(f"✅ Usuário encontrado:")
        print(f"   CPF: {usuario.cpf}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Hash: {usuario.senha_hash[:30]}...")
        
        # Testar verificação de senha
        print(f"\n🔐 Testando verificação de senha...")
        senha_correta = verificar_senha("0000", usuario.senha_hash)
        print(f"   Senha '0000' válida? {senha_correta}")
        
        # Testar autenticação completa
        print(f"\n🔑 Testando autenticação completa...")
        auth_result = autenticar_usuario("00000000000", "0000", db)
        print(f"   Resultado: {'✅ SUCESSO' if auth_result else '❌ FALHOU'}")
        
        if auth_result:
            print(f"   Usuario autenticado: {auth_result.nome}")
        
    else:
        print("❌ Usuário com CPF 00000000000 não encontrado!")
    
    # Testar também o outro usuário
    print("\n" + "="*50)
    usuario2 = db.query(Usuario).filter(Usuario.cpf == "06601206154").first()
    
    if usuario2:
        print(f"✅ Segundo usuário encontrado:")
        print(f"   CPF: {usuario2.cpf}")
        print(f"   Nome: {usuario2.nome}")
        
        # Testar autenticação
        auth_result2 = autenticar_usuario("06601206154", "101112", db)
        print(f"   Autenticação: {'✅ SUCESSO' if auth_result2 else '❌ FALHOU'}")
        
finally:
    db.close()
