#!/usr/bin/env python3
"""
DEBUG HORÁRIOS E ALERTAS INTERFACE
==================================

Investigar problemas específicos de horários iguais e alertas não funcionando.
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
SUPERVISOR_MECANICA = {"username": "supervisor.mecanica_dia@registroos.com", "password": "123456"}
USER_MECANICA = {"username": "user.mecanica_dia@registroos.com", "password": "123456"}

def verificar_programacao_banco(os_numero="000021115"):
    """Verificar programação específica no banco"""
    print(f"🔍 Verificando programação OS {os_numero} no banco...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar programação específica
        cursor.execute("""
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto, 
                   p.fim_previsto, p.status, p.observacoes, p.created_at,
                   os.os_numero
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            WHERE os.os_numero = ?
            ORDER BY p.id DESC
            LIMIT 1
        """, (os_numero,))
        
        programacao = cursor.fetchone()
        
        if programacao:
            print(f"📋 Programação encontrada:")
            print(f"   ID: {programacao[0]}")
            print(f"   OS ID: {programacao[1]} (Número: {programacao[8]})")
            print(f"   Responsável ID: {programacao[2]}")
            print(f"   Início: {programacao[3]}")
            print(f"   Fim: {programacao[4]}")
            print(f"   Status: {programacao[5]}")
            print(f"   Observações: {programacao[6]}")
            print(f"   Criado: {programacao[7]}")
            
            # Calcular duração
            if programacao[3] and programacao[4]:
                inicio = datetime.fromisoformat(programacao[3])
                fim = datetime.fromisoformat(programacao[4])
                duracao = fim - inicio
                print(f"   Duração: {duracao}")
                print(f"   Duração em horas: {duracao.total_seconds() / 3600:.2f}h")
            
            return programacao
        else:
            print(f"❌ Programação OS {os_numero} não encontrada")
            return None
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

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
        return None, None

def testar_alertas_detalhado(session, nome_usuario):
    """Testar alertas com detalhes"""
    print(f"\n🔔 Testando alertas para {nome_usuario}...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/alertas")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de alertas funcionando!")
            print(f"   Total de alertas: {len(data)}")
            
            for i, alerta in enumerate(data):
                print(f"   {i+1}. Tipo: {alerta.get('tipo')}")
                print(f"      Título: {alerta.get('titulo')}")
                print(f"      Mensagem: {alerta.get('mensagem')}")
                print(f"      Count: {alerta.get('count')}")
                print(f"      Prioridade: {alerta.get('prioridade')}")
            
            return data
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            print(f"Resposta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def verificar_dashboard_detalhado(session, nome_usuario):
    """Verificar dashboard com detalhes dos horários"""
    print(f"\n📊 Verificando dashboard para {nome_usuario}...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard funcionando!")
            print(f"   Total de programações: {len(data)}")
            
            for i, prog in enumerate(data):
                print(f"\n   📋 Programação {i+1}:")
                print(f"      ID: {prog.get('id')}")
                print(f"      OS: {prog.get('os_numero')}")
                print(f"      Status: {prog.get('status')}")
                print(f"      Responsável: {prog.get('responsavel_nome')}")
                
                inicio = prog.get('inicio_previsto')
                fim = prog.get('fim_previsto')
                print(f"      Início: {inicio}")
                print(f"      Fim: {fim}")
                
                if inicio and fim:
                    try:
                        inicio_dt = datetime.fromisoformat(inicio.replace('Z', ''))
                        fim_dt = datetime.fromisoformat(fim.replace('Z', ''))
                        duracao = fim_dt - inicio_dt
                        duracao_horas = duracao.total_seconds() / 3600
                        
                        print(f"      Duração: {duracao}")
                        print(f"      Duração em horas: {duracao_horas:.2f}h")
                        
                        if duracao_horas == 0:
                            print(f"      ⚠️ PROBLEMA: Duração zero (horários iguais)")
                        elif duracao_horas < 0:
                            print(f"      ⚠️ PROBLEMA: Duração negativa")
                        else:
                            print(f"      ✅ Duração válida")
                    except Exception as e:
                        print(f"      ❌ Erro ao calcular duração: {e}")
                
                print(f"      Observações: {prog.get('observacoes', '')[:50]}...")
            
            return data
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def verificar_programacoes_supervisor(session):
    """Verificar programações do supervisor"""
    print(f"\n👥 Verificando programações do supervisor...")
    
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supervisor vê {len(data)} programações")
            
            for i, prog in enumerate(data):
                print(f"   {i+1}. ID: {prog.get('id')} - OS: {prog.get('id_ordem_servico')}")
                print(f"      Status: {prog.get('status')} - Responsável: {prog.get('responsavel_id')}")
                
                inicio = prog.get('inicio_previsto')
                fim = prog.get('fim_previsto')
                if inicio and fim:
                    print(f"      Início: {inicio}")
                    print(f"      Fim: {fim}")
            
            return data
        else:
            print(f"❌ Erro: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 DEBUG HORÁRIOS E ALERTAS INTERFACE")
    print("=" * 45)
    
    # 1. Verificar dados no banco
    programacao_banco = verificar_programacao_banco("000021115")
    
    # 2. Testar supervisor
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_MECANICA, "SUPERVISOR MECANICA")
    if session_supervisor:
        alertas_supervisor = testar_alertas_detalhado(session_supervisor, "SUPERVISOR")
        programacoes_supervisor = verificar_programacoes_supervisor(session_supervisor)
    
    # 3. Testar usuário
    session_user, user_info = fazer_login(USER_MECANICA, "USUÁRIO MECANICA")
    if session_user:
        alertas_usuario = testar_alertas_detalhado(session_user, "USUÁRIO")
        dashboard_usuario = verificar_dashboard_detalhado(session_user, "USUÁRIO")
    
    # 4. Análise final
    print(f"\n📊 ANÁLISE DOS PROBLEMAS:")
    
    print(f"\n🔔 ALERTAS:")
    if 'alertas_supervisor' in locals():
        print(f"   Supervisor: {len(alertas_supervisor)} alertas (backend funcionando)")
    if 'alertas_usuario' in locals():
        print(f"   Usuário: {len(alertas_usuario)} alertas (backend funcionando)")
    print(f"   ⚠️ Se não aparecem na interface: problema no frontend")
    
    print(f"\n⏰ HORÁRIOS:")
    if programacao_banco:
        inicio_banco = programacao_banco[3]
        fim_banco = programacao_banco[4]
        if inicio_banco == fim_banco:
            print(f"   ❌ PROBLEMA: Horários iguais no banco ({inicio_banco})")
            print(f"   💡 CAUSA: Reatribuição não preserva duração original")
        else:
            print(f"   ✅ Horários diferentes no banco")
    
    print(f"\n💡 SOLUÇÕES NECESSÁRIAS:")
    print(f"   1. Corrigir reatribuição para preservar duração")
    print(f"   2. Verificar se frontend consome endpoint de alertas")
    print(f"   3. Implementar notificações visuais na interface")

if __name__ == "__main__":
    main()
