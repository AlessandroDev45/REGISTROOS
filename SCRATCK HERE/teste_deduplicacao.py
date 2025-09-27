#!/usr/bin/env python3
"""
Teste para verificar se a deduplicação está funcionando
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE: VERIFICAR DEDUPLICAÇÃO")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Verificar dados brutos da API
    print("\n2. 🔧 Dados BRUTOS da API desenvolvimento:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} programações")
            
            # Agrupar por ID para verificar duplicação
            ids_count = {}
            os_count = {}
            
            for prog in data:
                prog_id = prog.get('id')
                os_numero = prog.get('os_numero', 'N/A')
                
                # Contar IDs
                if prog_id in ids_count:
                    ids_count[prog_id] += 1
                else:
                    ids_count[prog_id] = 1
                
                # Contar OS
                if os_numero in os_count:
                    os_count[os_numero] += 1
                else:
                    os_count[os_numero] = 1
            
            # Verificar duplicação por ID
            duplicated_ids = {k: v for k, v in ids_count.items() if v > 1}
            if duplicated_ids:
                print(f"   ❌ IDs DUPLICADOS: {duplicated_ids}")
            else:
                print(f"   ✅ Sem duplicação de IDs")
            
            # Verificar múltiplas programações para mesma OS
            multiple_os = {k: v for k, v in os_count.items() if v > 1}
            if multiple_os:
                print(f"   📊 Múltiplas programações para mesma OS: {multiple_os}")
            else:
                print(f"   ✅ Uma programação por OS")
            
            # Mostrar lista detalhada
            print(f"\n   📋 Lista detalhada:")
            for i, prog in enumerate(data, 1):
                print(f"      {i:2d}. ID: {prog.get('id'):2d} | OS: {prog.get('os_numero', 'N/A'):>10s} | Responsável: {prog.get('responsavel_nome', 'N/A')[:20]:>20s} | Data: {prog.get('inicio_previsto', 'N/A')[:10]}")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Verificar se frontend está aplicando deduplicação
    print(f"\n3. 💡 EXPLICAÇÃO:")
    print(f"   - Se há múltiplas programações para mesma OS, isso é NORMAL")
    print(f"   - Uma OS pode ter várias programações em datas diferentes")
    print(f"   - O frontend deve deduplicar por ID único, não por OS")
    print(f"   - Duplicação de ID seria um BUG real")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Recarregue a página do frontend")
    print("   2. Vá em Desenvolvimento → Programação")
    print("   3. Verifique se não há cards duplicados")
    print("   4. Cada programação deve aparecer apenas UMA vez")

if __name__ == "__main__":
    main()
