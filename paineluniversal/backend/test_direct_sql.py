#!/usr/bin/env python3
"""
Teste de inserção direta SQL para diagnosticar problema de timeout
"""
import sqlite3
import hashlib
from datetime import datetime
import time

def test_direct_sql_insert():
    print("🧪 TESTE: Inserção SQL direta")
    print("=" * 40)
    
    try:
        print("1️⃣ Conectando ao banco...")
        conn = sqlite3.connect('app.db', timeout=10.0)
        cursor = conn.cursor()
        
        print("2️⃣ Verificando schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='usuarios'")
        schema = cursor.fetchone()
        if schema:
            print("📋 Schema encontrado:")
            print(schema[0])
        else:
            print("❌ Tabela usuarios não encontrada!")
            return
        
        print("\n3️⃣ Verificando usuários existentes...")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"📊 {count} usuários existentes")
        
        print("\n4️⃣ Preparando inserção de teste...")
        test_cpf = "12345678901"
        test_email = f"teste_direto_{int(time.time())}@teste.com"
        senha_hash = hashlib.md5(b"123456").hexdigest()
        
        # Verificar se CPF já existe
        cursor.execute("SELECT id FROM usuarios WHERE cpf = ?", (test_cpf,))
        if cursor.fetchone():
            print(f"🔄 CPF {test_cpf} já existe, usando CPF único...")
            test_cpf = f"999{int(time.time())}"[-11:]  # CPF único baseado em timestamp
        
        print(f"📧 Email: {test_email}")
        print(f"📱 CPF: {test_cpf}")
        
        print("\n5️⃣ Executando inserção...")
        start_time = time.time()
        
        cursor.execute("""
        INSERT INTO usuarios (nome, email, cpf, telefone, senha_hash, tipo, ativo, data_criacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Teste Direto SQL",
            test_email,
            test_cpf,
            "11999999999",
            senha_hash,
            "cliente",
            1,  # ativo = True
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        end_time = time.time()
        
        user_id = cursor.lastrowid
        print(f"✅ Usuário criado com sucesso!")
        print(f"🆔 ID: {user_id}")
        print(f"⏱️ Tempo: {end_time - start_time:.2f}s")
        
        print("\n6️⃣ Verificando inserção...")
        cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verificado: {user}")
        else:
            print("❌ Usuário não encontrado após inserção!")
        
    except sqlite3.Error as e:
        print(f"❌ Erro SQLite: {e}")
        print(f"❌ Tipo: {type(e).__name__}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print(f"❌ Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            conn.close()
            print("🔚 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    test_direct_sql_insert()
