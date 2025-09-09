#!/bin/bash
# Script de deploy automático para Railway
# Executa migrações necessárias

echo "🚀 Iniciando deploy automático..."

# 1. Executar migração completa (enum + tabela)
echo "📝 Executando migrações automáticas..."
python -c "
import sys
import os
sys.path.insert(0, 'backend')

try:
    from app.migrations.auto_migrate import run_auto_migration
    success = run_auto_migration()
    if success:
        print('✅ Migrações automáticas concluídas')
        sys.exit(0)
    else:
        print('❌ Erro nas migrações automáticas')
        sys.exit(1)
except Exception as e:
    print(f'❌ Erro fatal: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Migrações concluídas"
else
    echo "❌ Erro nas migrações"
    exit 1
fi

# 2. Verificar saúde do sistema
echo "🏥 Verificando saúde do sistema..."
python -c "
import sys
import os
sys.path.insert(0, 'backend')

try:
    from app.database import get_db
    from app.models import TipoUsuario
    from sqlalchemy import text
    
    # Testar conexão
    db = next(get_db())
    
    # Testar enum
    for value in ['admin', 'promoter', 'cliente']:
        result = db.execute(text(f\"SELECT '{value}'::tipousuario\"))
        assert result.scalar() == value
    
    print('✅ Conexão com banco OK')
    print(f'📋 Enum TipoUsuario: {[(e.name, e.value) for e in TipoUsuario]}')
    print('✅ Sistema validado e funcionando')
    
except Exception as e:
    print(f'❌ Erro na validação: {e}')
    sys.exit(1)
"

echo "🎉 Deploy automático concluído com sucesso!"
echo "🔧 Sistema pronto para registrar usuários admin!"
