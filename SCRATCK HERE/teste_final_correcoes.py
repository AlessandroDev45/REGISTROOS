#!/usr/bin/env python3
"""
Teste final das correções:
1. Cliente e equipamento em desenvolvimento
2. Modais sem departamento/setor
3. PCP pendências por departamento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE FINAL DAS CORREÇÕES")
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
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar programações em desenvolvimento (cliente e equipamento)
    print("\n2. 🔧 DESENVOLVIMENTO - Programações (cliente e equipamento):")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} programações")
            
            if data:
                print("   📊 Verificando cliente e equipamento:")
                for i, prog in enumerate(data[:3], 1):  # Primeiras 3
                    os_numero = prog.get('os_numero', 'N/A')
                    cliente = prog.get('cliente_nome', 'N/A')
                    equipamento = prog.get('equipamento_descricao', 'N/A')
                    print(f"      {i}. OS: {os_numero} | Cliente: {cliente[:30]} | Equipamento: {equipamento[:30]}")
                    
                    if cliente == 'N/A' or cliente == '':
                        print(f"         ❌ PROBLEMA: Cliente vazio!")
                    else:
                        print(f"         ✅ Cliente OK")
                        
                    if equipamento == 'N/A' or equipamento == '':
                        print(f"         ❌ PROBLEMA: Equipamento vazio!")
                    else:
                        print(f"         ✅ Equipamento OK")
                        
            else:
                print("   ❌ Nenhuma programação encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar colaboradores para modal
    print("\n3. 👥 DESENVOLVIMENTO - Colaboradores para modal:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/colaboradores")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} colaboradores")
            
            if data:
                print("   📊 Lista de colaboradores do setor:")
                for i, colab in enumerate(data[:5], 1):  # Primeiros 5
                    nome = colab.get('nome_completo', 'N/A')
                    setor = colab.get('setor', 'N/A')
                    privilege = colab.get('privilege_level', 'N/A')
                    print(f"      {i}. {nome[:25]:>25s} | Setor: {setor[:15]:>15s} | Nível: {privilege}")
            else:
                print("   ❌ Nenhum colaborador encontrado!")
                
        else:
            print(f"   ❌ Erro: {response.status_code} - Endpoint pode não existir ainda")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar PCP pendências por departamento
    print("\n4. 🏭 PCP - Pendências por departamento:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} pendências")
            
            if data:
                print("   📊 Pendências do departamento:")
                departamentos_encontrados = set()
                for i, pend in enumerate(data, 1):
                    os_numero = pend.get('numero_os', 'N/A')
                    responsavel = pend.get('responsavel_nome', 'N/A')
                    status = pend.get('status', 'N/A')
                    departamento = pend.get('setor_departamento', 'N/A')
                    print(f"      {i:2d}. OS: {os_numero:>10s} | Responsável: {responsavel[:20]:>20s} | Dept: {departamento}")
                    
                    if departamento != 'N/A':
                        departamentos_encontrados.add(departamento)
                
                print(f"\n   🏢 Departamentos únicos encontrados: {len(departamentos_encontrados)}")
                for dept in sorted(departamentos_encontrados):
                    print(f"      - {dept}")
                    
                if len(departamentos_encontrados) <= 1:
                    print("   ✅ CORRETO: PCP vê apenas pendências do seu departamento")
                else:
                    print("   ❌ PROBLEMA: PCP está vendo pendências de múltiplos departamentos")
                    
            else:
                print("   ❌ Nenhuma pendência encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n💡 RESULTADOS ESPERADOS:")
    print("   ✅ Desenvolvimento: Cliente e equipamento preenchidos")
    print("   ✅ Modal: Apenas colaboradores do setor (sem departamento/setor)")
    print("   ✅ PCP: Pendências apenas do departamento do usuário")

if __name__ == "__main__":
    main()
