#!/usr/bin/env python3
"""
TESTE FINAL DASHBOARD
====================

Teste final do dashboard após todas as correções.
"""

import requests

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

def testar_dashboard(session):
    """Testar dashboard final"""
    print("\n🔍 Testando dashboard final...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Tipo de resposta: {type(data)}")
            print(f"📋 Quantidade de programações: {len(data) if isinstance(data, list) else 'Não é lista'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"\n✅ SUCESSO! Dashboard funcionando!")
                print(f"📋 Programações encontradas:")
                
                for i, prog in enumerate(data):
                    print(f"   {i+1}. ID: {prog.get('id')}")
                    print(f"      Status: {prog.get('status')}")
                    print(f"      Observações: {prog.get('observacoes', '')[:50]}...")
                    print(f"      OS: {prog.get('os_numero')}")
                
                return True
            else:
                print(f"❌ Dashboard vazio")
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
    print("🔧 TESTE FINAL DASHBOARD")
    print("=" * 30)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Testar dashboard
    dashboard_ok = testar_dashboard(session)
    
    # 3. Resultado final
    print(f"\n📊 RESULTADO FINAL:")
    if dashboard_ok:
        print(f"🎉 DASHBOARD FUNCIONANDO PERFEITAMENTE!")
        print(f"✅ PROBLEMA RESOLVIDO COM SUCESSO!")
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"   1. Testar no frontend")
        print(f"   2. Verificar integração completa")
        print(f"   3. Validar com usuários reais")
    else:
        print(f"❌ Dashboard ainda não está funcionando")
        print(f"⚠️ Necessário mais investigação")

if __name__ == "__main__":
    main()
