#!/usr/bin/env python3
"""
Diagnóstico completo do sistema de produtos
"""
import sys
import os
sys.path.append(os.getcwd())            print(f"   🛣️ Total de rotas: {len(routes)}")

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
            
        # 4. Testar criação de produto
        print('\n4️⃣ TESTE DE CRIAÇÃO:')
        try:
            produto_teste = Produto(
                nome='Diagnóstico Test Product',
                descricao='Produto para teste de diagnóstico',
                tipo=TipoProduto.BEBIDA,
                preco=9.99,
                categoria='Diagnóstico',
                codigo_interno='DIAG_001',
                estoque_atual=1,
                estoque_minimo=0,
                estoque_maximo=10,
                controla_estoque=True,
                status=StatusProduto.ATIVO,
                empresa_id=empresas[0].id if empresas else None
            )
            
            db.add(produto_teste)
            db.commit()
            db.refresh(produto_teste)
            
            print(f"   ✅ Criação: SUCESSO (ID: {produto_teste.id})")
            
            # Testar atualização
            produto_teste.preco = 12.99
            produto_teste.descricao = 'Produto atualizado'
            db.commit()
            print(f"   ✅ Atualização: SUCESSO")
            
            # Testar soft delete
            produto_teste.status = StatusProduto.INATIVO
            db.commit()
            print(f"   ✅ Soft Delete: SUCESSO")
            
            # Limpar teste
            db.delete(produto_teste)
            db.commit()
            print(f"   🧹 Limpeza: SUCESSO")
            
        except Exception as e:
            print(f"   ❌ ERRO no teste: {str(e)}")
            db.rollback()
            
        # 5. Verificar schemas/imports
        print('\n5️⃣ VERIFICAÇÃO DE SCHEMAS:')
        try:
            from backend.app.schemas.produtos import ProdutoCreate, ProdutoResponse, ProdutoUpdate
            print('   ✅ Import schemas.produtos: SUCESSO')
            
            # Verificar campos do schema
            schema_create = ProdutoCreate.schema()
            properties = schema_create.get('properties', {})
            print(f"   📋 Campos ProdutoCreate: {list(properties.keys())}")
            
            if 'evento_id' in properties:
                print('   ⚠️ ATENÇÃO: evento_id ainda presente no schema ProdutoCreate')
            else:
                print('   ✅ evento_id removido do schema ProdutoCreate')
                
        except Exception as e:
            print(f"   ❌ ERRO no import: {str(e)}")
            
        # 6. Verificar router
        print('\n6️⃣ VERIFICAÇÃO DE ROUTER:')
        try:
            from backend.app.routers.produtos import router
            print('   ✅ Import router produtos: SUCESSO')
            
            # Verificar rotas
            routes = [route for route in router.routes]
            print(f"   🛣️ Total de rotas: {len(routes)}")
            for route in routes[:5]:  # Primeiras 5 rotas
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = list(route.methods) if route.methods else []
                    print(f"      {methods} {route.path}")
                    
        except Exception as e:
            print(f"   ❌ ERRO no router: {str(e)}")
            
        print('\n' + '=' * 60)
        print('🎯 DIAGNÓSTICO COMPLETO!')
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
