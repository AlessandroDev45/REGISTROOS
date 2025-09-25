#!/usr/bin/env python3
"""
Teste completo para verificar se a OS 12345 está funcionando corretamente
"""

import requests
import json

def testar_endpoints():
    """Testa todos os endpoints necessários para o funcionamento da OS 12345"""
    
    print("🧪 TESTE COMPLETO - OS 12345")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Testar endpoint de busca da OS
    print("\n1️⃣ TESTANDO BUSCA DA OS 12345")
    try:
        response = requests.get(f"{base_url}/api/formulario/os/12345", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ OS encontrada!")
            print(f"   📋 Número: {data.get('numero_os')}")
            print(f"   📊 Status: {data.get('status')}")
            print(f"   🏢 Cliente: {data.get('cliente')}")
            print(f"   ⚙️ Equipamento: {data.get('equipamento')}")
            print(f"   🔧 Tipo Máquina: {data.get('tipo_maquina')}")
            
            # Verificar se está bloqueada
            status_finalizados = [
                'RECUSADA - CONFERIDA',
                'TERMINADA - CONFERIDA', 
                'TERMINADA - EXPEDIDA',
                'OS CANCELADA'
            ]
            status_atual = data.get('status', '')
            bloqueada = status_atual in status_finalizados
            print(f"   🚫 Bloqueada para apontamento: {'SIM' if bloqueada else 'NÃO'}")
            
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 2. Testar endpoint de tipos de máquina
    print("\n2️⃣ TESTANDO TIPOS DE MÁQUINA")
    try:
        response = requests.get(f"{base_url}/api/formulario/tipos-maquina", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} tipos de máquina encontrados")
            if data:
                print(f"   📄 Primeiro item: {data[0]}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 3. Testar endpoint de tipos de atividade
    print("\n3️⃣ TESTANDO TIPOS DE ATIVIDADE")
    try:
        response = requests.get(f"{base_url}/api/formulario/tipos-atividade", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} tipos de atividade encontrados")
            if data:
                print(f"   📄 Primeiro item: {data[0]}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Testar endpoint de causas de retrabalho
    print("\n4️⃣ TESTANDO CAUSAS DE RETRABALHO")
    try:
        response = requests.get(f"{base_url}/api/formulario/causas-retrabalho", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} causas de retrabalho encontradas")
            if data:
                print(f"   📄 Primeiro item: {data[0]}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 5. Testar endpoint de descrições de atividade
    print("\n5️⃣ TESTANDO DESCRIÇÕES DE ATIVIDADE")
    try:
        response = requests.get(f"{base_url}/api/formulario/descricoes-atividade", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} descrições de atividade encontradas")
            if data:
                print(f"   📄 Primeiro item: {data[0]}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE COMPLETO FINALIZADO")

if __name__ == "__main__":
    testar_endpoints()
