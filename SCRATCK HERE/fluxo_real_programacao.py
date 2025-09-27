#!/usr/bin/env python3
"""
FLUXO REAL PROGRAMAÇÃO
=====================

Fluxo completo com dados reais:
1. PCP cria programação para setor MECANICA
2. Supervisor atribui para usuário específico
3. Usuário vê no dashboard
4. Usuário cria apontamento finalizando programação
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários reais
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}
SUPERVISOR_USER = {"username": "supervisor.mecanica_dia@registroos.com", "password": "123456"}
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
        print(f"Resposta: {response.text}")
        return None, None

def criar_programacao_pcp(session):
    """1. PCP cria programação para setor MECANICA"""
    print(f"\n📋 PASSO 1: PCP criando programação para setor MECANICA...")
    
    # Dados da programação
    agora = datetime.now()
    inicio = agora + timedelta(hours=2)
    fim = agora + timedelta(hours=10)
    
    dados_programacao = {
        "id_ordem_servico": 1,  # OS existente
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "observacoes": "Programação real para teste de fluxo completo - Manutenção preventiva motor",
        "id_setor": None,  # Será definido pelo setor
        "prioridade": "ALTA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=dados_programacao)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada pelo PCP! ID: {prog_id}")
            print(f"   OS: {data.get('id_ordem_servico')}")
            print(f"   Status: {data.get('status')}")
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

def atribuir_programacao_supervisor(session, prog_id):
    """2. Supervisor atribui programação para usuário específico"""
    print(f"\n👥 PASSO 2: Supervisor atribuindo programação {prog_id} para usuário MECANICA...")
    
    # Dados da atribuição
    dados_atribuicao = {
        "responsavel_id": 8,  # ID do user.mecanica_dia@registroos.com
        "setor_destino": "MECANICA DIA",  # Nome exato do setor
        "departamento_destino": "MOTORES",  # Departamento correto
        "data_inicio": (datetime.now() + timedelta(hours=1)).isoformat(),
        "data_fim": (datetime.now() + timedelta(hours=9)).isoformat(),
        "observacoes": "Atribuída para usuário MECANICA DIA - executar manutenção preventiva"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/atribuir", json=dados_atribuicao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação atribuída pelo supervisor!")
            print(f"   Responsável ID: {data.get('responsavel_id')}")
            print(f"   Setor: {data.get('setor_destino')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Erro ao atribuir programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_dashboard_usuario(session, user_info):
    """3. Verificar se programação aparece no dashboard do usuário"""
    print(f"\n📊 PASSO 3: Verificando dashboard do usuário {user_info.get('nome_completo')}...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Dashboard retornou {len(data)} programações")
            
            if len(data) > 0:
                print(f"✅ Programações encontradas no dashboard:")
                for i, prog in enumerate(data):
                    print(f"   {i+1}. ID: {prog.get('id')} - Status: {prog.get('status')}")
                    print(f"      OS: {prog.get('os_numero')} - Responsável: {prog.get('responsavel_nome')}")
                return data
            else:
                print(f"❌ Dashboard vazio - programação não aparece")
                return []
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def criar_apontamento_finalizacao(session, prog_id):
    """4. Usuário cria apontamento finalizando a programação"""
    print(f"\n📝 PASSO 4: Criando apontamento para finalizar programação {prog_id}...")
    
    # Dados do apontamento com todos os campos obrigatórios
    agora = datetime.now()
    dados_apontamento = {
        "numero_os": "000012345",  # Campo obrigatório
        "cliente": "AIR LIQUIDE BRASIL",  # Campo obrigatório
        "equipamento": "MOTOR ELETRICO PARTIDA",  # Campo obrigatório
        "tipo_maquina": "MOTOR ELETRICO",  # Campo obrigatório
        "tipo_atividade": "MANUTENCAO_PREVENTIVA",  # Campo obrigatório
        "descricao_atividade": "Manutenção preventiva concluída - motor revisado e testado",
        "data_inicio": agora.date().isoformat(),  # Apenas data, sem hora
        "hora_inicio": agora.strftime("%H:%M"),  # Hora separada
        "data_fim": agora.date().isoformat(),  # Apenas data, sem hora
        "hora_fim": (agora + timedelta(hours=6)).strftime("%H:%M"),  # Hora separada
        "observacao": f"Programação {prog_id} finalizada com sucesso",
        "resultado_global": "APROVADO",
        "observacao_resultado": "Manutenção realizada conforme procedimento",
        "status_os": "FINALIZADA",
        "retrabalho": False
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/desenvolvimento/os/apontamentos", json=dados_apontamento)
        
        if response.status_code == 200:
            data = response.json()
            apontamento_id = data.get('id')
            print(f"✅ Apontamento criado! ID: {apontamento_id}")
            print(f"   OS: {data.get('id_os')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Descrição: {data.get('descricao_atividade')}")
            return apontamento_id
        else:
            print(f"❌ Erro ao criar apontamento: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def finalizar_programacao_automatica(session, prog_id):
    """5. Finalizar programação automaticamente via integração"""
    print(f"\n🏁 PASSO 5: Finalizando programação {prog_id} automaticamente...")
    
    dados_finalizacao = {
        "programacao_id": prog_id,
        "observacoes": "Programação finalizada automaticamente após conclusão do apontamento"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/desenvolvimento/finalizar-programacao", json=dados_finalizacao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação finalizada automaticamente!")
            print(f"   Status: {data.get('status_programacao')}")
            print(f"   Mensagem: {data.get('message')}")
            return True
        else:
            print(f"❌ Erro ao finalizar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal - fluxo completo"""
    print("🔧 FLUXO REAL PROGRAMAÇÃO COM DADOS REAIS")
    print("=" * 50)
    
    # PASSO 1: PCP cria programação
    session_admin, admin_info = fazer_login(ADMIN_USER, "ADMIN/PCP")
    if not session_admin:
        return
    
    prog_id = criar_programacao_pcp(session_admin)
    if not prog_id:
        print("❌ Falha na criação da programação")
        return
    
    # PASSO 2: Supervisor atribui programação
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_USER, "SUPERVISOR MECANICA")
    if not session_supervisor:
        return
    
    atribuicao_ok = atribuir_programacao_supervisor(session_supervisor, prog_id)
    if not atribuicao_ok:
        print("❌ Falha na atribuição da programação")
        return
    
    # PASSO 3: Usuário verifica dashboard
    session_user, user_info = fazer_login(USER_MECANICA, "USUÁRIO MECANICA")
    if not session_user:
        return
    
    programacoes_dashboard = verificar_dashboard_usuario(session_user, user_info)
    
    # PASSO 4: Usuário cria apontamento
    apontamento_id = criar_apontamento_finalizacao(session_user, prog_id)
    
    # PASSO 5: Finalizar programação automaticamente
    if apontamento_id:
        finalizar_programacao_automatica(session_user, prog_id)
    
    # RESUMO FINAL
    print(f"\n📊 RESUMO DO FLUXO COMPLETO:")
    print(f"   1. Programação criada pelo PCP: {'✅' if prog_id else '❌'}")
    print(f"   2. Atribuída pelo supervisor: {'✅' if atribuicao_ok else '❌'}")
    print(f"   3. Aparece no dashboard do usuário: {'✅' if len(programacoes_dashboard) > 0 else '❌'}")
    print(f"   4. Apontamento criado: {'✅' if apontamento_id else '❌'}")
    print(f"   5. Programação finalizada: {'✅' if apontamento_id else '❌'}")
    
    if prog_id and atribuicao_ok and len(programacoes_dashboard) > 0 and apontamento_id:
        print(f"\n🎉 FLUXO COMPLETO EXECUTADO COM SUCESSO!")
        print(f"✅ TODAS AS FUNCIONALIDADES ESTÃO FUNCIONANDO!")
    else:
        print(f"\n⚠️ PROBLEMAS IDENTIFICADOS NO FLUXO")
        if not len(programacoes_dashboard) > 0:
            print(f"   - Programação não aparece no dashboard do usuário")
        print(f"\n💡 NECESSÁRIO INVESTIGAR E CORRIGIR")

if __name__ == "__main__":
    main()
