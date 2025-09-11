#!/usr/bin/env python3
"""
Script para corrigir duplicações de tabelas no models_cashless.py
"""

def fix_duplicate_tables():
    file_path = "backend/app/models_cashless.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar classes duplicadas
    class_definitions = {}
    new_lines = []
    skip_until_next_class = False
    current_class = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('class ') and line.strip().endswith('(Base):'):
            class_name = line.split('class ')[1].split('(')[0].strip()
            
            if class_name in class_definitions:
                print(f"⚠️  Classe duplicada encontrada: {class_name} na linha {i+1}")
                skip_until_next_class = True
                current_class = class_name
                continue
            else:
                class_definitions[class_name] = i
                skip_until_next_class = False
                current_class = class_name
        
        elif skip_until_next_class:
            # Pular linha se estamos ignorando uma classe duplicada
            if line.strip().startswith('class ') and line.strip().endswith('(Base):'):
                # Nova classe encontrada, parar de pular
                skip_until_next_class = False
                class_name = line.split('class ')[1].split('(')[0].strip()
                if class_name not in class_definitions:
                    class_definitions[class_name] = len(new_lines)
                    current_class = class_name
                    new_lines.append(line)
                else:
                    skip_until_next_class = True
            continue
        
        new_lines.append(line)
    
    # Escrever arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Duplicações removidas de models_cashless.py")
    print(f"📝 Classes mantidas: {list(class_definitions.keys())}")

if __name__ == "__main__":
    fix_duplicate_tables()
