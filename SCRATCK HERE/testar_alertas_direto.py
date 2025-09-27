#!/usr/bin/env python3
"""
TESTAR ALERTAS DIRETO
=====================

Testar o endpoint de alertas diretamente.
"""

import requests
import json

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários
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

def testar_endpoint_alertas(session, nome_usuario):
    """Testar endpoint de alertas"""
    print(f"\n🔔 Testando alertas para {nome_usuario}...")
    
    try:
        # Testar endpoint de alertas
        response = session.get(f"{BASE_URL}/api/desenvolvimento/alertas")
        
        print(f"📊 Resposta do endpoint:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alertas funcionando!")
            print(f"   Total de alertas: {len(data)}")
            
            for i, alerta in enumerate(data):
                print(f"   {i+1}. {alerta.get('titulo')}: {alerta.get('mensagem')}")
                print(f"      Tipo: {alerta.get('tipo')} - Count: {alerta.get('count')}")
            
            return data
        else:
            try:
                error_data = response.json()
                print(f"❌ Erro: {error_data}")
            except:
                print(f"❌ Erro texto: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 TESTAR ALERTAS DIRETO")
    print("=" * 30)
    
    # 1. Testar alertas para supervisor
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_LAB, "SUPERVISOR LAB")
    if session_supervisor:
        alertas_supervisor = testar_endpoint_alertas(session_supervisor, "SUPERVISOR")
    
    # 2. Testar alertas para usuário
    session_user, user_info = fazer_login(USER_LAB, "USUÁRIO LAB")
    if session_user:
        alertas_usuario = testar_endpoint_alertas(session_user, "USUÁRIO")
    
    # 3. Resultado
    print(f"\n📊 RESULTADO:")
    if 'alertas_supervisor' in locals():
        print(f"   Alertas supervisor: {len(alertas_supervisor)} encontrados")
    if 'alertas_usuario' in locals():
        print(f"   Alertas usuário: {len(alertas_usuario)} encontrados")

if __name__ == "__main__":
    main()
