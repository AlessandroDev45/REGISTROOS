#!/usr/bin/env python3
"""
Teste para verificar validação Pydantic
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
APONTAMENTO_URL = f"{BASE_URL}/api/desenvolvimento/os/apontamentos"

def fazer_login():
    """Fazer login e obter cookies de sessão"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_validacao_pydantic(cookies):
    """Testar diferentes cenários de validação"""
    
    # Teste 1: Dados vazios
    print(f"\n🔍 Teste 1: Dados vazios")
    dados_vazios = {}
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_vazios,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Apenas numero_os (campo obrigatório)
    print(f"\n🔍 Teste 2: Apenas numero_os")
    dados_minimos = {
        "numero_os": "TEST-001"
    }
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_minimos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Dados com tipos incorretos
    print(f"\n🔍 Teste 3: Dados com tipos incorretos")
    dados_incorretos = {
        "numero_os": "TEST-002",
        "usuario_id": "string_instead_of_int",  # Deveria ser int
        "retrabalho": "string_instead_of_bool"  # Deveria ser bool
    }
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_incorretos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Dados completos e corretos
    print(f"\n🔍 Teste 4: Dados completos e corretos")
    dados_completos = {
        "numero_os": "TEST-003",
        "cliente": "Cliente Teste",
        "equipamento": "Equipamento Teste",
        "tipo_maquina": "MOTOR",
        "tipo_atividade": "TESTE",
        "descricao_atividade": "Teste de funcionamento",
        "categoria_maquina": "MOTOR ELETRICO",
        "subcategorias_maquina": "MOTOR CA",
        "data_inicio": "2025-09-27",
        "hora_inicio": "08:00",
        "data_fim": "2025-09-27",
        "hora_fim": "17:00",
        "observacao": "Observação",
        "observacao_geral": "Observação geral",
        "resultado_global": "APROVADO",
        "status_os": "FINALIZADO",
        "retrabalho": False,
        "usuario_id": 1,
        "departamento": "MOTORES",
        "setor": "LABORATORIO",
        "testes_selecionados": [],
        "testes_exclusivos_selecionados": [],
        "tipo_salvamento": "APONTAMENTO",
        "supervisor_config": {"horas_orcadas": 8.0}
    }
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_completos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE: Validação Pydantic")
    print("=" * 60)
    
    cookies = fazer_login()
    if not cookies:
        return
    
    testar_validacao_pydantic(cookies)
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
