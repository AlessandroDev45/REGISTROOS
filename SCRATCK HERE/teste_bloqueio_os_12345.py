#!/usr/bin/env python3
"""
Teste para verificar se o bloqueio da OS 12345 está funcionando
"""

import requests
import json

def testar_os_12345():
    """Testa se a OS 12345 retorna dados de bloqueio corretos"""
    
    print("🧪 TESTE: Verificando bloqueio da OS 12345")
    print("=" * 50)
    
    try:
        # URL do endpoint
        url = "http://localhost:8000/api/formulario/os/12345"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar campos importantes
            print("\n🔍 VERIFICAÇÕES:")
            print(f"   📋 Número OS: {data.get('numero_os', 'N/A')}")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   👤 Cliente: {data.get('cliente', 'N/A')}")
            print(f"   🔧 Equipamento: {data.get('equipamento', 'N/A')}")
            print(f"   🚫 Bloqueado: {data.get('bloqueado_para_apontamento', 'N/A')}")
            print(f"   ⚠️ Motivo: {data.get('motivo_bloqueio', 'N/A')}")
            
            # Verificar se está bloqueado corretamente
            status_finalizados = [
                'RECUSADA - CONFERIDA',
                'TERMINADA - CONFERIDA', 
                'TERMINADA - EXPEDIDA',
                'OS CANCELADA'
            ]
            
            status_atual = data.get('status', '')
            deveria_estar_bloqueado = status_atual in status_finalizados
            esta_bloqueado = data.get('bloqueado_para_apontamento', False)
            
            print(f"\n🎯 RESULTADO DO TESTE:")
            print(f"   Status atual: {status_atual}")
            print(f"   Deveria estar bloqueado: {deveria_estar_bloqueado}")
            print(f"   Está bloqueado: {esta_bloqueado}")
            
            if deveria_estar_bloqueado == esta_bloqueado:
                print("   ✅ TESTE PASSOU - Bloqueio funcionando corretamente!")
            else:
                print("   ❌ TESTE FALHOU - Bloqueio não está funcionando!")
                
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    testar_os_12345()
