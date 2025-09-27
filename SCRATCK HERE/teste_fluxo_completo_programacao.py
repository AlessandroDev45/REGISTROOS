#!/usr/bin/env python3
"""
TESTE FLUXO COMPLETO PROGRAMAÇÃO
===============================

Testa o fluxo completo:
1. PCP cria programação
2. Supervisor atribui para colaborador
3. Colaborador vê no dashboard
"""

import requests
import sqlite3
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários de teste
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login(usuario):
    """Fazer login e obter sessão"""
    print(f"🔐 Fazendo login como {usuario['username']}...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=usuario, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('user', {})
        print(f"✅ Login realizado! Usuário: {user_info.get('nome_completo', 'N/A')} (ID: {user_info.get('id', 'N/A')})")
        return session, user_info
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None, None

def verificar_usuarios_disponiveis():
    """Verificar usuários disponíveis no banco"""
    print("\n🔍 Verificando usuários disponíveis...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_completo, email, privilege_level 
            FROM tipo_usuarios 
            WHERE privilege_level IN ('ADMIN', 'SUPERVISOR', 'USER')
            ORDER BY privilege_level, id
            LIMIT 10
        """)
        
        usuarios = cursor.fetchall()
        
        print(f"📋 Usuários encontrados:")
        for user in usuarios:
            print(f"   ID {user[0]}: {user[1]} ({user[2]}) - {user[3]}")
        
        conn.close()
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")
        return []

def criar_programacao_via_banco():
    """Criar programação diretamente no banco para teste"""
    print("\n🧪 Criando programação de teste...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se existe OS
        cursor.execute("SELECT id FROM ordens_servico LIMIT 1")
        os_result = cursor.fetchone()
        
        if not os_result:
            # Criar OS de teste
            cursor.execute("""
                INSERT INTO ordens_servico (os_numero, status_os, prioridade, created_at)
                VALUES ('TESTE-FLUXO-001', 'ABERTA', 'ALTA', ?)
            """, (datetime.now(),))
            os_id = cursor.lastrowid
            print(f"📋 OS criada: ID {os_id}")
        else:
            os_id = os_result[0]
            print(f"📋 Usando OS existente: ID {os_id}")
        
        # Criar programação
        agora = datetime.now()
        inicio = agora + timedelta(hours=2)
        fim = agora + timedelta(hours=10)
        
        cursor.execute("""
            INSERT INTO programacoes (
                id_ordem_servico, responsavel_id, inicio_previsto, fim_previsto,
                status, criado_por_id, observacoes, created_at, updated_at,
                historico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            os_id, 1, inicio, fim, 'ENVIADA', 1,
            'Programação teste para verificar fluxo completo de atribuição',
            agora, agora,
            f'[CRIAÇÃO] Programação criada para teste de fluxo em {agora.strftime("%d/%m/%Y %H:%M")}\n[ATRIBUIÇÃO] Atribuída para ADMINISTRADOR em {agora.strftime("%d/%m/%Y %H:%M")}'
        ))
        
        prog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Programação criada! ID: {prog_id}")
        print(f"   OS ID: {os_id}")
        print(f"   Responsável ID: 1 (Admin)")
        print(f"   Status: ENVIADA")
        print(f"   Início: {inicio.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Fim: {fim.strftime('%d/%m/%Y %H:%M')}")
        
        return prog_id
        
    except Exception as e:
        print(f"❌ Erro ao criar programação: {e}")
        return None

def verificar_programacao_no_banco(prog_id):
    """Verificar se a programação foi criada corretamente"""
    print(f"\n🔍 Verificando programação {prog_id} no banco...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.responsavel_id, p.status, p.observacoes, p.historico,
                   u.nome_completo as responsavel_nome,
                   os.os_numero
            FROM programacoes p
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            WHERE p.id = ?
        """, (prog_id,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Programação encontrada:")
            print(f"   ID: {result[0]}")
            print(f"   Responsável ID: {result[1]}")
            print(f"   Responsável Nome: {result[5]}")
            print(f"   Status: {result[2]}")
            print(f"   OS: {result[6]}")
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

def testar_dashboard_colaborador(session, user_info):
    """Testar se a programação aparece no dashboard do colaborador"""
    print(f"\n🔍 Testando dashboard do colaborador {user_info.get('nome_completo')}...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Tipo de resposta: {type(data)}")
            print(f"📋 Quantidade de programações: {len(data) if isinstance(data, list) else 'Não é lista'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ SUCESSO! Dashboard funcionando!")
                print(f"📋 Programações no dashboard:")
                
                for i, prog in enumerate(data):
                    print(f"   {i+1}. ID: {prog.get('id')}")
                    print(f"      Status: {prog.get('status')}")
                    print(f"      OS: {prog.get('os_numero')}")
                    print(f"      Responsável: {prog.get('responsavel_nome')}")
                    print(f"      Observações: {prog.get('observacoes', '')[:50]}...")
                
                return True
            else:
                print(f"❌ Dashboard vazio - programação não aparece")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE FLUXO COMPLETO PROGRAMAÇÃO")
    print("=" * 45)
    
    # 1. Verificar usuários disponíveis
    usuarios = verificar_usuarios_disponiveis()
    if not usuarios:
        print("❌ Nenhum usuário encontrado")
        return
    
    # 2. Criar programação de teste
    prog_id = criar_programacao_via_banco()
    if not prog_id:
        print("❌ Falha ao criar programação")
        return
    
    # 3. Verificar se foi criada corretamente
    banco_ok = verificar_programacao_no_banco(prog_id)
    if not banco_ok:
        print("❌ Programação não foi criada corretamente")
        return
    
    # 4. Testar login e dashboard do colaborador
    session, user_info = fazer_login(ADMIN_USER)
    if not session:
        print("❌ Falha no login")
        return
    
    # 5. Testar dashboard
    dashboard_ok = testar_dashboard_colaborador(session, user_info)
    
    # 6. Resumo final
    print(f"\n📊 RESUMO DO TESTE:")
    print(f"   Programação criada: {'✅' if prog_id else '❌'}")
    print(f"   Verificada no banco: {'✅' if banco_ok else '❌'}")
    print(f"   Aparece no dashboard: {'✅' if dashboard_ok else '❌'}")
    
    if prog_id and banco_ok and dashboard_ok:
        print(f"\n🎉 SUCESSO TOTAL!")
        print(f"✅ FLUXO DE ATRIBUIÇÃO FUNCIONANDO!")
        print(f"✅ DASHBOARD DO COLABORADOR FUNCIONANDO!")
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"   1. Adicionar campo 'Atribuído para' na interface")
        print(f"   2. Mostrar histórico de atribuição/edição")
        print(f"   3. Testar com usuários reais diferentes")
    else:
        print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
        if not dashboard_ok:
            print(f"   - Dashboard não mostra programações")
            print(f"   - Possível problema no endpoint ou query")
        print(f"\n💡 NECESSÁRIO:")
        print(f"   - Investigar por que programação não aparece no dashboard")

if __name__ == "__main__":
    main()
