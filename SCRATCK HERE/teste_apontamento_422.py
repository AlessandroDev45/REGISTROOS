#!/usr/bin/env python3
"""
Teste para reproduzir o erro 422 no endpoint /api/desenvolvimento/os/apontamentos
"""

import requests
import json
from datetime import datetime

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
        print(response.text)
        return None

def testar_endpoint_apontamento(cookies):
    """Testar o endpoint que está falhando"""
    print(f"\n🔍 Testando endpoint: {APONTAMENTO_URL}")
    
    # Dados similares ao que o frontend enviaria
    dados_frontend = {
        "numero_os": "TEST-APT-001",
        "status_os": "FINALIZADO",
        "cliente": "Cliente Teste",
        "equipamento": "Equipamento Teste",
        "tipo_maquina": "MOTOR",
        "tipo_atividade": "TESTE",
        "descricao_atividade": "Teste de funcionamento",
        "categoria_maquina": "MOTOR ELETRICO",
        "subcategorias_maquina": "MOTOR CA",
        "data_inicio": datetime.now().strftime('%Y-%m-%d'),
        "hora_inicio": "08:00",
        "data_fim": datetime.now().strftime('%Y-%m-%d'),
        "hora_fim": "17:00",
        "retrabalho": False,
        "causa_retrabalho": None,
        "observacao_geral": "Observação do teste",
        "resultado_global": "APROVADO",
        "usuario_id": 1,
        "departamento": "MOTORES",
        "setor": "LABORATORIO",
        "testes_selecionados": [],
        "testes_exclusivos_selecionados": [],
        "tipo_salvamento": "APONTAMENTO",
        "supervisor_config": {
            "horas_orcadas": 8.0,
            "testes_iniciais": True,
            "testes_parciais": False,
            "testes_finais": True
        },
        "pendencia_origem_id": None
    }
    
    print(f"📋 Dados de teste:")
    for key, value in dados_frontend.items():
        print(f"   {key}: {value}")
    
    try:
        print(f"\n🚀 Enviando requisição...")
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_frontend,
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
        elif response.status_code == 422:
            print(f"❌ Erro 422 - Unprocessable Entity")
            print(f"📋 Detalhes do erro de validação:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
                
                # Analisar detalhes do erro
                if 'detail' in error_data:
                    for error in error_data['detail']:
                        if isinstance(error, dict):
                            campo = error.get('loc', ['unknown'])[-1]
                            mensagem = error.get('msg', 'Erro desconhecido')
                            tipo = error.get('type', 'unknown')
                            print(f"   🔴 Campo '{campo}': {mensagem} (tipo: {tipo})")
                        
            except:
                print(f"   {response.text}")
            return False
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_campos_obrigatorios(cookies):
    """Testar apenas com campos obrigatórios"""
    print(f"\n🔍 Testando apenas campos obrigatórios...")
    
    dados_minimos = {
        "numero_os": "MIN-APT-001"
    }
    
    print(f"📋 Dados mínimos:")
    for key, value in dados_minimos.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_minimos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso com dados mínimos!")
            return True
        elif response.status_code == 422:
            print(f"❌ Erro 422 com dados mínimos")
            try:
                error_data = response.json()
                print(f"   Erros de validação:")
                for error in error_data.get('detail', []):
                    if isinstance(error, dict):
                        campo = error.get('loc', ['unknown'])[-1]
                        mensagem = error.get('msg', 'Erro desconhecido')
                        print(f"   🔴 {campo}: {mensagem}")
            except:
                print(f"   {response.text}")
            return False
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_sem_campos_problematicos(cookies):
    """Testar removendo campos que podem estar causando problema"""
    print(f"\n🔍 Testando sem campos potencialmente problemáticos...")
    
    dados_limpos = {
        "numero_os": "CLEAN-001",
        "cliente": "Cliente Teste",
        "equipamento": "Equipamento Teste",
        "tipo_maquina": "MOTOR",
        "tipo_atividade": "TESTE",
        "descricao_atividade": "Teste",
        "data_inicio": datetime.now().strftime('%Y-%m-%d'),
        "hora_inicio": "08:00",
        "observacao_geral": "Teste"
    }
    
    print(f"📋 Dados limpos:")
    for key, value in dados_limpos.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_limpos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso com dados limpos!")
            return True
        elif response.status_code == 422:
            print(f"❌ Ainda erro 422")
            try:
                error_data = response.json()
                print(f"   Erros:")
                for error in error_data.get('detail', []):
                    if isinstance(error, dict):
                        campo = error.get('loc', ['unknown'])[-1]
                        mensagem = error.get('msg', 'Erro desconhecido')
                        print(f"   🔴 {campo}: {mensagem}")
            except:
                print(f"   {response.text}")
            return False
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Reproduzir Erro 422 - /api/desenvolvimento/os/apontamentos")
    print("=" * 70)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return
    
    # Teste 1: Campos obrigatórios apenas
    testar_campos_obrigatorios(cookies)
    
    # Teste 2: Dados limpos
    testar_sem_campos_problematicos(cookies)
    
    # Teste 3: Dados completos do frontend
    sucesso = testar_endpoint_apontamento(cookies)
    
    print("\n" + "=" * 70)
    if sucesso:
        print("🏁 ✅ Endpoint funcionando corretamente!")
    else:
        print("🏁 ❌ Endpoint com problemas de validação!")
        print("\n💡 Próximos passos:")
        print("   1. Verificar modelo Pydantic ApontamentoCreate")
        print("   2. Verificar se campos obrigatórios estão sendo enviados")
        print("   3. Verificar tipos de dados dos campos")
        print("   4. Verificar se há campos extras não permitidos")

if __name__ == "__main__":
    main()
