#!/usr/bin/env python3
"""
Teste para reproduzir o erro 500 no endpoint save-apontamento-with-pendencia
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
PENDENCIA_URL = f"{BASE_URL}/api/save-apontamento-with-pendencia"

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
        print(response.text)
        return None

def testar_endpoint_pendencia(cookies):
    """Testar o endpoint que está falhando"""
    print(f"\n🔍 Testando endpoint: {PENDENCIA_URL}")
    
    # Dados de teste similares ao que o frontend enviaria
    dados_teste = {
        "numero_os": "TEST-001",
        "inpCliente": "Cliente Teste",
        "inpEquipamento": "Equipamento Teste",
        "data_inicio": datetime.now().strftime('%Y-%m-%d'),
        "hora_inicio": "08:00",
        "data_fim": datetime.now().strftime('%Y-%m-%d'),
        "hora_fim": "17:00",
        "tipo_maquina": "MOTOR",
        "tipo_atividade": "TESTE",
        "descricao_atividade": "Teste de funcionamento",
        "categoria_maquina": "MOTOR ELETRICO",
        "subcategorias_maquina": "MOTOR CA",
        "observacao": "Observação do teste",
        "observacao_geral": "Observação geral",
        "resultado_global": "APROVADO",
        "inpRetrabalho": False,
        "pendencia_descricao": "Pendência de teste",
        "pendencia_prioridade": "NORMAL",
        "testes": {},
        "observacoes_testes": {},
        "testes_exclusivos_selecionados": {}
    }
    
    print(f"📋 Dados de teste:")
    for key, value in dados_teste.items():
        print(f"   {key}: {value}")
    
    try:
        print(f"\n🚀 Enviando requisição...")
        response = requests.post(
            PENDENCIA_URL, 
            cookies=cookies,
            json=dados_teste,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            data = response.json()
            print(f"📋 Resposta:")
            for key, value in data.items():
                print(f"   {key}: {value}")
            return True
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"📋 Resposta de erro:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_com_dados_minimos(cookies):
    """Testar com dados mínimos obrigatórios"""
    print(f"\n🔍 Testando com dados mínimos...")
    
    dados_minimos = {
        "numero_os": "MIN-001",
        "pendencia_descricao": "Pendência mínima",
        "pendencia_prioridade": "NORMAL"
    }
    
    print(f"📋 Dados mínimos:")
    for key, value in dados_minimos.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(
            PENDENCIA_URL, 
            cookies=cookies,
            json=dados_minimos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso com dados mínimos!")
            return True
        else:
            print(f"❌ Erro com dados mínimos")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_com_dados_vazios(cookies):
    """Testar com dados vazios para ver qual validação falha"""
    print(f"\n🔍 Testando com dados vazios...")
    
    dados_vazios = {}
    
    try:
        response = requests.post(
            PENDENCIA_URL, 
            cookies=cookies,
            json=dados_vazios,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Validação funcionando (erro 400 esperado)")
            try:
                error_data = response.json()
                print(f"   Erro de validação: {error_data}")
            except:
                print(f"   {response.text}")
            return True
        else:
            print(f"❌ Resposta inesperada: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Reproduzir Erro 500 - save-apontamento-with-pendencia")
    print("=" * 70)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return
    
    # Teste 1: Dados vazios (deve dar erro 400)
    testar_com_dados_vazios(cookies)
    
    # Teste 2: Dados mínimos
    testar_com_dados_minimos(cookies)
    
    # Teste 3: Dados completos
    sucesso = testar_endpoint_pendencia(cookies)
    
    print("\n" + "=" * 70)
    if sucesso:
        print("🏁 ✅ Endpoint funcionando corretamente!")
    else:
        print("🏁 ❌ Endpoint com problemas!")
        print("\n💡 Próximos passos:")
        print("   1. Verificar logs do backend")
        print("   2. Verificar se todas as tabelas existem")
        print("   3. Verificar se os campos obrigatórios estão corretos")
        print("   4. Verificar se há problemas de importação")

if __name__ == "__main__":
    main()
