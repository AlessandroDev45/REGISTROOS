#!/usr/bin/env python3
"""
CRIAR PROGRAMAÇÃO TESTE FINAL
============================

Criar uma programação de teste e verificar se aparece no dashboard.
"""

import requests
import sqlite3
from datetime import datetime, timedelta

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

def criar_programacao_via_api(session):
    """Criar programação via API"""
    print("\n🧪 Criando programação via API...")
    
    # Dados da programação
    agora = datetime.now()
    inicio = agora + timedelta(hours=1)
    fim = agora + timedelta(hours=9)
    
    dados = {
        "responsavel_id": 1,  # Admin
        "setor_destino": "MECANICA",
        "departamento_destino": "PRODUCAO", 
        "data_inicio": inicio.isoformat(),
        "data_fim": fim.isoformat(),
        "observacoes": "Programação teste final para dashboard"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/atribuir", json=dados)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada! ID: {prog_id}")
            return prog_id
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_no_banco(prog_id):
    """Verificar se a programação foi criada no banco"""
    print(f"\n🔍 Verificando programação {prog_id} no banco...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, responsavel_id, status, observacoes FROM programacoes WHERE id = ?", (prog_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Programação encontrada no banco:")
            print(f"   ID: {result[0]}")
            print(f"   Responsável ID: {result[1]}")
            print(f"   Status: {result[2]}")
            print(f"   Observações: {result[3]}")
            conn.close()
            return True
        else:
            print(f"❌ Programação {prog_id} não encontrada no banco")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def testar_dashboard(session):
    """Testar se aparece no dashboard"""
    print(f"\n🔍 Testando dashboard...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes-v2")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Resposta do dashboard: {data}")
            
            count = data.get('count', 0)
            if count > 0:
                print(f"✅ Dashboard funcionando! {count} programações encontradas")
                return True
            else:
                print(f"❌ Dashboard vazio")
                return False
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CRIAR PROGRAMAÇÃO TESTE FINAL")
    print("=" * 40)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Criar programação
    prog_id = criar_programacao_via_api(session)
    if not prog_id:
        return
    
    # 3. Verificar no banco
    banco_ok = verificar_no_banco(prog_id)
    
    # 4. Testar dashboard
    dashboard_ok = testar_dashboard(session)
    
    # 5. Resumo
    print(f"\n📊 RESUMO FINAL:")
    print(f"   Programação criada: {'✅' if prog_id else '❌'}")
    print(f"   Encontrada no banco: {'✅' if banco_ok else '❌'}")
    print(f"   Aparece no dashboard: {'✅' if dashboard_ok else '❌'}")
    
    if prog_id and banco_ok and dashboard_ok:
        print(f"\n🎉 SUCESSO TOTAL! O dashboard está funcionando!")
    elif prog_id and banco_ok and not dashboard_ok:
        print(f"\n⚠️ Programação criada mas não aparece no dashboard")
        print(f"   Possível problema no endpoint ou frontend")
    else:
        print(f"\n❌ Falha na criação ou persistência da programação")

if __name__ == "__main__":
    main()
