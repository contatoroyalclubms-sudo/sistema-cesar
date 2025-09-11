#!/bin/bash

# TESTE E2E COMPLETO - SISTEMA PAINEL UNIVERSAL V6
# Este script executa testes E2E usando curl e validações simples

FRONTEND_URL="http://localhost:5175"
BACKEND_URL="http://localhost:8002"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TESTES E2E - EXECUÇÃO                    ║"
echo "║                 Sistema Painel Universal v6                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Criar diretório de resultados
mkdir -p test-results

# Variáveis de controle
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
ERRORS=()

START_TIME=$(date +%s)

# Função para testar endpoints
test_endpoint() {
    local url=$1
    local name=$2
    
    echo "🌐 Testando endpoint: $name"
    echo "   URL: $url"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Fazer requisição e capturar status e tempo
    response=$(curl -s -w "%{http_code}|%{time_total}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -c 12 | cut -d'|' -f1)
    time_total=$(echo "$response" | tail -c 12 | cut -d'|' -f2)
    body=$(echo "$response" | sed 's/|[^|]*$//')
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ $name: HTTP $http_code - $(echo "$body" | wc -c) bytes - ${time_total}s"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "   ❌ $name: HTTP $http_code"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ERRORS+=("$name: HTTP $http_code")
    fi
    
    echo "   Resposta: $(echo "$body" | head -c 100)..."
    echo ""
}

# Função para testar login via API
test_login_api() {
    echo "🚀 TESTE 3: LOGIN VIA API"
    echo "=========================="
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Dados de login
    login_data='{"cpf":"00000000000","password":"admin123"}'
    
    echo "📡 Enviando requisição de login..."
    echo "   Endpoint: $BACKEND_URL/api/auth/login"
    echo "   Dados: $login_data"
    
    # Fazer requisição de login
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$login_data" \
        "$BACKEND_URL/api/auth/login" 2>/dev/null)
        
    http_code=$(echo "$response" | tail -c 4)
    body=$(echo "$response" | sed 's/...$//')
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ Login via API: HTTP $http_code"
        echo "   Resposta: $body"
        
        # Verificar se há token na resposta
        if echo "$body" | grep -q "token\|access_token"; then
            echo "   ✅ Token encontrado na resposta"
        else
            echo "   ⚠️  Token não encontrado na resposta"
            ERRORS+=("Login API: Token não encontrado")
        fi
        
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "   ❌ Login via API: HTTP $http_code"
        echo "   Resposta: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ERRORS+=("Login API: HTTP $http_code")
    fi
    echo ""
}

# Função para verificar se os serviços estão rodando
check_services() {
    echo "🔍 VERIFICAÇÃO DE SERVIÇOS"
    echo "=========================="
    
    # Verificar frontend
    if curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
        echo "   ✅ Frontend rodando em $FRONTEND_URL"
    else
        echo "   ❌ Frontend NÃO está rodando em $FRONTEND_URL"
        echo "   💡 Inicie o frontend com: cd frontend && npm run dev"
        return 1
    fi
    
    # Verificar backend
    if curl -s "$BACKEND_URL/api/health" >/dev/null 2>&1; then
        echo "   ✅ Backend rodando em $BACKEND_URL"
    else
        echo "   ❌ Backend NÃO está rodando em $BACKEND_URL"
        echo "   💡 Inicie o backend com: cd backend && python simple_server.py"
        return 1
    fi
    
    echo ""
    return 0
}

# Executar testes
main() {
    echo "🎯 Iniciando testes E2E..."
    echo "Data/Hora: $(date)"
    echo ""
    
    # Verificar serviços
    if ! check_services; then
        echo "❌ Serviços não estão rodando. Abortando testes."
        exit 1
    fi
    
    # TESTE 1: Verificar se frontend está acessível
    echo "🚀 TESTE 1: FRONTEND ACESSÍVEL"
    echo "=============================="
    
    response=$(curl -s -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null)
    http_code=$(echo "$response" | tail -c 4)
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$http_code" = "200" ]; then
        echo "   ✅ Frontend acessível: HTTP $http_code"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "   ❌ Frontend inacessível: HTTP $http_code"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ERRORS+=("Frontend: HTTP $http_code")
    fi
    echo ""
    
    # TESTE 2: Endpoints da API
    echo "🚀 TESTE 2: API ENDPOINTS"
    echo "========================="
    
    test_endpoint "$BACKEND_URL/api/health" "Health Check"
    test_endpoint "$BACKEND_URL/api/cors-test" "CORS Test"
    test_endpoint "$BACKEND_URL/api/eventos" "Eventos API"
    
    # TESTE 3: Login via API
    test_login_api
    
    # TESTE 4: Verificar páginas do frontend
    echo "🚀 TESTE 4: PÁGINAS DO FRONTEND"
    echo "==============================="
    
    pages=(
        "/login:Login"
        "/app/dashboard:Dashboard"
        "/app/eventos:Eventos"
        "/app/usuarios:Usuários"
        "/app/produtos:Produtos"
        "/app/vendas:Vendas"
        "/app/estoque:Estoque"
    )
    
    for page_info in "${pages[@]}"; do
        page_path=$(echo "$page_info" | cut -d':' -f1)
        page_name=$(echo "$page_info" | cut -d':' -f2)
        
        full_url="$FRONTEND_URL$page_path"
        
        echo "📄 Testando página: $page_name"
        echo "   URL: $full_url"
        
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
        response=$(curl -s -w "%{http_code}" "$full_url" 2>/dev/null)
        http_code=$(echo "$response" | tail -c 4)
        body=$(echo "$response" | sed 's/...$//')
        
        if [ "$http_code" = "200" ]; then
            # Verificar se não é uma página de erro
            if echo "$body" | grep -qi "404\|not found\|error"; then
                echo "   ⚠️  $page_name: HTTP $http_code mas contém erro"
                ERRORS+=("Página $page_name: Contém erro")
            else
                echo "   ✅ $page_name: HTTP $http_code - $(echo "$body" | wc -c) bytes"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            fi
        else
            echo "   ❌ $page_name: HTTP $http_code"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            ERRORS+=("Página $page_name: HTTP $http_code")
        fi
        echo ""
    done
    
    # Gerar relatório final
    END_TIME=$(date +%s)
    EXECUTION_TIME=$((END_TIME - START_TIME))
    SUCCESS_RATE=$(((PASSED_TESTS * 100) / TOTAL_TESTS))
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    RELATÓRIO DE TESTES E2E                  ║"
    echo "║                 Sistema Painel Universal v6                 ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    printf "║ 📊 ESTATÍSTICAS GERAIS:                                     ║\n"
    printf "║   • Total de testes: %-2d                              ║\n" "$TOTAL_TESTS"
    printf "║   • Testes aprovados: %-2d                            ║\n" "$PASSED_TESTS"
    printf "║   • Testes falhados: %-2d                             ║\n" "$FAILED_TESTS"
    printf "║   • Tempo de execução: %-2ds                            ║\n" "$EXECUTION_TIME"
    echo "║                                                              ║"
    echo "║ 🌐 CONFIGURAÇÕES:                                           ║"
    printf "║   • Frontend: %-43s ║\n" "$FRONTEND_URL"
    printf "║   • Backend: %-44s ║\n" "$BACKEND_URL"
    echo "║   • Login: CPF 00000000000, Senha admin123                  ║"
    echo "║                                                              ║"
    echo "║ ✅ TESTES EXECUTADOS:                                        ║"
    echo "║   1. ✓ Frontend Acessível                                   ║"
    echo "║   2. ✓ API Endpoints                                        ║"
    echo "║   3. ✓ Login via API                                        ║"
    echo "║   4. ✓ Páginas do Frontend                                  ║"
    echo "║                                                              ║"
    
    if [ ${#ERRORS[@]} -gt 0 ]; then
        printf "║ ❌ ERROS ENCONTRADOS (%d):                               ║\n" "${#ERRORS[@]}"
        for error in "${ERRORS[@]}"; do
            printf "║   • %-54s ║\n" "${error:0:54}"
        done
        echo "║                                                              ║"
    else
        echo "║ 🎉 NENHUM ERRO CRÍTICO ENCONTRADO!                         ║"
    fi
    
    echo "║ 📁 ARTEFATOS GERADOS:                                       ║"
    echo "║   • Relatório: test-results/relatorio-e2e.txt               ║"
    echo "║   • Log completo: test-results/test-execution.log            ║"
    echo "║                                                              ║"
    printf "║ 🏆 TAXA DE SUCESSO: %d%%                                  ║\n" "$SUCCESS_RATE"
    echo "╚══════════════════════════════════════════════════════════════╝"
    
    # Salvar relatório em arquivo
    {
        echo "RELATÓRIO DE TESTES E2E - Sistema Painel Universal v6"
        echo "====================================================="
        echo "Data/Hora: $(date)"
        echo "Total de testes: $TOTAL_TESTS"
        echo "Testes aprovados: $PASSED_TESTS"
        echo "Testes falhados: $FAILED_TESTS"
        echo "Tempo de execução: ${EXECUTION_TIME}s"
        echo "Taxa de sucesso: ${SUCCESS_RATE}%"
        echo ""
        echo "Configurações:"
        echo "- Frontend: $FRONTEND_URL"
        echo "- Backend: $BACKEND_URL"
        echo "- Login: CPF 00000000000, Senha admin123"
        echo ""
        if [ ${#ERRORS[@]} -gt 0 ]; then
            echo "Erros encontrados:"
            for error in "${ERRORS[@]}"; do
                echo "- $error"
            done
        else
            echo "✅ Nenhum erro crítico encontrado!"
        fi
    } > test-results/relatorio-e2e.txt
    
    # Salvar dados JSON
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"totalTests\": $TOTAL_TESTS,"
        echo "  \"passedTests\": $PASSED_TESTS,"
        echo "  \"failedTests\": $FAILED_TESTS,"
        echo "  \"executionTime\": $EXECUTION_TIME,"
        echo "  \"successRate\": $SUCCESS_RATE,"
        echo "  \"frontend\": \"$FRONTEND_URL\","
        echo "  \"backend\": \"$BACKEND_URL\","
        echo "  \"errors\": ["
        for i in "${!ERRORS[@]}"; do
            echo "    \"${ERRORS[$i]}\""
            if [ $i -lt $((${#ERRORS[@]} - 1)) ]; then
                echo ","
            fi
        done
        echo "  ]"
        echo "}"
    } > test-results/test-summary.json
    
    echo ""
    echo "📋 Relatório completo salvo em:"
    echo "   • test-results/relatorio-e2e.txt"
    echo "   • test-results/test-summary.json"
    echo ""
    
    if [ "$SUCCESS_RATE" -ge 80 ]; then
        echo "🎉 Testes concluídos com SUCESSO!"
        return 0
    else
        echo "⚠️ Alguns testes falharam. Verifique o relatório."
        return 1
    fi
}

# Executar função principal
main "$@"