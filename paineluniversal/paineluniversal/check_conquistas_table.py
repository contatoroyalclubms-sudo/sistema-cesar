#!/usr/bin/env python3
import sys
sys.path.append('backend')

from backend.app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'conquistas' ORDER BY ordinal_position"))
    print("Colunas da tabela conquistas:")
    for row in result.fetchall():
        print(f"- {row[0]}")
