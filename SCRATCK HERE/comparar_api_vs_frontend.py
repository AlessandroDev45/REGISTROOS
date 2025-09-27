#!/usr/bin/env python3
"""
Script para comparar dados da API vs dados que aparecem no frontend
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 COMPARANDO API vs FRONTEND - SETORES")
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
    
    # 2. Buscar dados da API PCP
    print("\n2. 📊 DADOS DA API /api/pcp/programacao-form-data:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        if response.status_code == 200:
            data = response.json()
            setores_api = data.get('setores', [])
            
            print(f"   Total de setores da API: {len(setores_api)}")
            print("\n   🏭 SETORES DA API (primeiros 10):")
            for i, setor in enumerate(setores_api[:10]):
                print(f"   {i+1:2d}. ID: {setor.get('id', 'N/A'):2d} | Nome: {setor.get('nome', 'N/A'):25s} | Depto: {setor.get('departamento_nome', 'N/A')}")
            
            if len(setores_api) > 10:
                print(f"   ... e mais {len(setores_api) - 10} setores")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 3. Dados que aparecem no frontend (baseado no HTML que você mostrou)
    print("\n3. 🖥️ DADOS QUE APARECEM NO FRONTEND:")
    setores_frontend = [
        "ACABAMENTO (MOTORES)",
        "ACABAMENTO (TRANSFORMADORES)", 
        "COMERCIAL (MOTORES)",
        "COMERCIAL (TRANSFORMADORES)",
        "ENGENHARIA (MOTORES)",
        "ENGENHARIA (TRANSFORMADORES)",
        "ENROLAMENTO BARRAMENTO (MOTORES)",
        "ENROLAMENTO BARRAMENTO (TRANSFORMADORES)",
        "ENROLAMENTO FIO REDONDO (MOTORES)",
        "ENROLAMENTO FIO REDONDO (TRANSFORMADORES)",
        "ENSAIOS BT (MOTORES)",
        "ENSAIOS BT (TRANSFORMADORES)",
        "EXPEDICAO (MOTORES)",
        "EXPEDICAO (TRANSFORMADORES)",
        "FECHAMENTO (MOTORES)",
        "FECHAMENTO (TRANSFORMADORES)",
        "GERENCIA (MOTORES)",
        "GERENCIA (TRANSFORMADORES)",
        "GESTAO (MOTORES)",
        "GESTAO (TRANSFORMADORES)",
        "LABORATORIO DE ENSAIOS ELETRICOS (TRANSFORMADORES)",
        "LABORATORIO DE ENSAIOS ELETRICOS (MOTORES)",
        "MECANICA DIA (MOTORES)",
        "MECANICA DIA  (TRANSFORMADORES)",
        "MECANICA NOITE (MOTORES)",
        "MECANICA NOITE (TRANSFORMADORES)",
        "PARTE ATIVA (MOTORES)",
        "PARTE ATIVA (TRANSFORMADORES)",
        "PCP (MOTORES)",
        "PCP (TRANSFORMADORES)",
        "PINTURA (MOTORES)",
        "PINTURA (TRANSFORMADORES)",
        "POLOS (MOTORES)",
        "POLOS (TRANSFORMADORES)",
        "PREPARACAO (MOTORES)",
        "PREPARACAO (TRANSFORMADORES)"
    ]
    
    print(f"   Total de setores no frontend: {len(setores_frontend)}")
    print("\n   🖥️ SETORES DO FRONTEND (primeiros 10):")
    for i, setor in enumerate(setores_frontend[:10]):
        print(f"   {i+1:2d}. {setor}")
    
    if len(setores_frontend) > 10:
        print(f"   ... e mais {len(setores_frontend) - 10} setores")
    
    # 4. Comparação
    print("\n4. 🔍 ANÁLISE COMPARATIVA:")
    
    # Criar lista de nomes da API para comparação
    nomes_api = []
    for setor in setores_api:
        nome = setor.get('nome', '')
        depto = setor.get('departamento_nome', '')
        if nome and depto:
            nome_completo = f"{nome} ({depto})"
            nomes_api.append(nome_completo)
    
    print(f"   📊 Setores formatados da API: {len(nomes_api)}")
    print(f"   🖥️ Setores do frontend: {len(setores_frontend)}")
    
    # Verificar se são iguais
    setores_api_set = set(nomes_api)
    setores_frontend_set = set(setores_frontend)
    
    if setores_api_set == setores_frontend_set:
        print("   ✅ DADOS SÃO IDÊNTICOS!")
    else:
        print("   ❌ DADOS SÃO DIFERENTES!")
        
        # Mostrar diferenças
        apenas_api = setores_api_set - setores_frontend_set
        apenas_frontend = setores_frontend_set - setores_api_set
        
        if apenas_api:
            print(f"\n   📊 APENAS NA API ({len(apenas_api)}):")
            for setor in sorted(apenas_api)[:5]:
                print(f"      - {setor}")
            if len(apenas_api) > 5:
                print(f"      ... e mais {len(apenas_api) - 5}")
        
        if apenas_frontend:
            print(f"\n   🖥️ APENAS NO FRONTEND ({len(apenas_frontend)}):")
            for setor in sorted(apenas_frontend)[:5]:
                print(f"      - {setor}")
            if len(apenas_frontend) > 5:
                print(f"      ... e mais {len(apenas_frontend) - 5}")
    
    print("\n" + "=" * 70)
    print("🎯 COMPARAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
