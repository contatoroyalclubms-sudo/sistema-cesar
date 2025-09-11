#!/usr/bin/env python3
"""
Teste específico para verificar se a correção do schema resolveu o timeout de registro
"""
import sys
import os
import time
import requests
import json

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_register_schema():
    print("🔧 TESTE: API de registro com schema corrigido")
    print("=" * 50)
    
    # URL base da API
    base_url = "http://localhost:8001"
    
    try:
        print("1️⃣ Verificando se API está rodando...")
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"✅ API respondeu: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ API não está rodando. Iniciando servidor...")
            # Não vamos iniciar automaticamente, apenas informar
            print("💡 Execute: uvicorn backend.app.main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
        
        print("2️⃣ Testando endpoint de registro...")
        
        # Dados de teste
        test_time = int(time.time())
        user_data = {
            "nome": f"Teste Schema {test_time}",
            "email": f"schema{test_time}@teste.com",
            "cpf": f"111{test_time}"[-11:],  # CPF único
            "telefone": "11999999999",
            "senha": "123456",
            "tipo": "CLIENTE"
        }
        
        print(f"3️⃣ Enviando dados: {json.dumps(user_data, indent=2)}")
        
        # Teste com timeout maior para capturar o erro específico
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/auth/register",
                json=user_data,
                timeout=30  # Timeout de 30s para detectar o problema
            )
            end_time = time.time()
            
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Registro bem-sucedido!")
                print(f"📋 Resposta: {json.dumps(result, indent=2, default=str)}")
                
                # Verificar se todos os campos estão presentes
                expected_fields = ['id', 'cpf', 'nome', 'email', 'telefone', 'tipo', 'ativo', 'ultimo_login', 'criado_em', 'atualizado_em']
                missing_fields = [field for field in expected_fields if field not in result]
                
                if missing_fields:
                    print(f"⚠️ Campos faltando na resposta: {missing_fields}")
                else:
                    print("✅ Todos os campos presentes na resposta!")
                
                return True
            else:
                print(f"❌ Erro no registro: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"📝 Detalhes: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"📝 Resposta: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            print(f"⏱️ TIMEOUT após {end_time - start_time:.2f}s")
            print("❌ O problema de timeout ainda persiste!")
            return False
        except Exception as e:
            end_time = time.time()
            print(f"⏱️ Tempo antes do erro: {end_time - start_time:.2f}s")
            print(f"❌ Erro na requisição: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_register_schema()
    if success:
        print("\n🎉 Schema corrigido - API de registro funcionando!")
    else:
        print("\n❌ Ainda há problemas na API de registro!")
