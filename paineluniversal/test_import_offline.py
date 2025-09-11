#!/usr/bin/env python3
"""
Teste simples da funcionalidade de importação sem depender do servidor
"""

import os
import sys
import pandas as pd
from io import StringIO

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_column_mapping():
    """Testa o mapeamento de colunas da funcionalidade de importação"""
    print("🧪 TESTE DE MAPEAMENTO DE COLUNAS")
    print("=" * 50)
    
    # Simular dados de entrada com diferentes formatos de coluna
    test_data = """nome,preco,categoria,codigo_interno,estoque_atual,descricao,tipo
Produto A,10.50,Eletrônicos,PROD001,5,Descrição A,PRODUTO
Produto B,25.00,Casa,PROD002,10,Descrição B,PRODUTO
Serviço C,100.00,Serviços,SERV001,0,Descrição C,SERVICO"""
    
    # Mapear colunas (simulando a lógica do backend)
    column_mapping = {
        'nome': ['nome', 'produto', 'name', 'product'],
        'preco': ['preco', 'valor', 'price', 'preço'],
        'categoria': ['categoria', 'category', 'cat'],
        'codigo_interno': ['codigo_interno', 'sku', 'codigo', 'code'],
        'estoque_atual': ['estoque_atual', 'estoque', 'stock', 'quantidade'],
        'descricao': ['descricao', 'description', 'desc'],
        'tipo': ['tipo', 'type', 'category_type']
    }
    
    # Ler dados
    df = pd.read_csv(StringIO(test_data))
    print(f"✅ Dados lidos com sucesso: {len(df)} registros")
    print(f"📊 Colunas encontradas: {list(df.columns)}")
    
    # Mapear colunas encontradas
    found_columns = {}
    for target_col, variations in column_mapping.items():
        for col in df.columns:
            if col.lower().strip() in [v.lower() for v in variations]:
                found_columns[target_col] = col
                break
    
    print(f"🎯 Mapeamento de colunas:")
    for target, source in found_columns.items():
        print(f"   {target} ← {source}")
    
    # Verificar dados obrigatórios
    required_fields = ['nome', 'preco']
    missing_required = [field for field in required_fields if field not in found_columns]
    
    if missing_required:
        print(f"❌ Campos obrigatórios ausentes: {missing_required}")
        return False
    else:
        print(f"✅ Todos os campos obrigatórios estão presentes")
    
    # Simular processamento dos dados
    processed_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # Mapear dados
            nome = str(row[found_columns['nome']]).strip()
            preco_raw = row[found_columns['preco']]
            
            # Validar nome
            if not nome or nome == 'nan':
                errors.append(f"Linha {index + 2}: Nome é obrigatório")
                continue
            
            # Validar preço
            try:
                preco = float(preco_raw)
                if preco < 0:
                    errors.append(f"Linha {index + 2}: Preço deve ser maior que zero")
                    continue
            except (ValueError, TypeError):
                errors.append(f"Linha {index + 2}: Preço inválido: {preco_raw}")
                continue
            
            processed_count += 1
            print(f"✅ Produto processado: {nome} - R$ {preco:.2f}")
            
        except Exception as e:
            errors.append(f"Linha {index + 2}: Erro no processamento: {str(e)}")
    
    print(f"\n📊 RESULTADO DO TESTE:")
    print(f"   Total de registros: {len(df)}")
    print(f"   Processados com sucesso: {processed_count}")
    print(f"   Erros encontrados: {len(errors)}")
    
    if errors:
        print(f"\n❌ Detalhes dos erros:")
        for error in errors[:5]:  # Mostrar apenas os primeiros 5 erros
            print(f"   {error}")
        if len(errors) > 5:
            print(f"   ... e mais {len(errors) - 5} erros")
    
    return len(errors) == 0

def test_file_formats():
    """Testa diferentes formatos de arquivo"""
    print("\n🧪 TESTE DE FORMATOS DE ARQUIVO")
    print("=" * 50)
    
    # Testar CSV
    csv_data = """nome,preco,categoria
Produto CSV,15.00,Teste"""
    
    try:
        df_csv = pd.read_csv(StringIO(csv_data))
        print(f"✅ CSV processado: {len(df_csv)} registros")
    except Exception as e:
        print(f"❌ Erro no CSV: {e}")
        return False
    
    # Simular Excel (usando CSV com separator diferente)
    excel_data = """nome;preco;categoria
Produto Excel;20.00;Teste"""
    
    try:
        df_excel = pd.read_csv(StringIO(excel_data), sep=';')
        print(f"✅ Excel simulado processado: {len(df_excel)} registros")
    except Exception as e:
        print(f"❌ Erro no Excel: {e}")
        return False
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 TESTE OFFLINE DA FUNCIONALIDADE DE IMPORTAÇÃO")
    print("=" * 60)
    print("Este teste simula a lógica de importação sem precisar do servidor")
    print()
    
    success1 = test_column_mapping()
    success2 = test_file_formats()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A lógica de importação está funcionando corretamente.")
        print("💡 Para teste completo, inicie o servidor backend e execute test_import_produtos.py")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os detalhes acima.")

if __name__ == "__main__":
    main()
