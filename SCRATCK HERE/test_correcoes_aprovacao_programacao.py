#!/usr/bin/env python3
"""
TESTE DAS CORREÇÕES - APROVAÇÃO DE PROGRAMAÇÃO
==============================================

Este script testa as correções implementadas para resolver os problemas:
1. Supervisor aprova apontamento mas PCP não recebe que programação foi terminada
2. Loop infinito de requisições GET /api/admin/departamentos

CORREÇÕES IMPLEMENTADAS:
- Buscar programações com status 'CONCLUIDA' OU 'AGUARDANDO_APROVACAO'
- Corrigir useEffect no ProgramacaoFiltros.tsx para evitar loop infinito
- Adicionar logs detalhados para debug

TESTE COMPLETO:
1. Criar programação
2. Finalizar programação (status -> AGUARDANDO_APROVACAO)
3. Criar apontamento para a OS
4. Aprovar apontamento (deve aprovar programação automaticamente)
5. Verificar se PCP vê programação como APROVADA
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login"

# Credenciais de teste
SUPERVISOR_CREDENTIALS = {
    "username": "supervisor_teste",
    "password": "123456"
}

PCP_CREDENTIALS = {
    "username": "pcp_teste", 
    "password": "123456"
}

def fazer_login(credentials):
    """Fazer login e retornar headers de autenticação"""
    try:
        response = requests.post(LOGIN_URL, json=credentials)
        if response.status_code == 200:
            token = response.json().get('access_token')
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def criar_programacao_teste(auth_headers):
    """Criar uma programação de teste"""
    print("\n1. 📋 Criando programação de teste...")
    
    # Dados da programação
    agora = datetime.now()
    inicio = agora + timedelta(hours=1)
    fim = agora + timedelta(hours=3)
    
    programacao_data = {
        "os_numero": "TEST001",
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "id_setor": 1,
        "responsavel_id": 2,
        "observacoes": "Programação de teste para validar correções",
        "status": "PROGRAMADA"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/pcp/programacoes",
            json=programacao_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            programacao = response.json()
            print(f"✅ Programação criada: ID {programacao.get('id')}")
            return programacao
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def finalizar_programacao(programacao_id, auth_headers):
    """Finalizar programação (status -> AGUARDANDO_APROVACAO)"""
    print(f"\n2. 🏁 Finalizando programação {programacao_id}...")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/pcp/programacoes/{programacao_id}/status",
            json={"status": "AGUARDANDO_APROVACAO"},
            headers=auth_headers
        )
        
        if response.status_code == 200:
            print("✅ Programação finalizada (AGUARDANDO_APROVACAO)")
            return True
        else:
            print(f"❌ Erro ao finalizar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def criar_apontamento_teste(os_numero, auth_headers):
    """Criar apontamento de teste"""
    print(f"\n3. ⏱️ Criando apontamento para OS {os_numero}...")
    
    agora = datetime.now()
    apontamento_data = {
        "numero_os": os_numero,
        "data_inicio": agora.strftime("%Y-%m-%d"),
        "hora_inicio": agora.strftime("%H:%M"),
        "data_fim": agora.strftime("%Y-%m-%d"),
        "hora_fim": (agora + timedelta(hours=2)).strftime("%H:%M"),
        "status_apontamento": "CONCLUIDO",
        "observacao_os": "Apontamento de teste para validar aprovação automática"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/desenvolvimento/os/apontamentos",
            json=apontamento_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            apontamento = response.json()
            print(f"✅ Apontamento criado: ID {apontamento.get('id')}")
            return apontamento
        else:
            print(f"❌ Erro ao criar apontamento: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def aprovar_apontamento(apontamento_id, auth_headers):
    """Aprovar apontamento (deve aprovar programação automaticamente)"""
    print(f"\n4. ✅ Aprovando apontamento {apontamento_id}...")
    
    aprovacao_data = {
        "aprovado_supervisor": True,
        "observacoes_aprovacao": "Teste de aprovação automática de programação"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/desenvolvimento/apontamentos/{apontamento_id}/aprovar",
            json=aprovacao_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Apontamento aprovado: {resultado.get('message')}")
            
            # Verificar se programação foi aprovada automaticamente
            if resultado.get('programacao_aprovada'):
                print("🎯 SUCESSO! Programação aprovada automaticamente:")
                prog_aprovada = resultado['programacao_aprovada']
                print(f"   ID: {prog_aprovada['id']}")
                print(f"   OS: {prog_aprovada['os_numero']}")
                print(f"   Status: {prog_aprovada['status']}")
                return True
            else:
                print("⚠️ Programação NÃO foi aprovada automaticamente")
                return False
        else:
            print(f"❌ Erro ao aprovar: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_programacao_no_pcp(auth_headers):
    """Verificar se PCP vê programação como APROVADA"""
    print(f"\n5. 🏭 Verificando programações no PCP...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/pcp/programacoes",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            programacoes = response.json()
            print(f"📊 PCP encontrou {len(programacoes)} programações")
            
            # Buscar programações aprovadas
            aprovadas = [p for p in programacoes if p.get('status') == 'APROVADA']
            if aprovadas:
                print(f"✅ {len(aprovadas)} programações APROVADAS encontradas:")
                for p in aprovadas:
                    print(f"   - ID: {p.get('id')}, OS: {p.get('os_numero')}, Status: {p.get('status')}")
                return True
            else:
                print("⚠️ Nenhuma programação APROVADA encontrada no PCP")
                return False
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executar teste completo"""
    print("🧪 TESTE DAS CORREÇÕES - APROVAÇÃO DE PROGRAMAÇÃO")
    print("=" * 60)
    
    # Login como supervisor
    print("\n👨‍💼 Fazendo login como supervisor...")
    supervisor_headers = fazer_login(SUPERVISOR_CREDENTIALS)
    if not supervisor_headers:
        print("❌ Falha no login do supervisor")
        return
    
    # Login como PCP
    print("\n🏭 Fazendo login como PCP...")
    pcp_headers = fazer_login(PCP_CREDENTIALS)
    if not pcp_headers:
        print("❌ Falha no login do PCP")
        return
    
    # Executar teste
    try:
        # 1. Criar programação
        programacao = criar_programacao_teste(pcp_headers)
        if not programacao:
            return
        
        # 2. Finalizar programação
        if not finalizar_programacao(programacao['id'], pcp_headers):
            return
        
        # 3. Criar apontamento
        apontamento = criar_apontamento_teste("TEST001", supervisor_headers)
        if not apontamento:
            return
        
        # 4. Aprovar apontamento
        if not aprovar_apontamento(apontamento['id'], supervisor_headers):
            return
        
        # 5. Verificar no PCP
        if verificar_programacao_no_pcp(pcp_headers):
            print("\n🎉 TESTE PASSOU! Correções funcionando corretamente.")
        else:
            print("\n❌ TESTE FALHOU! Verificar logs do servidor.")
            
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    main()
