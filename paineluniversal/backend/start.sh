#!/bin/bash

# Script de startup para Railway - Backend
echo "🚀 Iniciando Backend FastAPI no Railway..."

# Definir porta (Railway usa PORT, fallback para 8000)
export PORT=${PORT:-8000}

echo "📊 Configurações:"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." # Mostra apenas início da URL

# Verificar se o diretório app existe
if [ ! -d "/app/app" ]; then
    echo "❌ Erro: Diretório /app/app não encontrado"
    ls -la /app/
    exit 1
fi

echo "✅ Estrutura do projeto:"
ls -la /app/

# Aguardar um pouco para garantir que dependências estão prontas
echo "⏳ Aguardando inicialização..."
sleep 2

# Executar migração crítica tipo_usuario
echo "🔧 Executando migração crítica tipo_usuario..."
python migrations/deploy_with_migrations.py
