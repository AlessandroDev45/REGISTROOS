#!/usr/bin/env python3
"""
TESTAR ALERTAS E HORÁRIOS
=========================

Testar problemas específicos de alertas e horários divergentes.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}
SUPERVISOR_LAB = {"username": "supervisor.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"}
USER_LAB = {"username": "user.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"}

def fazer_login(usuario, nome_usuario):
    """Fazer login e obter sessão"""
    print(f"🔐 Fazendo login como {nome_usuario}...")
    
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

def criar_programacao_com_horarios_especificos(session):
    """Criar programação com horários específicos (4.4h)"""
    print(f"\n📋 Criando programação com 4.4h específicas...")
    
    # Horários específicos: 10:30 AM por 4h24min
    agora = datetime.now()
    inicio = agora.replace(hour=10, minute=30, second=0, microsecond=0)
    fim = inicio + timedelta(hours=4, minutes=24)  # 4.4 horas
    
    dados_programacao = {
        "id_ordem_servico": 1,
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "observacoes": "Programação OS 000012345 - 4.4h - TESTES INICIAIS, TESTES ARMADURA",
        "id_setor": None,
        "prioridade": "ALTA"
    }
    
    print(f"⏰ Horários programados:")
    print(f"   Início: {inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Fim: {fim.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Duração: 4h24min (4.4h)")
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=dados_programacao)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada! ID: {prog_id}")
            return prog_id, inicio, fim
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None, None

def verificar_alertas_supervisor(session):
    """Verificar se há alertas para supervisor"""
    print(f"\n🔔 Verificando alertas para supervisor...")
    
    try:
        # Verificar se há endpoint de alertas/notificações
        response = session.get(f"{BASE_URL}/api/alertas")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📢 Supervisor tem {len(data)} alertas")
            return data
        elif response.status_code == 404:
            print(f"⚠️ Endpoint de alertas não existe")
            return []
        else:
            print(f"❌ Erro ao buscar alertas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def reatribuir_com_horarios_corretos(session, prog_id, inicio_original, fim_original):
    """Reatribuir mantendo horários originais"""
    print(f"\n🔄 Reatribuindo com horários corretos...")
    
    print(f"⏰ Horários que DEVERIAM ser mantidos:")
    print(f"   Início: {inicio_original.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Fim: {fim_original.strftime('%d/%m/%Y %H:%M')}")
    
    dados_reatribuicao = {
        "responsavel_id": 2,  # ID do usuário laboratório
        "setor_destino": "LABORATORIO DE ENSAIOS ELETRICOS",
        "departamento_destino": "TRANSFORMADORES",
        "data_inicio": inicio_original.isoformat(),  # Manter horário original
        "data_fim": fim_original.isoformat(),        # Manter horário original
        "observacoes": "TESTES INICIAIS, TESTES ARMADURA - Horários mantidos"
    }
    
    try:
        response = session.patch(f"{BASE_URL}/api/pcp/programacoes/{prog_id}/reatribuir", json=dados_reatribuicao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação reatribuída!")
            print(f"   ID: {data.get('id')}")
            print(f"   Novo responsável: {data.get('novo_responsavel_id')}")
            return True
        else:
            print(f"❌ Erro ao reatribuir: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_horarios_dashboard(session):
    """Verificar se horários estão corretos no dashboard"""
    print(f"\n📊 Verificando horários no dashboard...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 0:
                prog = data[0]  # Primeira programação
                inicio = prog.get('inicio_previsto')
                fim = prog.get('fim_previsto')
                
                print(f"⏰ Horários no dashboard:")
                print(f"   Início: {inicio}")
                print(f"   Fim: {fim}")
                
                if inicio and fim:
                    inicio_dt = datetime.fromisoformat(inicio.replace('Z', ''))
                    fim_dt = datetime.fromisoformat(fim.replace('Z', ''))
                    duracao = fim_dt - inicio_dt
                    
                    print(f"   Duração: {duracao}")
                    
                    # Verificar se duração é aproximadamente 4.4h
                    duracao_horas = duracao.total_seconds() / 3600
                    print(f"   Duração em horas: {duracao_horas:.2f}h")
                    
                    if abs(duracao_horas - 4.4) < 0.1:  # Tolerância de 6 minutos
                        print(f"✅ Horários corretos (4.4h)")
                        return True
                    else:
                        print(f"❌ Horários incorretos (deveria ser 4.4h)")
                        return False
                else:
                    print(f"❌ Horários não encontrados")
                    return False
            else:
                print(f"❌ Nenhuma programação no dashboard")
                return False
                
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_alertas_usuario(session):
    """Verificar se há alertas para usuário"""
    print(f"\n🔔 Verificando alertas para usuário...")
    
    try:
        # Verificar se há endpoint de alertas/notificações
        response = session.get(f"{BASE_URL}/api/alertas")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📢 Usuário tem {len(data)} alertas")
            return data
        elif response.status_code == 404:
            print(f"⚠️ Endpoint de alertas não existe")
            return []
        else:
            print(f"❌ Erro ao buscar alertas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 TESTAR ALERTAS E HORÁRIOS")
    print("=" * 35)
    
    # 1. PCP cria programação com horários específicos
    session_admin, admin_info = fazer_login(ADMIN_USER, "ADMIN/PCP")
    if not session_admin:
        return
    
    prog_id, inicio_original, fim_original = criar_programacao_com_horarios_especificos(session_admin)
    if not prog_id:
        return
    
    # 2. Supervisor verifica alertas
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_LAB, "SUPERVISOR LAB")
    if not session_supervisor:
        return
    
    alertas_supervisor = verificar_alertas_supervisor(session_supervisor)
    
    # 3. Supervisor reatribui mantendo horários
    reatribuicao_ok = reatribuir_com_horarios_corretos(session_supervisor, prog_id, inicio_original, fim_original)
    
    # 4. Usuário verifica alertas
    session_user, user_info = fazer_login(USER_LAB, "USUÁRIO LAB")
    if not session_user:
        return
    
    alertas_usuario = verificar_alertas_usuario(session_user)
    
    # 5. Usuário verifica horários no dashboard
    horarios_corretos = verificar_horarios_dashboard(session_user)
    
    # 6. Relatório final
    print(f"\n📊 RELATÓRIO FINAL:")
    print(f"   1. Programação criada com 4.4h: ✅")
    print(f"   2. Alertas para supervisor: {'✅' if len(alertas_supervisor) > 0 else '❌ (não implementado)'}")
    print(f"   3. Reatribuição funcionou: {'✅' if reatribuicao_ok else '❌'}")
    print(f"   4. Alertas para usuário: {'✅' if len(alertas_usuario) > 0 else '❌ (não implementado)'}")
    print(f"   5. Horários corretos no dashboard: {'✅' if horarios_corretos else '❌'}")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    if len(alertas_supervisor) == 0:
        print(f"   - Implementar sistema de alertas para supervisores")
    if len(alertas_usuario) == 0:
        print(f"   - Implementar sistema de alertas para usuários")
    if not horarios_corretos:
        print(f"   - Corrigir preservação de horários na reatribuição")

if __name__ == "__main__":
    main()
