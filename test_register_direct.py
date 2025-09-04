#!/usr/bin/env python3
"""
Teste direto da função de registro sem HTTP
"""
import sys
import os
import time
import traceback
import asyncio

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_register_function_direct():
    print("🧪 TESTE DIRETO: Função de registro")
    print("=" * 40)
    
    try:
        print("1️⃣ Importando módulos...")
        from app.routers.auth import registrar_usuario
        from app.schemas import UsuarioRegister  # Mudando para UsuarioRegister
        from app.database import SessionLocal
        
        print("2️⃣ Criando sessão de banco...")
        db = SessionLocal()
        
        print("3️⃣ Criando dados de teste...")
        test_time = int(time.time())
        
        user_data = UsuarioRegister(  # Mudando para UsuarioRegister
            nome=f"Teste Direto {test_time}",
            email=f"direto{test_time}@teste.com",
            cpf=f"111{test_time}"[-11:],
            telefone="11999999999",
            senha="123456",  # Agora usando senha corretamente
            tipo="CLIENTE"
        )
        
        print(f"4️⃣ Dados: {user_data.model_dump()}")
        
        print("5️⃣ Chamando função de registro...")
        start_time = time.time()
        
        try:
            resultado = await registrar_usuario(user_data, db)
            end_time = time.time()
            
            print(f"✅ Registro bem-sucedido!")
            print(f"⏱️ Tempo: {end_time - start_time:.2f}s")
            print(f"🆔 ID do usuário: {resultado.id}")
            print(f"📧 Email: {resultado.email}")
            
            # Verificar se o campo atualizado_em está presente
            if hasattr(resultado, 'atualizado_em'):
                print(f"📅 atualizado_em: {resultado.atualizado_em}")
                print("✅ Campo atualizado_em presente!")
            else:
                print("❌ Campo atualizado_em AUSENTE!")
            
            # Converter para dict para ver todos os campos
            print("📋 Campos do resultado:")
            for campo, valor in resultado.__dict__.items():
                if not campo.startswith('_'):
                    print(f"  - {campo}: {valor}")
            
            return True
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Erro no registro: {e}")
            print(f"⏱️ Tempo antes do erro: {end_time - start_time:.2f}s")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()
        return False
    
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(test_register_function_direct())
    if success:
        print("\n🎉 Teste direto bem-sucedido!")
    else:
        print("\n❌ Falha no teste direto!")
