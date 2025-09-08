#!/usr/bin/env python3
"""
Teste de performance do registro de usuário após otimizações
"""
import requests
import time
import json
import threading
from datetime import datetime

# URL do backend
API_BASE = "https://backend-painel-universal-production.up.railway.app"

def test_register_performance():
    """Testar performance do registro com as otimizações"""
    print("🚀 TESTE DE PERFORMANCE - Registro de Usuário Otimizado")
    print("=" * 70)
    
    # Dados de teste únicos
    timestamp = str(int(time.time()))[-6:]
    
    user_data = {
        "cpf": f"12345678{timestamp[-3:]}",  # CPF único
        "nome": f"Usuário Teste {timestamp}",
        "email": f"teste{timestamp}@performance.com",
        "telefone": "11999999999",
        "senha": "senha123",
        "tipo": "cliente"
    }
    
    print(f"📝 Dados de teste:")
    print(f"  - CPF: {user_data['cpf']}")
    print(f"  - Nome: {user_data['nome']}")
    print(f"  - Email: {user_data['email']}")
    print()
    
    try:
        print("⏱️ Iniciando teste de performance...")
        start_time = time.time()
        
        # Fazer requisição com timeout maior
        response = requests.post(
            f"{API_BASE}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutos para teste
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"📊 Resultado do teste:")
        print(f"  - Status: {response.status_code}")
        print(f"  - Tempo total: {duration:.2f}s")
        print(f"  - Performance: {'✅ EXCELENTE' if duration < 5 else '⚡ BOA' if duration < 15 else '⚠️ MELHORÁVEL'}")
        
        if response.status_code == 200:
            print("✅ Registro bem-sucedido!")
            user_response = response.json()
            print(f"📱 Usuário criado:")
            print(f"  - ID: {user_response.get('id')}")
            print(f"  - Nome: {user_response.get('nome')}")
            print(f"  - Email: {user_response.get('email')}")
            
            # Benchmark de performance
            if duration < 5:
                print("🎉 OTIMIZAÇÃO FUNCIONOU! Registro muito rápido!")
            elif duration < 15:
                print("✅ Otimização efetiva. Performance aceitável.")
            elif duration < 30:
                print("⚠️ Performance melhorou, mas ainda pode ser otimizada.")
            else:
                print("❌ Performance ainda problemática.")
                
        else:
            print(f"❌ Erro no registro: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📱 Erro detalhado: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📱 Resposta texto: {response.text}")
        
        return duration
                
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"⏰ TIMEOUT após {duration:.2f}s")
        print("❌ Ainda há problemas de performance")
        return duration
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Verifique se o backend está acessível")
        return None
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Erro geral após {duration:.2f}s: {e}")
        return duration

def test_multiple_registrations():
    """Teste com múltiplos registros para simular carga"""
    print("\n🔥 TESTE DE CARGA - Múltiplos Registros")
    print("=" * 50)
    
    num_tests = 3
    results = []
    
    def register_user(index):
        timestamp = str(int(time.time() * 1000))[-8:]  # Timestamp mais único
        
        user_data = {
            "cpf": f"987654{index:03d}{timestamp[-2:]}",
            "nome": f"Teste Carga {index}",
            "email": f"carga{index}_{timestamp}@teste.com",
            "telefone": "11999999999",
            "senha": "senha123",
            "tipo": "cliente"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            results.append({
                'index': index,
                'duration': duration,
                'status': response.status_code,
                'success': response.status_code == 200
            })
            
            print(f"✅ Usuário {index}: {duration:.2f}s (Status: {response.status_code})")
            
        except Exception as e:
            duration = time.time() - start_time
            results.append({
                'index': index,
                'duration': duration,
                'status': 'ERROR',
                'success': False,
                'error': str(e)
            })
            print(f"❌ Usuário {index}: {duration:.2f}s - Erro: {e}")
    
    # Executar testes em paralelo
    threads = []
    for i in range(num_tests):
        thread = threading.Thread(target=register_user, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Pequeno delay entre inicializações
    
    # Aguardar todos os threads
    for thread in threads:
        thread.join()
    
    # Analisar resultados
    if results:
        successful = [r for r in results if r['success']]
        avg_duration = sum(r['duration'] for r in results) / len(results)
        success_rate = len(successful) / len(results) * 100
        
        print(f"\n📊 Resumo do teste de carga:")
        print(f"  - Registros testados: {len(results)}")
        print(f"  - Taxa de sucesso: {success_rate:.1f}%")
        print(f"  - Tempo médio: {avg_duration:.2f}s")
        
        if successful:
            fastest = min(r['duration'] for r in successful)
            slowest = max(r['duration'] for r in successful)
            print(f"  - Mais rápido: {fastest:.2f}s")
            print(f"  - Mais lento: {slowest:.2f}s")
    
    return results

if __name__ == "__main__":
    print(f"🕐 Teste iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Teste individual
    duration = test_register_performance()
    
    # Teste de carga se o individual funcionou
    if duration and duration < 60:
        test_multiple_registrations()
    else:
        print("\n⚠️ Pulando teste de carga devido a problemas no teste individual")
    
    print(f"\n🕐 Teste concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 RELATÓRIO:")
    print("- Se os tempos estão < 5s: Otimização EXCELENTE ✅")
    print("- Se os tempos estão < 15s: Otimização BOA ⚡")
    print("- Se os tempos estão > 30s: Ainda precisa melhorar ⚠️")
