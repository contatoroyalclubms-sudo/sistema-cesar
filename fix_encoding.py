#!/usr/bin/env python3
"""
Script para corrigir problemas de encoding no arquivo estoque.py
"""

def fix_encoding_issues():
    file_path = "backend/app/routers/estoque.py"
    
    # Mapeamento de caracteres com problemas
    fixes = {
        'j�': 'já',
        'c�digo': 'código',
        'C�digo': 'Código',
        'transfer�ncia': 'transferência',
        'invent�rio': 'inventário',
        'op��o': 'opção',
        'transa��o': 'transação',
        'fun��o': 'função',
        '�': 'ó',
        '�': 'ã',
        '�': 'ç',
        '�': 'á',
        '�': 'é',
        '�': 'í',
        '�': 'õ',
        '�': 'ú'
    }
    
    try:
        # Tentar ler como UTF-8 primeiro
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Se falhar, tentar como latin-1
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Aplicar correções
    for wrong, correct in fixes.items():
        content = content.replace(wrong, correct)
    
    # Salvar como UTF-8
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Problemas de encoding corrigidos em estoque.py")

if __name__ == "__main__":
    fix_encoding_issues()
