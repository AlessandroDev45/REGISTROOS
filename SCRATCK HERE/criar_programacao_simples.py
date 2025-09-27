#!/usr/bin/env python3
"""
CRIAR PROGRAMAÇÃO SIMPLES
=========================

Criar programação diretamente no banco para teste.
"""

import sqlite3
from datetime import datetime, timedelta
import requests

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def criar_programacao_direto_banco():
    """Criar programação diretamente no banco"""
    print("🧪 Criando programação diretamente no banco...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se existe OS para usar
        cursor.execute("SELECT id FROM ordens_servico LIMIT 1")
        os_result = cursor.fetchone()
        
        if not os_result:
            print("❌ Nenhuma OS encontrada, criando uma...")
            cursor.execute("""
                INSERT INTO ordens_servico (os_numero, status_os, prioridade, created_at)
                VALUES ('TEST-001', 'ABERTA', 'NORMAL', ?)
            """, (datetime.now(),))
            os_id = cursor.lastrowid
        else:
            os_id = os_result[0]
        
        print(f"📋 Usando OS ID: {os_id}")
        
        # Criar programação
        agora = datetime.now()
        inicio = agora + timedelta(hours=1)
        fim = agora + timedelta(hours=9)
        
        cursor.execute("""
            INSERT INTO programacoes (
                id_ordem_servico, responsavel_id, inicio_previsto, fim_previsto,
                status, criado_por_id, observacoes, created_at, updated_at,
                historico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            os_id, 1, inicio, fim, 'ENVIADA', 1,
            'Programação teste criada diretamente no banco',
            agora, agora,
            f'[CRIAÇÃO] Programação criada para teste em {agora.strftime("%d/%m/%Y %H:%M")}'
        ))
        
        prog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Programação criada! ID: {prog_id}")
        return prog_id
        
    except Exception as e:
        print(f"❌ Erro ao criar programação: {e}")
        return None

def verificar_programacao(prog_id):
    """Verificar se a programação foi criada"""
    print(f"\n🔍 Verificando programação {prog_id}...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, responsavel_id, status, observacoes, historico
            FROM programacoes WHERE id = ?
        """, (prog_id,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Programação encontrada:")
            print(f"   ID: {result[0]}")
            print(f"   Responsável ID: {result[1]}")
            print(f"   Status: {result[2]}")
            print(f"   Observações: {result[3]}")
            print(f"   Histórico: {result[4]}")
            conn.close()
            return True
        else:
            print(f"❌ Programação não encontrada")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_dashboard():
    """Testar dashboard"""
    print(f"\n🔍 Testando dashboard...")
    
    session = requests.Session()
    
    # Login
    response = session.post(LOGIN_URL, json=ADMIN_USER)
    if response.status_code != 200:
        print("❌ Erro no login")
        return False
    
    # Testar endpoint
    response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes-v2")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Resposta do dashboard: {data}")
        
        count = data.get('count', 0)
        if count > 0:
            print(f"✅ Dashboard funcionando! {count} programações")
            return True
        else:
            print(f"❌ Dashboard vazio")
            return False
    else:
        print(f"❌ Erro no dashboard: {response.status_code}")
        return False

def main():
    """Função principal"""
    print("🔧 CRIAR PROGRAMAÇÃO SIMPLES")
    print("=" * 35)
    
    # 1. Criar programação no banco
    prog_id = criar_programacao_direto_banco()
    if not prog_id:
        return
    
    # 2. Verificar se foi criada
    banco_ok = verificar_programacao(prog_id)
    
    # 3. Testar dashboard
    dashboard_ok = testar_dashboard()
    
    # 4. Resumo
    print(f"\n📊 RESUMO:")
    print(f"   Programação criada: {'✅' if prog_id else '❌'}")
    print(f"   Verificada no banco: {'✅' if banco_ok else '❌'}")
    print(f"   Aparece no dashboard: {'✅' if dashboard_ok else '❌'}")
    
    if prog_id and banco_ok and dashboard_ok:
        print(f"\n🎉 SUCESSO! Dashboard funcionando perfeitamente!")
        print(f"✅ PROBLEMA DO DASHBOARD RESOLVIDO!")
    else:
        print(f"\n⚠️ Ainda há problemas a resolver")

if __name__ == "__main__":
    main()
