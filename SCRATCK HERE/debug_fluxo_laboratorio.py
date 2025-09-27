#!/usr/bin/env python3
"""
DEBUG FLUXO LABORATÓRIO
=======================

Investigar problemas no fluxo de programação para laboratório.
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}
SUPERVISOR_LAB = {"username": "supervisor.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"}
USER_LAB = {"username": "user.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"}

def verificar_banco_dados():
    """Verificar dados no banco"""
    print("🔍 Verificando dados no banco...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar usuários do laboratório
        cursor.execute("""
            SELECT id, nome_completo, nome_usuario, email, privilege_level
            FROM tipo_usuarios 
            WHERE email LIKE '%laboratorio%'
            ORDER BY id
        """)
        usuarios_lab = cursor.fetchall()
        
        print(f"👥 Usuários do laboratório:")
        for user in usuarios_lab:
            print(f"   ID {user[0]}: {user[1]} ({user[2]}) - {user[3]} - {user[4]}")
        
        # Verificar setores do laboratório
        cursor.execute("""
            SELECT id, nome, departamento
            FROM tipo_setores 
            WHERE nome LIKE '%LABORATORIO%'
            ORDER BY id
        """)
        setores_lab = cursor.fetchall()
        
        print(f"\n🏢 Setores do laboratório:")
        for setor in setores_lab:
            print(f"   ID {setor[0]}: {setor[1]} - {setor[2]}")
        
        # Verificar programações recentes
        cursor.execute("""
            SELECT id, id_ordem_servico, responsavel_id, status, observacoes, created_at
            FROM programacoes 
            ORDER BY id DESC
            LIMIT 5
        """)
        programacoes = cursor.fetchall()
        
        print(f"\n📋 Últimas 5 programações:")
        for prog in programacoes:
            print(f"   ID {prog[0]}: OS={prog[1]}, Resp={prog[2]}, Status={prog[3]}")
            print(f"      Obs: {prog[4][:50] if prog[4] else 'N/A'}...")
            print(f"      Criado: {prog[5]}")
        
        conn.close()
        return usuarios_lab, setores_lab
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return [], []

def fazer_login(usuario, nome_usuario):
    """Fazer login e obter sessão"""
    print(f"\n🔐 Fazendo login como {nome_usuario}...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=usuario, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('user', {})
        print(f"✅ Login realizado! {user_info.get('nome_completo', 'N/A')} (ID: {user_info.get('id', 'N/A')})")
        return session, user_info
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None, None

def criar_programacao_pcp(session):
    """Criar programação via PCP"""
    print(f"\n📋 Criando programação via PCP...")
    
    agora = datetime.now()
    inicio = agora + timedelta(hours=4, minutes=24)  # 4.4 horas
    fim = inicio + timedelta(hours=4, minutes=24)
    
    dados_programacao = {
        "id_ordem_servico": 1,
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "observacoes": "Programação para laboratório - 4.4h previstas",
        "id_setor": None,
        "prioridade": "ALTA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=dados_programacao)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada! ID: {prog_id}")
            print(f"   Início: {inicio.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Fim: {fim.strftime('%d/%m/%Y %H:%M')}")
            return prog_id
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_programacoes_supervisor(session):
    """Verificar programações disponíveis para supervisor"""
    print(f"\n👥 Verificando programações para supervisor...")
    
    try:
        # Verificar endpoint de programações do supervisor
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Supervisor vê {len(data)} programações")
            
            for i, prog in enumerate(data):
                print(f"   {i+1}. ID: {prog.get('id')} - Status: {prog.get('status')}")
                print(f"      Responsável: {prog.get('responsavel_id')}")
                print(f"      Observações: {prog.get('observacoes', '')[:50]}...")
            
            return data
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def reatribuir_programacao(session, prog_id, user_lab_id):
    """Reatribuir programação para usuário do laboratório"""
    print(f"\n🔄 Reatribuindo programação {prog_id} para usuário laboratório...")
    
    agora = datetime.now()
    dados_reatribuicao = {
        "responsavel_id": user_lab_id,
        "setor_destino": "LABORATORIO DE ENSAIOS ELETRICOS",
        "departamento_destino": "TRANSFORMADORES",  # Verificar se está correto
        "data_inicio": agora.isoformat(),
        "data_fim": agora.isoformat(),  # Mesmo horário (problema identificado!)
        "observacoes": "TESTES INICIAIS, TESTES ARMADURA"
    }
    
    try:
        response = session.patch(f"{BASE_URL}/api/pcp/programacoes/{prog_id}/reatribuir", json=dados_reatribuicao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação reatribuída!")
            print(f"   ID: {data.get('id')}")
            print(f"   Responsável: {data.get('responsavel_id')}")
            return True
        else:
            print(f"❌ Erro ao reatribuir: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_dashboard_usuario_lab(session):
    """Verificar dashboard do usuário laboratório"""
    print(f"\n📊 Verificando dashboard do usuário laboratório...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Dashboard retornou {len(data)} programações")
            
            if len(data) > 0:
                for i, prog in enumerate(data):
                    print(f"   {i+1}. ID: {prog.get('id')} - OS: {prog.get('os_numero')}")
                    print(f"      Responsável: {prog.get('responsavel_nome')}")
                    print(f"      Observações: {prog.get('observacoes', '')[:50]}...")
            else:
                print(f"❌ Dashboard vazio - programação não aparece")
            
            return data
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 DEBUG FLUXO LABORATÓRIO")
    print("=" * 35)
    
    # 1. Verificar banco de dados
    usuarios_lab, setores_lab = verificar_banco_dados()
    
    if not usuarios_lab:
        print("❌ Nenhum usuário do laboratório encontrado")
        return
    
    # Encontrar IDs dos usuários
    user_lab_id = None
    for user in usuarios_lab:
        if "user.laboratorio" in user[3]:  # email
            user_lab_id = user[0]
            break
    
    if not user_lab_id:
        print("❌ Usuário do laboratório não encontrado")
        return
    
    print(f"\n🎯 Usuário laboratório encontrado: ID {user_lab_id}")
    
    # 2. PCP cria programação
    session_admin, admin_info = fazer_login(ADMIN_USER, "ADMIN/PCP")
    if not session_admin:
        return
    
    prog_id = criar_programacao_pcp(session_admin)
    if not prog_id:
        return
    
    # 3. Supervisor verifica programações
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_LAB, "SUPERVISOR LAB")
    if not session_supervisor:
        return
    
    programacoes_supervisor = verificar_programacoes_supervisor(session_supervisor)
    
    # 4. Supervisor reatribui
    if prog_id:
        reatribuicao_ok = reatribuir_programacao(session_supervisor, prog_id, user_lab_id)
    
    # 5. Usuário verifica dashboard
    session_user, user_info = fazer_login(USER_LAB, "USUÁRIO LAB")
    if not session_user:
        return
    
    programacoes_user = verificar_dashboard_usuario_lab(session_user)
    
    # 6. Análise final
    print(f"\n📊 ANÁLISE DOS PROBLEMAS:")
    print(f"   1. Supervisor vê programações: {'✅' if len(programacoes_supervisor) > 0 else '❌'}")
    print(f"   2. Reatribuição funciona: {'✅' if 'reatribuicao_ok' in locals() and reatribuicao_ok else '❌'}")
    print(f"   3. Usuário vê no dashboard: {'✅' if len(programacoes_user) > 0 else '❌'}")

if __name__ == "__main__":
    main()
