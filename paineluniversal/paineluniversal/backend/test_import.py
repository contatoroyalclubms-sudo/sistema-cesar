#!/usr/bin/env python3
"""
Teste de importação do backend
"""

try:
    import app.main
    print("✅ Backend importação OK")
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    import traceback
    traceback.print_exc()
