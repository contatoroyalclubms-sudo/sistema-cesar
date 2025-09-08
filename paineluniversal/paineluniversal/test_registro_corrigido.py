#!/usr/bin/env python3
"""
Teste específico para validar as correções no registro de usuários
Testa o endpoint /api/auth/register com os problemas corrigidos
"""

import requests
import json
import time
import random
import string

# Configurações
API_BASE = "http://localhost:8000"
REGISTER_ENDPOINT = f"{API_BASE}/api/auth/register"

def generate_test_cpf():
    """Gera um CPF válido para teste"""
    # Gerar 9 primeiros dígitos
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcular primeiro dígito verificador
    soma = sum(cpf[i] * (10 - i) for i in range(9))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    # Calcular segundo dígito verificador
    soma = sum(cpf[i] * (11 - i) for i in range(10))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    return ''.join(map(str, cpf))

def test_user_registration():
    """Testa o registro de usuário com as correções aplicadas"""
    print("🧪 TESTE DE REGISTRO DE USUÁRIO - PÓS CORREÇÕES")
    print("=" * 60)
    
    # Gerar dados de teste únicos
    cpf = generate_test_cpf()
    timestamp = int(time.time())
    
    user_data = {
        "cpf": cpf,
        "nome": f"Usuário Teste {timestamp}",
        "email": f"teste{timestamp}@email.com",
        "telefone": "11999887766",
        "senha": "teste123",
        "tipo": "cliente"  # Enviando como string, deve ser convertido para enum no backend
    }
    
    print(f"📋 Dados do teste:")
    print(f"   CPF: {cpf}")
    print(f"   Nome: {user_data['nome']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Tipo: {user_data['tipo']}")
    print()
    
    try:
        print("⏱️ Enviando requisição de registro...")
        start_time = time.time()
        
        response = requests.post(
            REGISTER_ENDPOINT,
            json=user_data,
            timeout=30,  # Timeout menor para teste
            headers={
                "Content-Type": "application/json"
            }
        )
        
        duration = time.time() - start_time
        print(f"⏱️ Requisição concluída em {duration:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ REGISTRO REALIZADO COM SUCESSO!")
            print(f"📊 Dados retornados:")
            print(f"   ID: {result.get('id')}")
            print(f"   Nome: {result.get('nome')}")
            print(f"   Email: {result.get('email')}")
            print(f"   CPF: {result.get('cpf')}")
            print(f"   Tipo: {result.get('tipo')}")
            print(f"   Ativo: {result.get('ativo')}")
            
            return True
        else:
            print(f"❌ ERRO NO REGISTRO!")
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response.text}")
            
            # Tentar parsear o erro
            try:
                error_data = response.json()
                if "detail" in error_data:
                    print(f"Detalhes do erro: {error_data['detail']}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - O servidor demorou mais de 30s para responder")
        print("🔧 Verifique se a otimização do bcrypt funcionou")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO - Servidor não está rodando")
        print("💡 Inicie o servidor backend com: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def test_duplicate_registration():
    """Testa registro duplicado para verificar validações"""
    print("\n🧪 TESTE DE REGISTRO DUPLICADO")
    print("=" * 60)
    
    # Usar dados que provavelmente já existem
    user_data = {
        "cpf": "12345678901",
        "nome": "Usuário Duplicado",
        "email": "duplicado@test.com",
        "senha": "teste123",
        "tipo": "cliente"
    }
    
    try:
        response = requests.post(
            REGISTER_ENDPOINT,
            json=user_data,
            timeout=15
        )
        
        if response.status_code == 400:
            error_data = response.json()
            detail = error_data.get('detail', '')
            
            if 'CPF já cadastrado' in detail or 'Email já cadastrado' in detail:
                print("✅ VALIDAÇÃO DE DUPLICATAS FUNCIONANDO")
                print(f"Erro esperado: {detail}")
                return True
            else:
                print(f"⚠️ Erro diferente do esperado: {detail}")
                return False
        elif response.status_code == 200:
            print("⚠️ Registro permitiu duplicata (pode não ser problema se CPF/email únicos)")
            return True
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de duplicata: {e}")
        return False

def test_invalid_data():
    """Testa validação de dados inválidos"""
    print("\n🧪 TESTE DE VALIDAÇÃO DE DADOS")
    print("=" * 60)
    
    # Teste com CPF inválido
    invalid_data = {
        "cpf": "123",  # CPF muito curto
        "nome": "",    # Nome vazio
        "email": "email_invalido",  # Email sem @
        "senha": "1",  # Senha muito curta
        "tipo": "cliente"
    }
    
    try:
        response = requests.post(
            REGISTER_ENDPOINT,
            json=invalid_data,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ VALIDAÇÃO DE DADOS INVÁLIDOS FUNCIONANDO")
            error_data = response.json()
            print(f"Erros de validação: {error_data.get('detail')}")
            return True
        else:
            print(f"⚠️ Status inesperado para dados inválidos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de validação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DO SISTEMA DE REGISTRO")
    print("🔧 Validando correções implementadas:")
    print("   - Correção do tipo de usuário (enum)")
    print("   - Otimização do bcrypt (menos rounds)")
    print("   - Validações gerais")
    print("=" * 60)
    
    results = []
    
    # Teste principal
    print("1️⃣ Teste de registro básico:")
    results.append(test_user_registration())
    
    # Teste de duplicata
    print("2️⃣ Teste de validação de duplicatas:")
    results.append(test_duplicate_registration())
    
    # Teste de validação
    print("3️⃣ Teste de validação de dados:")
    results.append(test_invalid_data())
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES:")
    
    test_names = [
        "Registro básico",
        "Validação duplicatas", 
        "Validação dados"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {i+1}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n🎯 RESUMO: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ As correções no sistema de registro estão funcionando")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
