#!/usr/bin/env python3
"""
Script para testar o endpoint de dados do formulário do PCP
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔄 TESTANDO ENDPOINT PCP PROGRAMACAO-FORM-DATA")
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
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint programacao-form-data
    print("\n2. Testando /api/pcp/programacao-form-data...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint funcionando!")
            
            # Verificar dados retornados
            setores = data.get('setores', [])
            usuarios = data.get('usuarios', [])
            departamentos = data.get('departamentos', [])
            ordens_servico = data.get('ordens_servico', [])
            
            print(f"\n   📊 DADOS RETORNADOS:")
            print(f"   - Setores: {len(setores)}")
            print(f"   - Usuários: {len(usuarios)}")
            print(f"   - Departamentos: {len(departamentos)}")
            print(f"   - Ordens de Serviço: {len(ordens_servico)}")
            
            if len(setores) > 0:
                print(f"\n   🏢 PRIMEIROS 3 SETORES:")
                for i, setor in enumerate(setores[:3]):
                    print(f"   {i+1}. {setor.get('nome', 'N/A')} - Depto: {setor.get('departamento_nome', 'N/A')}")
            
            if len(usuarios) > 0:
                print(f"\n   👥 PRIMEIROS 3 USUÁRIOS:")
                for i, usuario in enumerate(usuarios[:3]):
                    print(f"   {i+1}. {usuario.get('nome_completo', 'N/A')} - {usuario.get('privilege_level', 'N/A')} - Setor: {usuario.get('setor', 'N/A')}")
            
            if len(departamentos) > 0:
                print(f"\n   🏭 DEPARTAMENTOS:")
                for i, dept in enumerate(departamentos[:5]):
                    print(f"   {i+1}. {dept.get('nome_tipo', 'N/A')}")
            
            if len(ordens_servico) > 0:
                print(f"\n   📋 PRIMEIRAS 3 OSs:")
                for i, os in enumerate(ordens_servico[:3]):
                    print(f"   {i+1}. OS: {os.get('os_numero', 'N/A')} - Cliente: {os.get('cliente_nome', 'N/A')}")
            
            # Verificar se há erros
            if 'erro' in data:
                print(f"\n   ⚠️ ERRO REPORTADO: {data['erro']}")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
