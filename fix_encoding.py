import os
import codecs

# Corrigir encoding de todos os arquivos Python
routers_dir = "app/routers"

for filename in os.listdir(routers_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(routers_dir, filename)
        print(f"Processando {filepath}...")

        try:
            # Tentar ler com diferentes encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except:
                    continue

            if content:
                # Remover caracteres problemáticos
                content = content.replace('�', 'o')
                content = content.replace('ó', 'o')
                content = content.replace('ã', 'a')
                content = content.replace('ç', 'c')
                content = content.replace('õ', 'o')
                content = content.replace('ê', 'e')
                content = content.replace('á', 'a')
                content = content.replace('é', 'e')
                content = content.replace('í', 'i')
                content = content.replace('ú', 'u')

                # Salvar com UTF-8
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  OK - Corrigido!")
        except Exception as e:
            print(f"  ERRO: {e}")

print("\nTodos os arquivos foram processados!")