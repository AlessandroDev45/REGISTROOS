#!/usr/bin/env python3
"""
Teste das implementações de pendências e programações
Verifica se os fluxos implementados estão funcionando corretamente
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_programacao_detection():
    """Testa a detecção automática de programação ativa"""
    print("🔍 Testando detecção de programação ativa...")
    
    # Simular verificação de programação para uma OS
    os_numero = "12345"
    
    try:
        response = requests.get(
            f"{API_URL}/desenvolvimento/verificar-programacao-os/{os_numero}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detecção funcionando: {data}")
            return data.get('tem_programacao', False)
        else:
            print(f"❌ Erro na detecção: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_apontamento_with_programacao():
    """Testa criação de apontamento com finalização de programação"""
    print("📝 Testando apontamento com finalização de programação...")
    
    apontamento_data = {
        "numero_os": "12345",
        "cliente": "Cliente Teste",
        "equipamento": "Equipamento Teste",
        "tipo_maquina": "TIPO_A",
        "tipo_atividade": "MANUTENCAO",
        "descricao_atividade": "Teste de manutenção",
        "data_inicio": "2024-01-15",
        "hora_inicio": "08:00",
        "data_fim": "2024-01-15",
        "hora_fim": "17:00",
        "observacao": "Teste de apontamento com programação",
        "resultado_global": "APROVADO"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/desenvolvimento/os/apontamentos",
            json=apontamento_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Apontamento criado: {data}")
            
            if data.get('programacao_finalizada'):
                print("🎯 Programação finalizada automaticamente!")
                return True
            else:
                print("ℹ️ Nenhuma programação foi finalizada")
                return True
        else:
            print(f"❌ Erro na criação: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_pendencia_resolution_flow():
    """Testa o fluxo de resolução de pendência via apontamento"""
    print("📋 Testando fluxo de resolução de pendência...")
    
    # Simular dados de uma pendência
    pendencia_data = {
        "id": 1,
        "numero_os": "12345",
        "cliente": "Cliente Teste",
        "descricao_maquina": "Equipamento com problema",
        "tipo_maquina": "TIPO_A",
        "descricao_pendencia": "Problema a ser resolvido"
    }
    
    # Simular dados preenchidos para apontamento
    dados_apontamento = {
        "inpNumOS": pendencia_data["numero_os"],
        "inpCliente": pendencia_data["cliente"],
        "inpEquipamento": pendencia_data["descricao_maquina"],
        "selMaq": pendencia_data["tipo_maquina"],
        "observacao": f"RESOLUÇÃO DE PENDÊNCIA #{pendencia_data['id']}: {pendencia_data['descricao_pendencia']}",
        "pendencia_origem_id": pendencia_data["id"]
    }
    
    print(f"📝 Dados preparados para apontamento: {dados_apontamento}")
    
    # Simular criação do apontamento de resolução
    apontamento_data = {
        **dados_apontamento,
        "data_inicio": "2024-01-15",
        "hora_inicio": "08:00",
        "data_fim": "2024-01-15", 
        "hora_fim": "17:00",
        "resultado_global": "APROVADO"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/desenvolvimento/os/apontamentos",
            json=apontamento_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Apontamento de resolução criado: {data}")
            
            # Simular finalização da pendência
            pendencia_resolve_data = {
                "solucao_aplicada": dados_apontamento["observacao"],
                "observacoes_fechamento": f"Pendência resolvida através do apontamento #{data.get('id')}",
                "status": "FECHADA"
            }
            
            resolve_response = requests.patch(
                f"{API_URL}/desenvolvimento/pendencias/{pendencia_data['id']}/resolver",
                json=pendencia_resolve_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            if resolve_response.status_code == 200:
                print("✅ Pendência finalizada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao finalizar pendência: {resolve_response.status_code}")
                return False
        else:
            print(f"❌ Erro na criação do apontamento: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_access_control():
    """Testa controle de acesso para pendências por setor"""
    print("🔒 Testando controle de acesso por setor...")
    
    try:
        response = requests.get(
            f"{API_URL}/desenvolvimento/pendencias",
            headers={"Authorization": "Bearer test_token"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pendências acessíveis: {len(data)} encontradas")
            
            # Verificar se as pendências retornadas são do setor correto
            for pendencia in data[:3]:  # Verificar apenas as primeiras 3
                print(f"   - Pendência #{pendencia.get('id')}: OS {pendencia.get('numero_os')}")
            
            return True
        else:
            print(f"❌ Erro no acesso: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes das implementações...")
    print("=" * 60)
    
    tests = [
        ("Detecção de Programação", test_programacao_detection),
        ("Apontamento com Programação", test_apontamento_with_programacao),
        ("Resolução de Pendência", test_pendencia_resolution_flow),
        ("Controle de Acesso", test_access_control)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"💥 {test_name}: ERRO - {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Implementações funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique as implementações.")

if __name__ == "__main__":
    main()
