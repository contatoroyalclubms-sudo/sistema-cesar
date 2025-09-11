# Temporário - Fix para imports dos modelos MEEP
with open('app/models.py', 'a', encoding='utf-8') as f:
    f.write('\n\n# ==================== IMPORTAR MODELOS MEEP COMPLETOS ====================\n')
    f.write('# Import all additional MEEP models to make them available through main models module\n')
    f.write('from .models_meep_complete import *\n')
    
print("Modelos MEEP importados para models.py")