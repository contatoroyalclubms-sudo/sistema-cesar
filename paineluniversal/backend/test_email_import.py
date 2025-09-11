#!/usr/bin/env python3
"""
Teste de importação do serviço de email
"""

try:
    from app.services.email_service import email_service
    print("✅ Email service importado com sucesso")
    print(f"Modo teste: {email_service.test_mode}")
except Exception as e:
    print(f"❌ Erro na importação do email service: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers.auth import router
    print("✅ Router auth importado com sucesso")
except Exception as e:
    print(f"❌ Erro na importação do router auth: {e}")
    import traceback
    traceback.print_exc()

try:
    import app.main
    print("✅ App main importado com sucesso")
except Exception as e:
    print(f"❌ Erro na importação do main: {e}")
    import traceback
    traceback.print_exc()
