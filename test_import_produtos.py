#!/usr/bin/env python3
"""
Script de teste para a funcionalidade de importação de produtos
Testa o endpoint completo de importação com dados de exemplo
"""

import os
import sys
import tempfile
import pandas as pd
import requests
from typing import Optional

# Configurações da API
API_BASE_URL = "http://localhost:8000"
IMPORT_ENDPOINT = f"{API_BASE_URL}/produtos/import"
TEMPLATE_ENDPOINT = f"{API_BASE_URL}/produtos/import/template"

def create_sample_csv() -> str:
    """Cria um arquivo CSV de exemplo com produtos para teste"""
    data = [
        {
            "nome": "Produto Teste 1",
            "preco": 25.50,
            "categoria": "Eletrônicos",
            "codigo_interno": "TEST001",
            "estoque_atual": 10,
            "descricao": "Descrição do produto teste 1",
            "tipo": "PRODUTO"
        },
        {
            "nome": "Produto Teste 2", 
            "preco": 45.99,
            "categoria": "Casa",
            "codigo_interno": "TEST002",
            "estoque_atual": 5,
            "descricao": "Descrição do produto teste 2",
            "tipo": "PRODUTO"
        },
        {
            "nome": "Serviço Teste 1",
            "preco": 100.00,
            "categoria": "Serviços",
            "codigo_interno": "SERV001",
            "estoque_atual": 0,
            "descricao": "Descrição do serviço teste",
            "tipo": "SERVICO"
        }
    ]
    
    df = pd.DataFrame(data)
    
    # Criar arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    print(f"✅ Arquivo CSV criado: {temp_file.name}")
    print(f"📊 Dados do arquivo:")
    print(df.to_string(index=False))
    print()
    
    return temp_file.name

def test_template_download():
    """Testa o download do template"""
    print("🔍 Testando download do template...")
    try:
        response = requests.get(TEMPLATE_ENDPOINT)
        if response.status_code == 200:
            print("✅ Template baixado com sucesso")
            # Salvar template para verificação
            with open("template_produtos.csv", "wb") as f:
                f.write(response.content)
            print("📝 Template salvo como 'template_produtos.csv'")
        else:
            print(f"❌ Erro ao baixar template: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    return True

def test_import_csv(csv_file: str) -> bool:
    """Testa a importação do arquivo CSV"""
    print("📤 Testando importação de produtos...")
    
    try:
        # Preparar arquivo para upload
        with open(csv_file, 'rb') as f:
            files = {'file': ('test_produtos.csv', f, 'text/csv')}
            
            response = requests.post(IMPORT_ENDPOINT, files=files)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ Importação realizada com sucesso!")
            print(f"📊 Resultado:")
            print(f"   - Produtos processados: {result.get('total_processados', 0)}")
            print(f"   - Sucessos: {result.get('sucessos', 0)}")
            print(f"   - Erros: {result.get('erros', 0)}")
            
            # Mostrar detalhes dos sucessos
            if result.get('produtos_criados'):
                print(f"✅ Produtos criados com sucesso:")
                for produto in result['produtos_criados']:
                    print(f"   - {produto.get('nome', 'N/A')} (ID: {produto.get('id', 'N/A')})")
            
            # Mostrar detalhes dos erros
            if result.get('detalhes_erros'):
                print(f"❌ Erros encontrados:")
                for erro in result['detalhes_erros']:
                    print(f"   - Linha {erro.get('linha', 'N/A')}: {erro.get('erro', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erro na importação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def cleanup_temp_files(*files):
    """Remove arquivos temporários"""
    for file_path in files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️ Arquivo temporário removido: {file_path}")
        except Exception as e:
            print(f"⚠️ Erro ao remover {file_path}: {e}")

def main():
    """Função principal de teste"""
    print("🚀 TESTE DA FUNCIONALIDADE DE IMPORTAÇÃO DE PRODUTOS")
    print("=" * 60)
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API não está respondendo corretamente")
            print("Certifique-se de que o backend está rodando em http://localhost:8000")
            return
    except Exception as e:
        print(f"❌ Não foi possível conectar à API: {e}")
        print("Certifique-se de que o backend está rodando em http://localhost:8000")
        return
    
    print("✅ API está rodando!")
    print()
    
    # Teste 1: Download do template
    if not test_template_download():
        print("❌ Teste do template falhou. Abortando.")
        return
    
    print()
    
    # Teste 2: Criar arquivo de teste
    csv_file = create_sample_csv()
    
    # Teste 3: Importação
    success = test_import_csv(csv_file)
    
    # Cleanup
    cleanup_temp_files(csv_file)
    
    print()
    print("=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A funcionalidade de importação está funcionando corretamente.")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os logs acima para detalhes dos erros.")

if __name__ == "__main__":
    main()
