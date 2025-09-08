#!/usr/bin/env python3
"""
Script para debugar problemas no ranking
"""
import os
import sys
from sqlalchemy import create_engine, text

# Adicionar path do backend
sys.path.append('backend')

from backend.app.database import engine

def check_ranking_data():
    """Verificar dados necessários para o ranking"""
    with engine.connect() as conn:
        # Verificar usuários promoter
        result = conn.execute(text("SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'promoter'"))
        promoters = result.fetchone()[0]
        print(f"👤 Promoters encontrados: {promoters}")
        
        # Verificar listas
        result = conn.execute(text("SELECT COUNT(*) as total FROM listas"))
        listas = result.fetchone()[0]
        print(f"📋 Listas encontradas: {listas}")
        
        # Verificar transações
        result = conn.execute(text("SELECT COUNT(*) as total FROM transacoes"))
        transacoes = result.fetchone()[0]
        print(f"💰 Transações encontradas: {transacoes}")
        
        # Verificar checkins
        result = conn.execute(text("SELECT COUNT(*) as total FROM checkins"))
        checkins = result.fetchone()[0]
        print(f"✅ Check-ins encontrados: {checkins}")
        
        # Verificar eventos
        result = conn.execute(text("SELECT COUNT(*) as total FROM eventos"))
        eventos = result.fetchone()[0]
        print(f"🎉 Eventos encontrados: {eventos}")
        
        # Verificar conquistas
        result = conn.execute(text("SELECT COUNT(*) as total FROM conquistas"))
        conquistas = result.fetchone()[0]
        print(f"🏆 Conquistas encontradas: {conquistas}")
        
        print("\n" + "="*50)
        
        if promoters == 0:
            print("❌ PROBLEMA: Não há promoters no sistema!")
            print("💡 Solução: Criar usuários do tipo 'promoter'")
        elif listas == 0:
            print("❌ PROBLEMA: Não há listas no sistema!")
            print("💡 Solução: Criar listas para os promoters")
        elif transacoes == 0:
            print("❌ PROBLEMA: Não há transações no sistema!")
            print("💡 Solução: Criar transações de teste")
        else:
            print("✅ Dados básicos encontrados. Problema pode estar na query.")

if __name__ == "__main__":
    try:
        check_ranking_data()
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
