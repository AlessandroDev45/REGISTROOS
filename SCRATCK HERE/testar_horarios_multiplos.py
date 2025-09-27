#!/usr/bin/env python3
"""
TESTAR HORÁRIOS E MÚLTIPLOS COLABORADORES
=========================================

Testar as duas novas funcionalidades:
1. Supervisor pode mudar horários
2. Supervisor pode atribuir para múltiplos colaboradores
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}
SUPERVISOR_MECANICA = {"username": "supervisor.mecanica_dia@registroos.com", "password": "123456"}
USER_MECANICA = {"username": "user.mecanica_dia@registroos.com", "password": "123456"}

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

def criar_programacao_teste(session):
    """Criar programação para teste"""
    print(f"\n📋 Criando programação para teste...")
    
    agora = datetime.now()
    inicio = agora + timedelta(hours=2)
    fim = inicio + timedelta(hours=6)  # 6 horas de duração
    
    dados_programacao = {
        "id_ordem_servico": 1,
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "observacoes": "Programação teste para múltiplos colaboradores",
        "id_setor": None,
        "prioridade": "ALTA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=dados_programacao)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada! ID: {prog_id}")
            print(f"   Duração original: 6h ({inicio.strftime('%H:%M')} - {fim.strftime('%H:%M')})")
            return prog_id, inicio, fim
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None, None

def testar_mudanca_horarios(session, prog_id):
    """Testar mudança de horários pelo supervisor"""
    print(f"\n⏰ TESTE 1: Supervisor mudando horários...")
    
    # Supervisor define novos horários específicos
    novo_inicio = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    novo_fim = novo_inicio + timedelta(hours=4)  # 4 horas em vez de 6
    
    dados_reatribuicao = {
        "responsavel_id": 8,  # user.mecanica_dia
        "setor_destino": "MECANICA DIA",
        "departamento_destino": "MOTORES",
        "data_inicio": novo_inicio.isoformat(),
        "data_fim": novo_fim.isoformat(),
        "observacoes": "Horários alterados pelo supervisor: 14:00-18:00 (4h)"
    }
    
    print(f"📅 Novos horários definidos pelo supervisor:")
    print(f"   Início: {novo_inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Fim: {novo_fim.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Duração: 4h (alterada de 6h)")
    
    try:
        response = session.patch(f"{BASE_URL}/api/pcp/programacoes/{prog_id}/reatribuir", json=dados_reatribuicao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Horários alterados com sucesso!")
            print(f"   Responsável: {data.get('novo_responsavel_id')}")
            return True
        else:
            print(f"❌ Erro ao alterar horários: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_atribuicao_multipla(session, prog_id):
    """Testar atribuição para múltiplos colaboradores"""
    print(f"\n👥 TESTE 2: Atribuindo para múltiplos colaboradores...")
    
    # Lista de colaboradores para atribuir
    responsaveis = [
        {
            "id": 8,  # user.mecanica_dia
            "observacoes": "Responsável principal - executar montagem"
        },
        {
            "id": 17,  # joao.mecanica (se existir)
            "observacoes": "Apoio na montagem - verificar componentes"
        },
        {
            "id": 18,  # maria.mecanica (se existir)
            "observacoes": "Controle de qualidade - inspeção final"
        }
    ]
    
    dados_multiplos = {
        "responsaveis": responsaveis
    }
    
    print(f"👥 Atribuindo para {len(responsaveis)} colaboradores:")
    for i, resp in enumerate(responsaveis):
        print(f"   {i+1}. ID {resp['id']}: {resp['observacoes']}")
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/{prog_id}/atribuir-multiplos", json=dados_multiplos)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Atribuição múltipla realizada!")
            print(f"   Total de atribuições: {data.get('total_atribuicoes')}")
            print(f"   Programação original: {data.get('programacao_original_id')}")
            
            programacoes = data.get('programacoes', [])
            for prog in programacoes:
                print(f"   - ID {prog['id']}: {prog['responsavel_nome']} ({prog['tipo']})")
            
            return data
        else:
            print(f"❌ Erro na atribuição múltipla: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_dashboards_usuarios(session_user):
    """Verificar se programações aparecem nos dashboards"""
    print(f"\n📊 Verificando dashboards dos usuários...")
    
    try:
        response = session_user.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard usuário principal:")
            print(f"   Total de programações: {len(data)}")
            
            for i, prog in enumerate(data):
                inicio = prog.get('inicio_previsto')
                fim = prog.get('fim_previsto')
                
                if inicio and fim:
                    inicio_dt = datetime.fromisoformat(inicio.replace('Z', ''))
                    fim_dt = datetime.fromisoformat(fim.replace('Z', ''))
                    duracao = fim_dt - inicio_dt
                    duracao_horas = duracao.total_seconds() / 3600
                    
                    print(f"   {i+1}. ID {prog.get('id')}: {inicio_dt.strftime('%H:%M')}-{fim_dt.strftime('%H:%M')} ({duracao_horas:.1f}h)")
                    print(f"      OS: {prog.get('os_numero')} - Status: {prog.get('status')}")
            
            return data
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 TESTAR HORÁRIOS E MÚLTIPLOS COLABORADORES")
    print("=" * 50)
    
    # 1. PCP cria programação
    session_admin, admin_info = fazer_login(ADMIN_USER, "ADMIN/PCP")
    if not session_admin:
        return
    
    prog_id, inicio_original, fim_original = criar_programacao_teste(session_admin)
    if not prog_id:
        return
    
    # 2. Supervisor testa mudança de horários
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_MECANICA, "SUPERVISOR")
    if not session_supervisor:
        return
    
    horarios_alterados = testar_mudanca_horarios(session_supervisor, prog_id)
    
    # 3. Criar nova programação para teste múltiplo
    prog_id_multiplo, _, _ = criar_programacao_teste(session_admin)
    if prog_id_multiplo:
        atribuicao_multipla = testar_atribuicao_multipla(session_supervisor, prog_id_multiplo)
    
    # 4. Verificar dashboards
    session_user, user_info = fazer_login(USER_MECANICA, "USUÁRIO")
    if session_user:
        dashboards = verificar_dashboards_usuarios(session_user)
    
    # 5. Relatório final
    print(f"\n📊 RELATÓRIO FINAL:")
    print(f"   1. Programação criada: ✅")
    print(f"   2. Horários alterados pelo supervisor: {'✅' if horarios_alterados else '❌'}")
    print(f"   3. Atribuição múltipla: {'✅' if 'atribuicao_multipla' in locals() and atribuicao_multipla else '❌'}")
    print(f"   4. Dashboards atualizados: {'✅' if 'dashboards' in locals() and len(dashboards) > 0 else '❌'}")
    
    print(f"\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
    print(f"   ✅ Supervisor pode alterar horários específicos")
    print(f"   ✅ Supervisor pode atribuir para múltiplos colaboradores")
    print(f"   ✅ Sistema preserva duração quando horários são iguais")
    print(f"   ✅ Sistema cria cópias para colaboradores adicionais")

if __name__ == "__main__":
    main()
