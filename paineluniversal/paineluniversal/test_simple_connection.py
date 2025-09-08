#!/usr/bin/env python3
import os
import sys
import time

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("🔍 Teste super simples de conectividade...")
print(f"⏰ Iniciado em: {time.strftime('%H:%M:%S')}")

try:
    print("📦 Importando módulos...")
    from app.models import Usuario
    from app.database import SessionLocal
    print("✅ Módulos importados com sucesso")
    
    print("🔗 Criando sessão...")
    db = SessionLocal()
    print("✅ Sessão criada")
    
    print("📊 Contando usuários...")
    start_time = time.time()
    count = db.query(Usuario).count()
    end_time = time.time()
    
    print(f"✅ Query executada em {end_time - start_time:.2f}s")
    print(f"📈 {count} usuários encontrados")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print(f"❌ Tipo: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
finally:
    try:
        if 'db' in locals():
            db.close()
            print("🔚 Sessão fechada")
    except:
        pass
    
    print(f"⏰ Finalizado em: {time.strftime('%H:%M:%S')}")
