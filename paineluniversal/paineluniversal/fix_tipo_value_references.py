#!/usr/bin/env python3
"""
Script para corrigir todas as referências incorretas a 'tipo.value' 
no código backend, substituindo por apenas 'tipo'
"""

import os
import re
from pathlib import Path

def fix_tipo_value_references():
    """Corrige todas as referências a usuario.tipo.value no backend"""
    
    backend_path = Path("backend/app")
    
    # Padrões a serem corrigidos
    patterns_to_fix = [
        (r'usuario_atual\.tipo\.value', 'usuario_atual.tipo'),
        (r'usuario\.tipo\.value', 'usuario.tipo'),
        (r'row\.tipo\.value', 'row.tipo'),
        (r'mov\.tipo\.value', 'mov.tipo'),
    ]
    
    # Arquivos para ignorar (se necessário)
    ignore_files = []
    
    total_fixes = 0
    
    # Buscar arquivos Python no backend
    for py_file in backend_path.rglob("*.py"):
        if py_file.name in ignore_files:
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixes = 0
            
            # Aplicar cada padrão de correção
            for pattern, replacement in patterns_to_fix:
                before_count = len(re.findall(pattern, content))
                content = re.sub(pattern, replacement, content)
                after_count = len(re.findall(pattern, content))
                fixes_made = before_count - after_count
                file_fixes += fixes_made
                
                if fixes_made > 0:
                    print(f"✅ {py_file}: {fixes_made} correções para '{pattern}'")
            
            # Salvar arquivo se houve mudanças
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                total_fixes += file_fixes
                print(f"💾 Salvo: {py_file} ({file_fixes} correções)")
                
        except Exception as e:
            print(f"❌ Erro ao processar {py_file}: {e}")
    
    print(f"\n🎉 Correção concluída! Total de correções: {total_fixes}")
    return total_fixes

if __name__ == "__main__":
    print("🔧 Iniciando correção de referências tipo.value...")
    fixes = fix_tipo_value_references()
    
    if fixes > 0:
        print("⚠️  IMPORTANTE: Reinicie o servidor backend para aplicar as mudanças!")
    else:
        print("ℹ️  Nenhuma correção necessária.")
