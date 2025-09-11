"""
Teste para verificar se o cadastro de produtos funciona após correções
"""
import os
import sys
sys.path.append(os.getcwd())
from app.database import get_db
from app.models import Produto, TipoProduto, StatusProduto
from sqlalchemy.orm import Session

def test_produto_creation():
    """Testar criação de produto sem evento_id"""
    db = next(get_db())
    
    try:
        print("🧪 Testando criação de produto...")
        
        # Criar produto de teste
        produto_data = {
            "nome": "Produto Teste",
            "descricao": "Produto para testar o cadastro",
            "tipo": TipoProduto.BEBIDA,
            "preco": 15.50,
            "categoria": "Cervejas",
            "codigo_interno": "TEST001",
            "estoque_atual": 10,
            "estoque_minimo": 5,
            "estoque_maximo": 100,
            "controla_estoque": True,
            "status": StatusProduto.ATIVO,
            # evento_id será None por padrão (não especificado)
        }
        
        # Tentar criar produto
        novo_produto = Produto(**produto_data)
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
        
        print(f"✅ Produto criado com sucesso!")
        print(f"   ID: {novo_produto.id}")
        print(f"   Nome: {novo_produto.nome}")
        print(f"   Preço: R$ {novo_produto.preco}")
        print(f"   evento_id: {novo_produto.evento_id}")
        
        # Limpar teste
        db.delete(novo_produto)
        db.commit()
        print("🧹 Produto teste removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar produto: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_produto_creation()
    if success:
        print("\n🎉 TESTE PASSOU! Cadastro de produtos está funcionando")
    else:
        print("\n💥 TESTE FALHOU! Ainda há problemas no cadastro")
