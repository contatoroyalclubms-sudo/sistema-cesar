#!/usr/bin/env python3
"""
Teste para verificar se o sistema de produtos está funcionando após correções
"""
import sys
import os
sys.path.append(os.getcwd())

from backend.app.database import get_db
from backend.app.models import Produto, TipoProduto, StatusProduto
from sqlalchemy.orm import Session

def test_produtos_system():
    """Testar sistema de produtos após correções"""
    print('🧪 Testando sistema de produtos após correções...')

    db = next(get_db())
    try:
        # Verificar se existem produtos
        produtos = db.query(Produto).all()
        print(f'📊 Total de produtos no banco: {len(produtos)}')
        
        if produtos:
            produto = produtos[0]
            print(f'🔍 Primeiro produto: {produto.nome} - Preço: R$ {produto.preco}')
            print(f'   ID: {produto.id}')
            print(f'   Tipo: {produto.tipo}')
            print(f'   Status: {produto.status}')
            print(f'   Evento ID: {getattr(produto, "evento_id", "[REMOVIDO]")}')
            print(f'   Empresa ID: {produto.empresa_id}')
            
        # Tentar criar um produto teste
        print('\n🔧 Testando criação de produto...')
        produto_teste = Produto(
            nome='Produto Teste API',
            descricao='Teste após correções',
            tipo=TipoProduto.BEBIDA,
            preco=10.50,
            categoria='Teste',
            codigo_interno='TEST_API_001',
            estoque_atual=5,
            estoque_minimo=1,
            estoque_maximo=50,
            controla_estoque=True,
            status=StatusProduto.ATIVO
        )
        
        db.add(produto_teste)
        db.commit()
        db.refresh(produto_teste)
        
        print(f'✅ Produto teste criado com sucesso!')
        print(f'   ID: {produto_teste.id}')
        print(f'   Nome: {produto_teste.nome}')
        print(f'   Preço: R$ {produto_teste.preco}')
        
        # Limpar teste
        db.delete(produto_teste)
        db.commit()
        print('🧹 Produto teste removido')
        
        print('\n🎉 SUCESSO: Sistema de produtos funcionando corretamente!')
        return True
        
    except Exception as e:
        print(f'❌ ERRO: {str(e)}')
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_produtos_system()
    sys.exit(0 if success else 1)
