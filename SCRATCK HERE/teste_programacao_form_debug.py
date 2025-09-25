#!/usr/bin/env python3
"""
Teste específico para debug do endpoint programacao-form-data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🧪 TESTE DEBUG: Endpoint programacao-form-data")
    print("=" * 60)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Fazer login
    print("\n1. Fazendo login...")
    try:
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        response = session.post(f"{BASE_URL}/api/token", data=login_data)
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.status_code}")
            return
        print("   ✅ Login realizado com sucesso")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return
    
    # Testar endpoint programacao-form-data
    print("\n2. Testando endpoint /api/pcp/programacao-form-data...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint funcionando")
            
            # Verificar estrutura detalhada
            print(f"\n   📊 ANÁLISE DETALHADA:")
            print(f"   - setores: {len(data.get('setores', []))} itens")
            print(f"   - usuarios: {len(data.get('usuarios', []))} itens")
            print(f"   - departamentos: {len(data.get('departamentos', []))} itens")
            print(f"   - ordens_servico: {len(data.get('ordens_servico', []))} itens")
            print(f"   - status_opcoes: {len(data.get('status_opcoes', []))} itens")
            
            # Mostrar alguns exemplos se houver dados
            if data.get('setores'):
                print(f"\n   🏢 SETORES (primeiros 3):")
                for i, setor in enumerate(data['setores'][:3]):
                    print(f"   {i+1}. ID: {setor.get('id')}, Nome: {setor.get('nome')}, Depto: {setor.get('departamento_nome', 'N/A')}")
            
            if data.get('usuarios'):
                print(f"\n   👥 USUÁRIOS (primeiros 3):")
                for i, usuario in enumerate(data['usuarios'][:3]):
                    print(f"   {i+1}. ID: {usuario.get('id')}, Nome: {usuario.get('nome_completo')}, Setor: {usuario.get('setor_nome', 'N/A')}")
            
            if data.get('departamentos'):
                print(f"\n   🏛️ DEPARTAMENTOS:")
                for i, dept in enumerate(data['departamentos']):
                    print(f"   {i+1}. ID: {dept.get('id')}, Nome: {dept.get('nome')}")
            
            if data.get('ordens_servico'):
                print(f"\n   📋 ORDENS DE SERVIÇO (primeiras 3):")
                for i, os in enumerate(data['ordens_servico'][:3]):
                    print(f"   {i+1}. ID: {os.get('id')}, OS: {os.get('os_numero')}, Status: {os.get('status')}")
            
            if data.get('status_opcoes'):
                print(f"\n   📊 STATUS OPÇÕES:")
                for i, status in enumerate(data['status_opcoes']):
                    print(f"   {i+1}. {status}")
            
            # Verificar se há dados vazios
            if all(len(data.get(key, [])) == 0 for key in ['setores', 'usuarios', 'departamentos']):
                print(f"\n   ⚠️ PROBLEMA: Todos os arrays principais estão vazios!")
                print(f"   Isso indica que as consultas SQL não estão retornando dados.")
            
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    main()
