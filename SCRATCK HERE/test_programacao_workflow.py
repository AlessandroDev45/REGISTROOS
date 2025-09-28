#!/usr/bin/env python3
"""
Teste do fluxo completo de programação -> apontamento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_programacao_workflow():
    """Testa o fluxo completo de programação para apontamento"""
    
    print("🧪 TESTE: Fluxo Programação -> Apontamento")
    print("=" * 50)
    
    # 1. Listar programações disponíveis
    print("\n1️⃣ Listando programações disponíveis...")
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacoes")
        if response.status_code == 200:
            programacoes = response.json()
            print(f"✅ Encontradas {len(programacoes)} programações")
            
            # Encontrar uma programação PROGRAMADA
            programacao_teste = None
            for prog in programacoes:
                if prog.get('status') == 'PROGRAMADA':
                    programacao_teste = prog
                    break
            
            if not programacao_teste:
                print("❌ Nenhuma programação PROGRAMADA encontrada")
                return False
                
            print(f"🎯 Programação selecionada: OS {programacao_teste['os_numero']} (ID: {programacao_teste['id']})")
            
        else:
            print(f"❌ Erro ao listar programações: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 2. Simular clique em "Iniciar" - atualizar status para EM_ANDAMENTO
    print(f"\n2️⃣ Iniciando execução da programação {programacao_teste['id']}...")
    try:
        response = requests.patch(
            f"{BASE_URL}/api/pcp/programacoes/{programacao_teste['id']}/status",
            json={"status": "EM_ANDAMENTO"}
        )
        
        if response.status_code == 200:
            print("✅ Status da programação atualizado para EM_ANDAMENTO")
        else:
            print(f"❌ Erro ao atualizar status: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 3. Verificar se a OS existe para apontamento
    print(f"\n3️⃣ Verificando OS {programacao_teste['os_numero']} para apontamento...")
    try:
        # Simular busca de OS como faria o frontend
        os_numero = programacao_teste['os_numero']
        
        # Testar endpoint de verificação de programação
        response = requests.get(f"{BASE_URL}/api/desenvolvimento/verificar-programacao-os/{os_numero}")
        
        if response.status_code == 200:
            verificacao = response.json()
            print(f"✅ Verificação de programação: {verificacao}")
            
            if verificacao.get('tem_programacao'):
                print("🎯 Programação detectada corretamente!")
            else:
                print("⚠️ Programação não detectada")
                
        else:
            print(f"❌ Erro ao verificar programação: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    
    # 4. Simular URL que seria gerada
    print(f"\n4️⃣ URL que seria gerada pelo frontend:")
    setor_slug = "laboratorio-eletrico"  # Mesmo slug usado no código
    url_frontend = f"/desenvolvimento/{setor_slug}?tab=apontamento&os={programacao_teste['os_numero']}&programacao_id={programacao_teste['id']}"
    print(f"🔗 {url_frontend}")
    
    print(f"\n5️⃣ Parâmetros que o frontend deveria detectar:")
    print(f"   - tab: apontamento")
    print(f"   - os: {programacao_teste['os_numero']}")
    print(f"   - programacao_id: {programacao_teste['id']}")
    
    print("\n✅ Teste concluído! Verifique se:")
    print("   1. O frontend redireciona para a aba 'apontamento'")
    print("   2. O campo OS é pré-preenchido")
    print("   3. A programação é detectada automaticamente")
    print("   4. O botão muda para 'Salvar e Finalizar Programação'")
    
    return True

if __name__ == "__main__":
    test_programacao_workflow()
