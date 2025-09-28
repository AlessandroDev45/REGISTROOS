#!/usr/bin/env python3
"""
Teste específico para verificar se a aprovação automática de programação está funcionando
quando um apontamento é aprovado pelo supervisor.
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
HEADERS = {"Content-Type": "application/json"}

def fazer_login():
    """Fazer login e obter token"""
    login_data = {
        "username": "admin",  # Ajuste conforme necessário
        "password": "admin123"  # Ajuste conforme necessário
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, headers=HEADERS)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def buscar_programacao_concluida(auth_headers):
    """Buscar uma programação com status CONCLUIDA"""
    try:
        response = requests.get(f"{BASE_URL}/pcp/programacoes", headers=auth_headers)
        if response.status_code == 200:
            programacoes = response.json()
            for prog in programacoes:
                if prog.get('status') == 'CONCLUIDA':
                    return prog
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar programações: {e}")
        return None

def buscar_apontamento_por_os(os_numero, auth_headers):
    """Buscar apontamento pela OS"""
    try:
        response = requests.get(f"{BASE_URL}/desenvolvimento/apontamentos", headers=auth_headers)
        if response.status_code == 200:
            apontamentos = response.json()
            for apt in apontamentos:
                if apt.get('numero_os') == os_numero and not apt.get('aprovado_supervisor'):
                    return apt
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar apontamentos: {e}")
        return None

def testar_aprovacao_automatica():
    """Testar aprovação automática de programação"""
    print("🧪 Testando aprovação automática de programação...")
    
    # 1. Fazer login
    auth_headers = fazer_login()
    if not auth_headers:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado com sucesso")
    
    # 2. Buscar uma programação CONCLUIDA
    programacao = buscar_programacao_concluida(auth_headers)
    if not programacao:
        print("⚠️ Nenhuma programação CONCLUIDA encontrada")
        return
    
    print(f"📋 Programação CONCLUIDA encontrada:")
    print(f"   ID: {programacao['id']}")
    print(f"   OS: {programacao.get('os_numero')}")
    print(f"   Status: {programacao['status']}")
    
    # 3. Buscar apontamento relacionado à OS
    apontamento = buscar_apontamento_por_os(programacao.get('os_numero'), auth_headers)
    if not apontamento:
        print(f"⚠️ Nenhum apontamento não aprovado encontrado para OS {programacao.get('os_numero')}")
        return
    
    print(f"📝 Apontamento encontrado:")
    print(f"   ID: {apontamento['id']}")
    print(f"   OS: {apontamento['numero_os']}")
    print(f"   Aprovado: {apontamento.get('aprovado_supervisor', False)}")
    
    # 4. Aprovar o apontamento
    print("👨‍💼 Aprovando apontamento...")
    try:
        response = requests.put(
            f"{BASE_URL}/desenvolvimento/apontamentos/{apontamento['id']}/aprovar",
            json={
                "aprovado_supervisor": True,
                "observacoes_aprovacao": "Teste de aprovação automática"
            },
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
                
                # 5. Verificar no banco se realmente foi aprovada
                print("🔍 Verificando status no banco...")
                response = requests.get(f"{BASE_URL}/pcp/programacoes/{programacao['id']}", headers=auth_headers)
                if response.status_code == 200:
                    prog_atualizada = response.json()
                    if prog_atualizada.get('status') == 'APROVADA':
                        print("✅ CONFIRMADO! Programação está APROVADA no banco")
                    else:
                        print(f"❌ ERRO! Programação ainda está {prog_atualizada.get('status')} no banco")
                else:
                    print(f"⚠️ Erro ao verificar programação: {response.status_code}")
                
            else:
                print("❌ FALHA! Programação NÃO foi aprovada automaticamente")
                print("   Resposta da API:", json.dumps(resultado, indent=2))
        else:
            print(f"❌ Erro ao aprovar apontamento: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def verificar_logs_backend():
    """Verificar se há logs no backend"""
    print("\n📋 INSTRUÇÕES PARA DEBUG:")
    print("1. Verifique os logs do backend para mensagens como:")
    print("   🔍 Buscando programação para OS: [numero]")
    print("   ✅ Programação encontrada: ID [id], Status: [status]")
    print("   ✅ Programação [id] aprovada automaticamente!")
    print("   ⚠️ Nenhuma programação CONCLUIDA encontrada para OS [numero]")
    print("   ❌ Erro ao aprovar programação automaticamente: [erro]")
    print("\n2. Se não aparecer nenhum log, o problema pode ser:")
    print("   - Programação não está com status CONCLUIDA")
    print("   - OS do apontamento não corresponde à OS da programação")
    print("   - Erro na query de busca da programação")

if __name__ == "__main__":
    testar_aprovacao_automatica()
    verificar_logs_backend()
