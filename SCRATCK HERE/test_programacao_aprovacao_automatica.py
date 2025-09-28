#!/usr/bin/env python3
"""
Teste para verificar o fluxo completo de programação:
1. Iniciar programação
2. Criar apontamento
3. Finalizar programação automaticamente
4. Aprovar apontamento
5. Aprovar programação automaticamente
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
HEADERS = {"Content-Type": "application/json"}

def fazer_login():
    """Fazer login e obter token"""
    login_data = {
        "username": "admin",  # Ajuste conforme necessário
        "password": "admin123"  # Ajuste conforme necessário
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, headers=HEADERS)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def testar_fluxo_completo():
    """Testar o fluxo completo de programação"""
    print("🧪 Iniciando teste do fluxo de programação...")
    
    # 1. Fazer login
    auth_headers = fazer_login()
    if not auth_headers:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado com sucesso")
    
    # 2. Buscar uma programação existente
    try:
        response = requests.get(f"{BASE_URL}/pcp/programacoes", headers=auth_headers)
        if response.status_code == 200:
            programacoes = response.json()
            if programacoes:
                programacao = programacoes[0]
                print(f"📋 Programação encontrada: {programacao.get('id')} - OS {programacao.get('os_numero')}")
                
                # 3. Testar iniciar execução (mudar status para EM_ANDAMENTO)
                print("🚀 Testando iniciar execução...")
                response = requests.patch(
                    f"{BASE_URL}/pcp/programacoes/{programacao['id']}/status",
                    json={"status": "EM_ANDAMENTO"},
                    headers=auth_headers
                )
                if response.status_code == 200:
                    print("✅ Programação iniciada (EM_ANDAMENTO)")
                else:
                    print(f"⚠️ Erro ao iniciar programação: {response.status_code}")
                
                # 4. Simular criação de apontamento
                print("📝 Simulando criação de apontamento...")
                apontamento_data = {
                    "numero_os": programacao.get('os_numero'),
                    "status_os": "EM_ANDAMENTO",
                    "cliente": "Cliente Teste",
                    "equipamento": "Equipamento Teste",
                    "tipo_maquina": 1,
                    "tipo_atividade": 1,
                    "descricao_atividade": 1,
                    "data_inicio": datetime.now().strftime("%Y-%m-%d"),
                    "hora_inicio": "08:00",
                    "data_fim": datetime.now().strftime("%Y-%m-%d"),
                    "hora_fim": "17:00",
                    "observacao": "Teste de programação finalizada automaticamente"
                }
                
                response = requests.post(
                    f"{BASE_URL}/desenvolvimento/apontamentos",
                    json=apontamento_data,
                    headers=auth_headers
                )
                
                if response.status_code == 200:
                    apontamento = response.json()
                    print(f"✅ Apontamento criado: {apontamento.get('id')}")
                    
                    # 5. Verificar se programação foi finalizada automaticamente
                    response = requests.get(f"{BASE_URL}/pcp/programacoes/{programacao['id']}", headers=auth_headers)
                    if response.status_code == 200:
                        prog_atualizada = response.json()
                        if prog_atualizada.get('status') == 'CONCLUIDA':
                            print("✅ Programação finalizada automaticamente!")
                        else:
                            print(f"⚠️ Programação não foi finalizada. Status: {prog_atualizada.get('status')}")
                    
                    # 6. Testar aprovação do apontamento (deve aprovar programação automaticamente)
                    print("👨‍💼 Testando aprovação do apontamento...")
                    response = requests.put(
                        f"{BASE_URL}/desenvolvimento/apontamentos/{apontamento['id']}/aprovar",
                        json={
                            "aprovado_supervisor": True,
                            "observacoes_aprovacao": "Aprovado automaticamente via teste"
                        },
                        headers=auth_headers
                    )
                    
                    if response.status_code == 200:
                        aprovacao_result = response.json()
                        print(f"✅ Apontamento aprovado: {aprovacao_result.get('message')}")
                        
                        if aprovacao_result.get('programacao_aprovada'):
                            print("🎯 Programação aprovada automaticamente!")
                            print(f"   OS: {aprovacao_result['programacao_aprovada']['os_numero']}")
                            print(f"   Status: {aprovacao_result['programacao_aprovada']['status']}")
                        else:
                            print("⚠️ Programação não foi aprovada automaticamente")
                    else:
                        print(f"❌ Erro ao aprovar apontamento: {response.status_code} - {response.text}")
                
                else:
                    print(f"❌ Erro ao criar apontamento: {response.status_code} - {response.text}")
            else:
                print("⚠️ Nenhuma programação encontrada")
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    testar_fluxo_completo()
