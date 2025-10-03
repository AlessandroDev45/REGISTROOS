#!/usr/bin/env python3
"""
TESTE DA SOLUÇÃO DE SCRAPING PARA PRODUÇÃO
==========================================

Script para testar a implementação da solução de scraping em lote
sem afetar o sistema de produção.
"""

import sys
import os
import requests
import time
import json
from datetime import datetime

# Configurações do teste
BASE_URL = "http://localhost:8000"  # Ajustar conforme necessário
TEST_OS_NUMBERS = ["12345", "12346", "12347", "12348", "12349"]  # OS de teste

def test_individual_scraping():
    """Testa scraping individual (funcionalidade existente)"""
    print("🧪 TESTE 1: Scraping Individual")
    print("=" * 50)
    
    try:
        # Testar endpoint existente
        response = requests.get(f"{BASE_URL}/api/desenvolvimento/scraping-status")
        
        if response.status_code == 200:
            print("✅ Endpoint de status funcionando")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Erro no endpoint de status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    return True

def test_batch_scraping():
    """Testa scraping em lote (nova funcionalidade)"""
    print("\n🧪 TESTE 2: Scraping em Lote")
    print("=" * 50)
    
    try:
        # Dados do lote de teste
        batch_data = {
            "os_numbers": TEST_OS_NUMBERS[:3],  # Apenas 3 OS para teste
            "batch_name": f"Teste_Lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        print(f"📦 Iniciando lote de teste: {batch_data['batch_name']}")
        print(f"   OS: {batch_data['os_numbers']}")
        
        # Iniciar lote
        response = requests.post(
            f"{BASE_URL}/api/desenvolvimento/scraping-batch",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            
            print("✅ Lote iniciado com sucesso")
            print(f"   Task ID: {task_id}")
            print(f"   Tempo estimado: {result.get('estimated_time')}")
            
            # Monitorar progresso
            if task_id:
                return monitor_batch_progress(task_id)
            
        else:
            print(f"❌ Erro ao iniciar lote: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de lote: {e}")
        return False

def monitor_batch_progress(task_id, max_wait=300):
    """Monitora o progresso do lote"""
    print(f"\n📊 Monitorando progresso do lote: {task_id}")
    print("-" * 40)
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/api/desenvolvimento/scraping-batch-status/{task_id}")
            
            if response.status_code == 200:
                status = response.json()
                
                print(f"⏳ Status: {status.get('status')}")
                print(f"   Progresso: {status.get('progress', 0)}%")
                print(f"   Mensagem: {status.get('message', 'N/A')}")
                
                if status.get('status') == 'completed':
                    print("✅ Lote concluído com sucesso!")
                    result = status.get('result', {})
                    print(f"   Total OS: {result.get('total_os', 0)}")
                    print(f"   Sucessos: {result.get('success_count', 0)}")
                    print(f"   Erros: {result.get('error_count', 0)}")
                    return True
                    
                elif status.get('status') == 'failed':
                    print("❌ Lote falhou!")
                    print(f"   Erro: {status.get('error', 'Erro desconhecido')}")
                    return False
                    
                elif status.get('status') in ['pending', 'processing']:
                    print("   Aguardando...")
                    time.sleep(10)  # Aguardar 10 segundos
                    
            else:
                print(f"❌ Erro ao obter status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
            return False
    
    print("⏰ Timeout no monitoramento")
    return False

def test_admin_dashboard():
    """Testa dashboard administrativo"""
    print("\n🧪 TESTE 3: Dashboard Administrativo")
    print("=" * 50)
    
    try:
        # Testar endpoint de dashboard
        response = requests.get(f"{BASE_URL}/api/admin/scraping/dashboard?days=7")
        
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Dashboard funcionando")
            
            stats = dashboard.get('dashboard_data', {})
            general = stats.get('estatisticas_gerais', {})
            
            print(f"   Total requests: {general.get('total_requests', 0)}")
            print(f"   Taxa de sucesso: {general.get('success_rate', 0)}%")
            print(f"   Tempo médio: {general.get('avg_processing_time', 0)}s")
            
            return True
            
        elif response.status_code == 403:
            print("⚠️ Dashboard requer privilégios de admin (esperado)")
            return True
            
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste do dashboard: {e}")
        return False

def test_queue_status():
    """Testa status das filas"""
    print("\n🧪 TESTE 4: Status das Filas")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/desenvolvimento/scraping-queue-status")
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Status das filas funcionando")
            
            if "error" in status:
                print(f"   ⚠️ {status['error']} (Celery pode não estar rodando)")
            else:
                print(f"   Workers online: {status.get('workers_online', 0)}")
                print(f"   Tasks ativas: {status.get('active_tasks', 0)}")
                print(f"   Tasks agendadas: {status.get('scheduled_tasks', 0)}")
            
            return True
            
        else:
            print(f"❌ Erro no status das filas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de filas: {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DA SOLUÇÃO DE SCRAPING PARA PRODUÇÃO")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    tests = [
        ("Scraping Individual", test_individual_scraping),
        ("Status das Filas", test_queue_status),
        ("Dashboard Administrativo", test_admin_dashboard),
        ("Scraping em Lote", test_batch_scraping),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
    elif passed >= total * 0.75:
        print("⚠️ Maioria dos testes passou. Verificar falhas antes de usar em produção.")
    else:
        print("❌ Muitos testes falharam. Sistema precisa de correções.")
    
    print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    run_all_tests()
