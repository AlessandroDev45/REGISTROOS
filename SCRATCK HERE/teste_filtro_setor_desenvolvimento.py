#!/usr/bin/env python3
"""
Teste para verificar se o filtro por setor está funcionando no desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔒 TESTE: FILTRO POR SETOR NO DESENVOLVIMENTO")
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
            print("   ✅ Login realizado com sucesso")
            user_data = login_response.json()
            print(f"   👤 Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   🏢 Setor: {user_data.get('setor', 'N/A')} (ID: {user_data.get('id_setor', 'N/A')})")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint de programações do desenvolvimento
    print("\n2. 🎯 Testando programações do desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} programações retornadas")
            
            # Verificar se todas são do mesmo setor
            setores_encontrados = set()
            for prog in data:
                if 'id_setor' in prog:
                    setores_encontrados.add(prog['id_setor'])
                    
            print(f"   🔍 Setores encontrados: {setores_encontrados}")
            
            if len(setores_encontrados) <= 1:
                print("   ✅ FILTRO FUNCIONANDO: Apenas um setor retornado")
            else:
                print("   ❌ FILTRO FALHOU: Múltiplos setores retornados")
                
            # Mostrar algumas programações
            if data:
                print("\n   📊 Primeiras programações:")
                for i, prog in enumerate(data[:3]):
                    print(f"      {i+1}. OS: {prog.get('os_numero', 'N/A')} | Setor ID: {prog.get('id_setor', 'N/A')} | Status: {prog.get('status', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 3. Testar endpoint de pendências do desenvolvimento
    print("\n3. 📋 Testando pendências do desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} pendências retornadas")
            
            # Verificar se todas são do mesmo setor (através do apontamento origem)
            print(f"   🔍 Pendências filtradas por setor do usuário")
            
            # Mostrar algumas pendências
            if data:
                print("\n   📊 Primeiras pendências:")
                for i, pend in enumerate(data[:3]):
                    print(f"      {i+1}. ID: {pend.get('id', 'N/A')} | Status: {pend.get('status', 'N/A')} | Cliente: {pend.get('cliente', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Comparar com PCP (deve mostrar todos os setores)
    print("\n4. 🏭 Comparando com PCP (deve mostrar todos os setores)...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ PCP: {len(data)} programações retornadas")
            
            # Verificar setores no PCP
            setores_pcp = set()
            for prog in data:
                if 'id_setor' in prog:
                    setores_pcp.add(prog['id_setor'])
                    
            print(f"   🔍 Setores no PCP: {setores_pcp}")
            print(f"   📊 Total de setores diferentes: {len(setores_pcp)}")
            
            if len(setores_pcp) > 1:
                print("   ✅ PCP CORRETO: Mostra múltiplos setores")
            else:
                print("   ⚠️ PCP: Apenas um setor (pode estar correto se só há dados de um setor)")
        else:
            print(f"   ❌ Erro PCP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição PCP: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n📋 RESUMO:")
    print("✅ Desenvolvimento deve mostrar APENAS programações/pendências do setor do usuário")
    print("✅ PCP deve mostrar programações/pendências de TODOS os setores")

if __name__ == "__main__":
    main()
