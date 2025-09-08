#!/usr/bin/env python3
"""
Teste de API para produtos - verificar se endpoints estão funcionando
"""
import requests
import json
import sys
import os

def test_produtos_api():
    """Testar endpoints de produtos"""
    print('🔍 Testando API de produtos...')
    
    # URL base da API (assumindo que está rodando localmente)
    base_url = "http://localhost:8000/api"
    
    try:
        # Teste 1: Listar produtos (GET /api/produtos/)
        print('\n📋 Teste 1: Listar produtos')
        response = requests.get(f"{base_url}/produtos/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Formato da resposta: {type(data)}")
            
            if isinstance(data, dict) and 'produtos' in data:
                produtos = data['produtos']
                total = data.get('total', 0)
                print(f"📦 Total de produtos: {total}")
                print(f"📦 Produtos na página: {len(produtos)}")
                
                if produtos:
                    produto = produtos[0]
                    print(f"🔍 Primeiro produto:")
                    print(f"   Nome: {produto.get('nome')}")
                    print(f"   Preço: R$ {produto.get('preco')}")
                    print(f"   Tipo: {produto.get('tipo')}")
                    print(f"   Categoria: {produto.get('categoria')}")
                    print(f"   Estoque: {produto.get('estoque_atual')}")
                    
            elif isinstance(data, list):
                print(f"📦 Lista direta com {len(data)} produtos")
                if data:
                    produto = data[0]
                    print(f"🔍 Primeiro produto: {produto.get('nome')} - R$ {produto.get('preco')}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Teste 2: Criar produto (POST /api/produtos/)
        print('\n📝 Teste 2: Criar produto')
        produto_data = {
            "nome": "Produto Teste API",
            "descricao": "Produto criado via teste de API",
            "tipo": "BEBIDA",
            "preco": 15.50,
            "categoria": "Teste API",
            "codigo_interno": "API_TEST_001",
            "estoque_atual": 10,
            "estoque_minimo": 2,
            "estoque_maximo": 50,
            "controla_estoque": True,
            "status": "ATIVO"
        }
        
        response = requests.post(f"{base_url}/produtos/", json=produto_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            produto_criado = response.json()
            produto_id = produto_criado.get('id')
            print(f"✅ Produto criado com sucesso! ID: {produto_id}")
            
            # Teste 3: Buscar produto específico (GET /api/produtos/{id})
            print(f'\n🔍 Teste 3: Buscar produto ID {produto_id}')
            response = requests.get(f"{base_url}/produtos/{produto_id}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                produto = response.json()
                print(f"✅ Produto encontrado: {produto.get('nome')}")
            else:
                print(f"❌ Erro ao buscar produto: {response.text}")
                
            # Teste 4: Atualizar produto (PUT /api/produtos/{id})
            print(f'\n✏️ Teste 4: Atualizar produto ID {produto_id}')
            update_data = {
                "preco": 18.90,
                "descricao": "Produto atualizado via API"
            }
            response = requests.put(f"{base_url}/produtos/{produto_id}", json=update_data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Produto atualizado com sucesso!")
            else:
                print(f"❌ Erro ao atualizar: {response.text}")
                
            # Teste 5: Deletar produto (DELETE /api/produtos/{id})
            print(f'\n🗑️ Teste 5: Deletar produto ID {produto_id}')
            response = requests.delete(f"{base_url}/produtos/{produto_id}")
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 204]:
                print("✅ Produto deletado com sucesso!")
            else:
                print(f"❌ Erro ao deletar: {response.text}")
                
        else:
            print(f"❌ Erro ao criar produto: {response.status_code}")
            print(f"Response: {response.text}")
            
        print('\n🎉 Teste de API completo!')
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API.")
        print("   Verifique se o backend está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_produtos_api()
    sys.exit(0 if success else 1)
