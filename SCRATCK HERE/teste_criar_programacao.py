#!/usr/bin/env python3
"""
Script para testar criação de programação e reproduzir o erro 500
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def main():
    print("🚨 TESTANDO CRIAÇÃO DE PROGRAMAÇÃO - REPRODUZIR ERRO 500")
    print("=" * 70)
    
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
    
    # 2. Preparar dados da programação
    print("\n2. 📋 Preparando dados da programação...")
    
    # Dados que o frontend está enviando
    agora = datetime.now()
    inicio = agora + timedelta(hours=1)
    fim = agora + timedelta(hours=3)
    
    programacao_data = {
        "os_numero": "000012345",  # OS que sabemos que existe
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "id_departamento": 1,  # MOTORES
        "id_setor": 42,  # LABORATORIO DE ENSAIOS ELETRICOS
        "responsavel_id": 1,  # ADMINISTRADOR
        "observacoes": "Teste de criação de programação",
        "status": "PROGRAMADA"
    }
    
    print(f"   📊 Dados da programação:")
    print(f"      - OS: {programacao_data['os_numero']}")
    print(f"      - Departamento: {programacao_data['id_departamento']}")
    print(f"      - Setor: {programacao_data['id_setor']}")
    print(f"      - Responsável: {programacao_data['responsavel_id']}")
    print(f"      - Início: {programacao_data['inicio_previsto']}")
    print(f"      - Fim: {programacao_data['fim_previsto']}")
    
    # 3. Tentar criar programação
    print("\n3. 🚀 Tentando criar programação...")
    try:
        response = session.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=programacao_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ Programação criada com sucesso!")
            data = response.json()
            print(f"   📊 ID da programação: {data.get('id', 'N/A')}")
        else:
            print(f"   ❌ Erro {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
            # Tentar parsear JSON de erro
            try:
                error_data = response.json()
                print(f"   🔍 Detalhes do erro: {error_data}")
            except:
                print("   ⚠️ Resposta não é JSON válido")
                
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Teste alternativo sem os_numero
    print("\n4. 🔄 Teste alternativo com id_ordem_servico...")
    
    programacao_data_alt = {
        "id_ordem_servico": 1,  # ID direto da OS
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "id_departamento": 1,
        "id_setor": 42,
        "responsavel_id": 1,
        "observacoes": "Teste alternativo com ID direto",
        "status": "PROGRAMADA"
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=programacao_data_alt,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ Programação criada com sucesso!")
            data = response.json()
            print(f"   📊 ID da programação: {data.get('id', 'N/A')}")
        else:
            print(f"   ❌ Erro {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
