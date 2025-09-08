#!/usr/bin/env python3
"""
Script para criar produtos de demonstração e testar o sistema completo
"""
import sys
import os
sys.path.append(os.getcwd())

from backend.app.database import get_db
from backend.app.models import Produto, TipoProduto, StatusProduto, Empresa
from sqlalchemy.orm import Session

def create_demo_products():
    """Criar produtos de demonstração para testar o sistema"""
    print('🛠️ Criando produtos de demonstração...')

    db = next(get_db())
    try:
        # Verificar se existe uma empresa
        empresa = db.query(Empresa).first()
        if not empresa:
            print('📦 Criando empresa padrão...')
            empresa = Empresa(
                nome="Empresa Demo - Painel Universal",
                cnpj="00000000000100",
                email="demo@paineluniversal.com",
                telefone="(11) 99999-9999",
                endereco="Endereço Demo",
                ativa=True
            )
            db.add(empresa)
            db.commit()
            db.refresh(empresa)
            print(f'✅ Empresa criada: {empresa.nome}')

        # Produtos de demonstração
        produtos_demo = [
            {
                'nome': 'Cerveja Heineken 600ml',
                'descricao': 'Cerveja premium importada',
                'tipo': TipoProduto.BEBIDA,
                'preco': 8.50,
                'categoria': 'Cervejas',
                'codigo_interno': 'CERV001',
                'estoque_atual': 50,
                'estoque_minimo': 10,
                'estoque_maximo': 200
            },
            {
                'nome': 'Caipirinha de Cachaça',
                'descricao': 'Drink tradicional brasileiro',
                'tipo': TipoProduto.BEBIDA,
                'preco': 12.00,
                'categoria': 'Drinks',
                'codigo_interno': 'DRINK001',
                'estoque_atual': 30,
                'estoque_minimo': 5,
                'estoque_maximo': 100
            },
            {
                'nome': 'Hambúrguer Artesanal',
                'descricao': 'Hambúrguer com blend especial da casa',
                'tipo': TipoProduto.COMIDA,
                'preco': 25.90,
                'categoria': 'Lanches',
                'codigo_interno': 'FOOD001',
                'estoque_atual': 20,
                'estoque_minimo': 3,
                'estoque_maximo': 50
            },
            {
                'nome': 'Porção de Batata Frita',
                'descricao': 'Batata crocante temperada',
                'tipo': TipoProduto.COMIDA,
                'preco': 15.00,
                'categoria': 'Petiscos',
                'codigo_interno': 'SIDE001',
                'estoque_atual': 40,
                'estoque_minimo': 8,
                'estoque_maximo': 100
            },
            {
                'nome': 'Ingresso VIP',
                'descricao': 'Acesso completo ao evento',
                'tipo': TipoProduto.INGRESSO,
                'preco': 80.00,
                'categoria': 'Ingressos',
                'codigo_interno': 'TICK001',
                'estoque_atual': 100,
                'estoque_minimo': 10,
                'estoque_maximo': 500
            }
        ]

        # Verificar se já existem produtos
        produtos_existentes = db.query(Produto).count()
        if produtos_existentes > 0:
            print(f'⚠️ Já existem {produtos_existentes} produtos no banco. Removendo para demo...')
            db.query(Produto).delete()
            db.commit()

        # Criar produtos de demo
        produtos_criados = []
        for produto_data in produtos_demo:
            produto = Produto(
                **produto_data,
                controla_estoque=True,
                status=StatusProduto.ATIVO,
                empresa_id=empresa.id
            )
            db.add(produto)
            produtos_criados.append(produto)

        db.commit()
        
        print(f'✅ {len(produtos_criados)} produtos criados com sucesso!')
        for produto in produtos_criados:
            db.refresh(produto)
            print(f'   📦 {produto.nome} - R$ {produto.preco} (ID: {produto.id})')

        print('\n🎉 Sistema pronto para teste!')
        print('📋 Produtos disponíveis por categoria:')
        
        categorias = {}
        for produto in produtos_criados:
            if produto.categoria not in categorias:
                categorias[produto.categoria] = []
            categorias[produto.categoria].append(produto)
            
        for categoria, produtos in categorias.items():
            print(f'   🏷️ {categoria}: {len(produtos)} produtos')
            
        return True
        
    except Exception as e:
        print(f'❌ ERRO: {str(e)}')
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_demo_products()
    sys.exit(0 if success else 1)
