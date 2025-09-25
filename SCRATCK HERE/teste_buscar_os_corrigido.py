#!/usr/bin/env python3
"""
Teste para verificar se o endpoint de buscar OS está retornando
os dados de cliente e equipamento corretamente após a correção.
"""

import requests
import json
import sys

def testar_buscar_os(numero_os):
    """Testa o endpoint de buscar OS"""
    
    url = f"http://localhost:8000/api/formulario/buscar-os/{numero_os}"
    
    print(f"🔍 Testando busca da OS: {numero_os}")
    print(f"📡 URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Resposta recebida com sucesso!")
            print("\n📋 Dados retornados:")
            print(f"   📋 Número da OS: {data.get('numero_os', 'N/A')}")
            print(f"   📊 Status OS: {data.get('status_os', 'N/A')}")
            print(f"   🏢 Cliente: {data.get('cliente', 'N/A')}")
            print(f"   ⚙️ Equipamento: {data.get('equipamento', 'N/A')}")
            print(f"   🔧 Tipo Máquina: {data.get('tipo_maquina', 'N/A')}")
            print(f"   ⏰ Horas Orçadas: {data.get('horas_orcadas', 'N/A')}")
            print(f"   🧪 Testes Exclusivo OS: {data.get('testes_exclusivo_os', 'N/A')}")
            print(f"   📍 Fonte: {data.get('fonte', 'N/A')}")
            
            # Verificar se os dados importantes estão presentes
            cliente = data.get('cliente', '')
            equipamento = data.get('equipamento', '')
            
            print("\n🔍 Verificação dos dados:")
            
            if cliente and cliente != 'Cliente não informado':
                print(f"   ✅ Cliente: OK - '{cliente}'")
            else:
                print(f"   ❌ Cliente: PROBLEMA - '{cliente}'")
            
            if equipamento and equipamento != 'Equipamento não informado':
                print(f"   ✅ Equipamento: OK - '{equipamento}'")
            else:
                print(f"   ❌ Equipamento: PROBLEMA - '{equipamento}'")
            
            print(f"\n📄 JSON completo:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            return True
            
        elif response.status_code == 404:
            print("❌ OS não encontrada (404)")
            print(f"📄 Resposta: {response.text}")
            return False
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        print(f"📄 Resposta bruta: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    
    print("🧪 TESTE DO ENDPOINT BUSCAR OS - CORREÇÃO DE CLIENTE E EQUIPAMENTO")
    print("=" * 70)
    
    # Lista de OSs para testar
    oss_para_testar = [
        "12345",
        "000012345",
        "12346",
        "16608"
    ]
    
    resultados = []
    
    for os_numero in oss_para_testar:
        print(f"\n{'='*20} TESTANDO OS {os_numero} {'='*20}")
        sucesso = testar_buscar_os(os_numero)
        resultados.append((os_numero, sucesso))
        print()
    
    # Resumo dos resultados
    print("📊 RESUMO DOS TESTES:")
    print("-" * 30)
    
    sucessos = 0
    for os_numero, sucesso in resultados:
        status = "✅ SUCESSO" if sucesso else "❌ FALHOU"
        print(f"   OS {os_numero}: {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\n📈 Total: {sucessos}/{len(resultados)} testes bem-sucedidos")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM! O problema foi corrigido.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
