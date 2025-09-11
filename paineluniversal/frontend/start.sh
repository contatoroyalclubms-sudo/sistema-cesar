#!/bin/sh

# Script de startup para Railway
echo "🚀 Iniciando Frontend no Railway..."

# Verificar variáveis de ambiente
echo "PORT: $PORT"
echo "NODE_ENV: $NODE_ENV"
echo "VITE_API_URL: $VITE_API_URL"

# Configurar porta dinâmica do Railway
if [ -n "$PORT" ]; then
    echo "📝 Configurando porta $PORT no nginx..."
    sed -i "s/listen 3000/listen $PORT/g" /etc/nginx/nginx.conf
fi

# Verificar se o build existe
if [ ! -d "/usr/share/nginx/html" ] || [ -z "$(ls -A /usr/share/nginx/html)" ]; then
    echo "❌ Erro: Diretório de build não encontrado ou vazio"
    exit 1
fi

echo "✅ Build encontrado, arquivos disponíveis:"
ls -la /usr/share/nginx/html/

# Verificar configuração do nginx
echo "🔧 Testando configuração do nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração do nginx válida"
    echo "🌟 Iniciando servidor nginx..."
    exec nginx -g 'daemon off;'
else
    echo "❌ Erro na configuração do nginx"
    exit 1
fi
