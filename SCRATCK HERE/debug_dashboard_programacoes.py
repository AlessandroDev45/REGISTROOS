#!/usr/bin/env python3
"""
DEBUG DASHBOARD PROGRAMAÇÕES
===========================

Debugar por que as programações não aparecem no dashboard do colaborador.
"""

import requests
import sqlite3

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login como admin...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=ADMIN_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def verificar_usuario_logado(session):
    """Verificar dados do usuário logado"""
    print("\n🔍 Verificando dados do usuário logado...")
    
    try:
        response = session.get(f"{BASE_URL}/api/me")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Usuário logado:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Nome: {user_data.get('nome_completo')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Privilégio: {user_data.get('privilege_level')}")
            return user_data.get('id')
        else:
            print(f"❌ Erro ao buscar dados do usuário: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_programacoes_banco(user_id):
    """Verificar programações no banco de dados"""
    print(f"\n🔍 Verificando programações no banco para usuário ID {user_id}...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todas as programações
        cursor.execute("""
            SELECT id, responsavel_id, status, observacoes, historico
            FROM programacoes 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        todas_programacoes = cursor.fetchall()
        
        print(f"📋 Últimas 10 programações no banco:")
        for prog in todas_programacoes:
            print(f"   ID {prog[0]}: responsável_id={prog[1]}, status={prog[2]}")
        
        # Buscar programações do usuário específico
        cursor.execute("""
            SELECT id, responsavel_id, status, observacoes, historico
            FROM programacoes 
            WHERE responsavel_id = ?
            ORDER BY id DESC
        """, (user_id,))
        
        programacoes_usuario = cursor.fetchall()
        
        print(f"\n📋 Programações do usuário {user_id}:")
        if programacoes_usuario:
            for prog in programacoes_usuario:
                print(f"   ID {prog[0]}: status={prog[2]}")
                print(f"      Histórico: {prog[4] or 'Vazio'}")
        else:
            print("   ❌ Nenhuma programação encontrada para este usuário")
        
        conn.close()
        return len(programacoes_usuario)
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return 0

def verificar_endpoint_dashboard(session):
    """Verificar endpoint do dashboard"""
    print(f"\n🔍 Verificando endpoint /api/desenvolvimento/minhas-programacoes...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            programacoes = response.json()
            print(f"📋 Programações retornadas: {len(programacoes)}")
            
            for i, prog in enumerate(programacoes):
                print(f"   {i+1}. ID {prog.get('id')}: {prog.get('status')} - {prog.get('os_numero')}")
                
            return len(programacoes)
        else:
            print(f"❌ Erro na resposta: {response.text}")
            return 0
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0

def criar_programacao_teste(session, user_id):
    """Criar uma programação de teste atribuída ao usuário"""
    print(f"\n🧪 Criando programação de teste para usuário {user_id}...")
    
    try:
        # Buscar uma OS
        response = session.get(f"{BASE_URL}/api/os/")
        if response.status_code != 200:
            print("❌ Erro ao buscar OSs")
            return None
            
        oss = response.json().get('data', [])
        if not oss:
            print("❌ Nenhuma OS encontrada")
            return None
            
        os_teste = oss[0]
        
        # Criar programação via atribuição (que deveria funcionar)
        dados_atribuicao = {
            "responsavel_id": user_id,
            "setor_destino": "MECANICA",
            "departamento_destino": "PRODUCAO",
            "data_inicio": "2025-01-15T08:00:00",
            "data_fim": "2025-01-15T17:00:00",
            "observacoes": "Teste de debug dashboard"
        }
        
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/atribuir", json=dados_atribuicao)
        
        if response.status_code == 200:
            data = response.json()
            programacao_id = data.get('id')
            print(f"✅ Programação criada! ID: {programacao_id}")
            return programacao_id
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 DEBUG DASHBOARD PROGRAMAÇÕES")
    print("=" * 50)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Verificar usuário logado
    user_id = verificar_usuario_logado(session)
    if not user_id:
        return
    
    # 3. Verificar programações no banco
    count_banco = verificar_programacoes_banco(user_id)
    
    # 4. Verificar endpoint dashboard
    count_endpoint = verificar_endpoint_dashboard(session)
    
    # 5. Se não há programações, criar uma
    if count_banco == 0:
        print(f"\n💡 Criando programação de teste...")
        programacao_id = criar_programacao_teste(session, user_id)
        
        if programacao_id:
            # Verificar novamente
            print(f"\n🔄 Verificando novamente após criação...")
            verificar_programacoes_banco(user_id)
            verificar_endpoint_dashboard(session)
    
    print(f"\n📊 RESUMO:")
    print(f"   Programações no banco: {count_banco}")
    print(f"   Programações no endpoint: {count_endpoint}")
    
    if count_banco > 0 and count_endpoint == 0:
        print("⚠️ PROBLEMA: Programações existem no banco mas não aparecem no endpoint")
        print("💡 Verifique a query SQL do endpoint")
    elif count_banco == 0:
        print("ℹ️ Nenhuma programação atribuída ao usuário")
    else:
        print("✅ Tudo funcionando corretamente")

if __name__ == "__main__":
    main()
