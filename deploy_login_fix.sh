#!/bin/bash

echo "🚀 DEPLOY AUTOMÁTICO - CORREÇÃO SISTEMA DE LOGIN"
echo "================================================"

# 1. Verificar se estamos no diretório correto
if [ ! -f "auto_migrate_railway.py" ]; then
    echo "❌ Erro: auto_migrate_railway.py não encontrado!"
    echo "Execute este script do diretório backend/"
    exit 1
fi

# 2. Fazer commit das alterações
echo "📝 Commitando correções..."
cd ..  # Voltar para root do projeto

git add backend/auto_migrate_railway.py
git add backend/validate_post_deploy.py
git add backend/start.sh

# Verificar se há mudanças para commitar
if git diff --staged --quiet; then
    echo "ℹ️ Nenhuma mudança para commitar"
else
    git commit -m "🔧 Fix: Sistema de login - migração automática tipo_usuario

- Adiciona migração automática da coluna tipo_usuario no PostgreSQL
- Executa durante o deploy do Railway com segurança
- Inclui backup, rollback automático e validação
- Corrige erro 'column tipo_usuario does not exist'
- Mantém compatibilidade com funcionalidades existentes"
    
    echo "✅ Commit realizado com sucesso"
fi

# 3. Push para triggerar deploy automático
echo "🚀 Fazendo push para triggerar deploy..."
git push origin HEAD

echo ""
echo "🎯 DEPLOY INICIADO!"
echo "================================"
echo "✅ Migração automática configurada"
echo "✅ Validação pós-deploy incluída"
echo "✅ Sistema de login será corrigido"
echo ""
echo "📊 Acompanhe o deploy em:"
echo "   https://railway.app/"
echo ""
echo "📝 Logs esperados durante deploy:"
echo "   🔧 Executando migração crítica tipo_usuario..."
echo "   ✅ Migração da tabela usuarios concluída!"
echo "   🎯 Iniciando aplicação FastAPI..."
echo ""
echo "⏰ Tempo estimado: 2-3 minutos"
echo "🎉 Login funcionará após conclusão do deploy!"
