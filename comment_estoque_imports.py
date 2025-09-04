#!/usr/bin/env python3
"""
Script para comentar TODOS os imports relacionados a estoque
"""

import os
import re

def comment_estoque_imports():
    files_to_check = [
        "backend/app/main.py",
        "backend/app/routers/__init__.py",
        "backend/app/schemas_extended.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comentar imports de estoque
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if ('estoque' in line.lower() or 'Estoque' in line) and ('import' in line or 'from' in line):
                    if not line.strip().startswith('#'):
                        indentation = len(line) - len(line.lstrip())
                        new_lines.append(' ' * indentation + '# ' + line.strip() + '  # COMENTADO - ESTOQUE')
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Imports de estoque comentados em {file_path}")

if __name__ == "__main__":
    comment_estoque_imports()
