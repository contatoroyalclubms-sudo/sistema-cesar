import os
print("🔍 Debug do ambiente:")
print(f"📁 Current directory: {os.getcwd()}")
print(f"📦 DATABASE_URL: {os.getenv('DATABASE_URL', 'Não definida')}")

try:
    print("🔧 Tentando importar módulos...")
    from app.database import SessionLocal, settings
    print("✅ Módulos importados com sucesso")
    print(f"🗄️ Database URL: {settings.database_url}")
    
    print("🔗 Tentando conectar ao banco...")
    db = SessionLocal()
    print("✅ Conexão criada")
    
    from app.models import Empresa
    print("📊 Contando empresas...")
    count = db.query(Empresa).count()
    print(f"🏢 Total de empresas: {count}")
    
    empresas = db.query(Empresa).all()
    for empresa in empresas:
        print(f"   - {empresa.nome} (ID: {empresa.id})")
    
    db.close()
    print("✅ Conexão fechada")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
