#!/usr/bin/env python3
"""
🧪 TESTE HTTP REAL - Simular produção
=====================================
Este teste simula exatamente o que acontece em produção:
requisições HTTP reais para o endpoint de registro.
"""

import asyncio
import httpx
import json
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"  # Assumindo que o servidor está rodando
ENDPOINT = f"{BASE_URL}/api/auth/register"

async def test_http_register():
    """Teste HTTP real do endpoint de registro"""
    print("🧪 TESTE HTTP REAL: Endpoint de registro")
    print("=" * 50)
    
    # Dados de teste
    timestamp = int(time.time())
    test_data = {
        "cpf": f"111{timestamp % 100000000:08d}",  # CPF único baseado no timestamp
        "nome": f"Teste HTTP {timestamp}",
        "email": f"http{timestamp}@teste.com",
        "telefone": "11999999999",
        "senha": "123456",
        "tipo": "cliente"
    }
    
    print(f"1️⃣ Dados de teste: {json.dumps(test_data, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"2️⃣ Fazendo requisição HTTP POST para: {ENDPOINT}")
            
            start_time = time.time()
            
            # Headers que o frontend enviaria
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "http://localhost:3000",  # Simular frontend
                "User-Agent": "Test-HTTP-Client/1.0"
            }
            
            response = await client.post(
                ENDPOINT,
                json=test_data,
                headers=headers
            )
            
            duration = time.time() - start_time
            
            print(f"3️⃣ Resposta recebida em {duration:.2f}s")
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sucesso! Usuário criado:")
                print(f"   ID: {result.get('id')}")
                print(f"   Nome: {result.get('nome')}")
                print(f"   Email: {result.get('email')}")
                print(f"   Tipo: {result.get('tipo')}")
                return True
            else:
                print(f"❌ Erro HTTP {response.status_code}:")
                try:
                    error_data = response.json()
                    print(f"   Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Texto: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ TIMEOUT: Requisição demorou mais de 30 segundos")
        return False
    except httpx.ConnectError:
        print("❌ ERRO DE CONEXÃO: Servidor não está rodando?")
        print("   Execute: uvicorn backend.app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

async def test_multiple_requests():
    """Teste com múltiplas requisições para detectar problemas de concorrência"""
    print("\n🔄 TESTE MÚLTIPLAS REQUISIÇÕES")
    print("=" * 50)
    
    tasks = []
    for i in range(3):
        print(f"📤 Criando requisição {i+1}/3...")
        tasks.append(test_http_register())
    
    print("⏳ Executando todas as requisições em paralelo...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successes = sum(1 for r in results if r is True)
    failures = len(results) - successes
    
    print(f"\n📊 RESULTADOS:")
    print(f"   ✅ Sucessos: {successes}")
    print(f"   ❌ Falhas: {failures}")
    
    if failures > 0:
        print("\n🔍 PROBLEMAS DETECTADOS:")
        for i, result in enumerate(results):
            if result is not True:
                print(f"   Requisição {i+1}: {result}")

async def test_malformed_data():
    """Teste com dados inválidos para verificar validation handlers"""
    print("\n🚨 TESTE DADOS INVÁLIDOS")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "CPF inválido",
            "data": {"cpf": "123", "nome": "Teste", "email": "test@test.com", "senha": "123456"}
        },
        {
            "name": "Email inválido", 
            "data": {"cpf": "12345678901", "nome": "Teste", "email": "email_invalido", "senha": "123456"}
        },
        {
            "name": "Campo obrigatório faltando",
            "data": {"cpf": "12345678901", "email": "test@test.com", "senha": "123456"}  # sem nome
        },
        {
            "name": "Senha muito curta",
            "data": {"cpf": "12345678901", "nome": "Teste", "email": "test@test.com", "senha": "12"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for test_case in test_cases:
            print(f"\n🧪 Testando: {test_case['name']}")
            
            try:
                response = await client.post(
                    ENDPOINT,
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 422:
                    print("   ✅ Validação funcionando corretamente")
                    try:
                        error_details = response.json()
                        print(f"   📝 Detalhes: {error_details.get('message', 'N/A')}")
                    except:
                        pass
                else:
                    print(f"   ⚠️ Status inesperado: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")

async def main():
    """Função principal do teste"""
    print("🚀 INICIANDO TESTES HTTP DE REGISTRO")
    print("=" * 60)
    print(f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL Base: {BASE_URL}")
    print("=" * 60)
    
    # Teste básico
    success = await test_http_register()
    
    if success:
        # Se o teste básico passou, fazer testes adicionais
        await test_multiple_requests()
        await test_malformed_data()
    else:
        print("\n⚠️ Teste básico falhou. Verifique se o servidor está rodando.")
        print("   Comando: uvicorn backend.app.main:app --reload")
    
    print("\n🎯 ANÁLISE PARA PRODUÇÃO:")
    print("=" * 60)
    print("✅ Se todos os testes passaram: problema é específico do ambiente de produção")
    print("❌ Se algum teste falhou: há problema no código/middleware/handlers")
    print("🔍 Próximos passos: comparar logs entre local e produção")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
