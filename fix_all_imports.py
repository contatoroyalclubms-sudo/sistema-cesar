import os
import re

def fix_imports():
    # Corrige imports em todos os arquivos de routers
    routers_dir = "app/routers"
    
    for filename in os.listdir(routers_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(routers_dir, filename)
            print(f"Processando {filepath}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Corrige os imports
            content = content.replace("from app.database", "from database")
            content = content.replace("from app.models", "from models")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  OK - {filename} corrigido!")
    
    print("\nTodos os arquivos foram corrigidos!")

if __name__ == "__main__":
    fix_imports()