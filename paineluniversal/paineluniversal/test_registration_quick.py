#!/usr/bin/env python3
"""
Teste rápido de registro após criação de tabelas
"""
import sys
import os
import time

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_user_registration_quick():
    print("🧪 TESTE RÁPIDO: Registro de usuário")
    print("=" * 40)
    
    try:
        print("1️⃣ Importando módulos...")
        from app.models import Usuario
        from app.database import SessionLocal
        from datetime import datetime
        import hashlib
        
        print("2️⃣ Criando sessão...")
        db = SessionLocal()
        
        print("3️⃣ Verificando se tabela usuarios existe...")
        try:
            count = db.query(Usuario).count()
            print(f"✅ Tabela usuarios existe - {count} usuários")
        except Exception as e:
            print(f"❌ Problema com tabela usuarios: {e}")
            return False
        
        print("4️⃣ Tentando criar usuário de teste...")
        test_time = int(time.time())
        
        novo_usuario = Usuario(
            nome=f"Teste {test_time}",
            email=f"teste{test_time}@teste.com",
            cpf=f"111{test_time}"[-11:],  # CPF único
            telefone="11999999999",
            senha_hash=hashlib.md5(b"123456").hexdigest(),
            tipo="CLIENTE",  # Deve ser maiúsculo conforme enum
            ativo=True
            # criado_em é preenchido automaticamente pelo server_default
        )
        
        start_time = time.time()
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        end_time = time.time()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"🆔 ID: {novo_usuario.id}")
        print(f"⏱️ Tempo: {end_time - start_time:.2f}s")
        
        # Limpar o usuário de teste
        db.delete(novo_usuario)
        db.commit()
        print("🧹 Usuário de teste removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    success = test_user_registration_quick()
    if success:
        print("\n🎉 Registro de usuário funcionando!")
    else:
        print("\n❌ Ainda há problemas no registro!")
