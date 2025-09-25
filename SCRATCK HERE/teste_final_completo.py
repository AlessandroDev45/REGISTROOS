#!/usr/bin/env python3
"""
Teste final completo para verificar se tudo está funcionando
"""

import requests
import json

def teste_final_completo():
    """Testa todos os endpoints necessários"""
    
    print("🧪 TESTE FINAL COMPLETO")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Testar OS 12345
    print("\n1️⃣ TESTANDO OS 12345")
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
            
            # Verificar se está bloqueada
            status_finalizados = [
                'RECUSADA - CONFERIDA',
                'TERMINADA - CONFERIDA', 
                'TERMINADA - EXPEDIDA',
                'OS CANCELADA'
            ]
            status_atual = data.get('status', '')
            bloqueada = status_atual in status_finalizados
            print(f"   🚫 Bloqueada: {'SIM' if bloqueada else 'NÃO'}")
            
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Testar tipos de máquina (desenvolvimento)
    print("\n2️⃣ TESTANDO TIPOS DE MÁQUINA (DESENVOLVIMENTO)")
    try:
        response = requests.get(f"{base_url}/api/formulario/tipos-maquina", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} tipos encontrados")
            if data:
                print(f"   📄 Primeiro: {data[0].get('nome_tipo')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar tipos de máquina (admin)
    print("\n3️⃣ TESTANDO TIPOS DE MÁQUINA (ADMIN)")
    try:
        response = requests.get(f"{base_url}/api/admin/tipos-maquina/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} tipos encontrados")
            if data:
                print(f"   📄 Primeiro: {data[0].get('nome_tipo')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar tipos de atividade
    print("\n4️⃣ TESTANDO TIPOS DE ATIVIDADE")
    try:
        response = requests.get(f"{base_url}/api/formulario/tipos-atividade", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} tipos encontrados")
            if data:
                print(f"   📄 Primeiro: {data[0].get('nome_tipo')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 5. Testar descrições de atividade
    print("\n5️⃣ TESTANDO DESCRIÇÕES DE ATIVIDADE")
    try:
        response = requests.get(f"{base_url}/api/formulario/descricoes-atividade", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} descrições encontradas")
            if data:
                print(f"   📄 Primeira: {data[0].get('codigo')} - {data[0].get('descricao')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 6. Testar causas de retrabalho
    print("\n6️⃣ TESTANDO CAUSAS DE RETRABALHO")
    try:
        response = requests.get(f"{base_url}/api/formulario/causas-retrabalho", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} causas encontradas")
            if data:
                print(f"   📄 Primeira: {data[0].get('codigo')} - {data[0].get('descricao')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE FINAL COMPLETO CONCLUÍDO")
    print("\n📋 RESUMO:")
    print("   ✅ OS 12345 deve estar bloqueada mas mostrando dados")
    print("   ✅ Tipos de máquina devem funcionar no desenvolvimento E admin")
    print("   ✅ Tipos de atividade devem carregar")
    print("   ✅ Descrições de atividade devem carregar (não mais 0 opções)")
    print("   ✅ Causas de retrabalho devem carregar")

if __name__ == "__main__":
    teste_final_completo()
