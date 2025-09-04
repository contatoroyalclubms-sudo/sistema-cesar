#!/usr/bin/env python3
"""
Diagnóstico completo do sistema de produtos
"""
import sys
import os
sys.path.append(os.getcwd())

from backend.app.database import get_db
from backend.app.models import Produto, TipoProduto, StatusProduto, Empresa
from sqlalchemy.orm import Session
from sqlalchemy import text

def diagnostic_produtos_system():
    """Diagnóstico completo do sistema de produtos"""
    print('🔬 DIAGNÓSTICO COMPLETO DO SISTEMA DE PRODUTOS')
    print('=' * 60)

    db = next(get_db())
    try:
        # 1. Verificar estrutura da tabela produtos
        print('\n1️⃣ ESTRUTURA DA TABELA PRODUTOS:')
        result = db.execute(text("PRAGMA table_info(produtos)"))
        columns = result.fetchall()
        
        for column in columns:
            col_name = column[1]
            col_type = column[2]
            not_null = column[3]
            default_val = column[4]
            print(f"   🔹 {col_name}: {col_type} {'(NOT NULL)' if not_null else '(NULL)'} {f'DEFAULT {default_val}' if default_val else ''}")
            
        # Verificar se evento_id existe
        has_evento_id = any(col[1] == 'evento_id' for col in columns)
        print(f"\n   ❓ Coluna evento_id presente: {'✅ SIM' if has_evento_id else '❌ NÃO'}")
        
        # 2. Verificar produtos existentes
        print('\n2️⃣ PRODUTOS NO BANCO:')
        produtos = db.query(Produto).all()
        print(f"   📊 Total: {len(produtos)} produtos")
        
        if produtos:
            print('   🔍 Primeiros 3 produtos:')
            for i, produto in enumerate(produtos[:3], 1):
                print(f"      {i}. {produto.nome} - R$ {produto.preco}")
                print(f"         Tipo: {produto.tipo}, Status: {produto.status}")
                print(f"         Categoria: {produto.categoria}, Estoque: {produto.estoque_atual}")
                if hasattr(produto, 'evento_id'):
                    print(f"         Evento ID: {produto.evento_id}")
                print(f"         Empresa ID: {produto.empresa_id}")
                print()
        
        # 3. Verificar empresas
        print('3️⃣ EMPRESAS NO BANCO:')
        empresas = db.query(Empresa).all()
        print(f"   📊 Total: {len(empresas)} empresas")
        for empresa in empresas:
            print(f"      🏢 {empresa.nome} (ID: {empresa.id}) - Ativa: {empresa.ativa}")
            
        print('\n🎯 DIAGNÓSTICO COMPLETO!')
        return True
        
    except Exception as e:
        print(f'❌ ERRO GERAL: {str(e)}')
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = diagnostic_produtos_system()
    sys.exit(0 if success else 1)
