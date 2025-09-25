#!/usr/bin/env python3
"""
Teste do fluxo completo de busca de OS:
1. SELECT * FROM ordens_servico WHERE os_numero = ?
2. Se não existir, rodar scraping
3. Aguardar retorno
4. Nova SELECT * FROM ordens_servico
"""

import sqlite3
import requests
import json

def verificar_os_no_banco(os_numero):
    """Verifica se a OS existe no banco"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero = ?", (os_numero,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print(f"✅ OS {os_numero} encontrada no banco (ID: {result[0]})")
            return True
        else:
            print(f"❌ OS {os_numero} NÃO encontrada no banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def testar_endpoint_os(session, os_numero):
    """Testa o endpoint de busca de OS"""
    try:
        print(f"\n🔍 Testando endpoint para OS: {os_numero}")
        response = session.get(f"http://localhost:8000/api/desenvolvimento/formulario/os/{os_numero}", timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint retornou sucesso!")
            print(f"📋 Dados retornados:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Número: {data.get('numero_os')}")
            print(f"   - Cliente: {data.get('cliente')}")
            print(f"   - Equipamento: {data.get('equipamento')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Fonte: {data.get('fonte', 'banco')}")
            return True
        else:
            print(f"❌ Endpoint falhou: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no endpoint: {e}")
        return False

def fazer_login_simples():
    """Login básico para teste"""
    session = requests.Session()
    
    # Tentar com diferentes credenciais
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "user.pcp@registroos.com", "password": "123456"},
        {"username": "supervisor.pcp@registroos.com", "password": "123456"},
    ]
    
    for cred in credenciais:
        try:
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            if response.status_code == 200:
                print(f"✅ Login OK: {cred['username']}")
                return session
        except:
            continue
    
    print("❌ Nenhum login funcionou")
    return None

def main():
    """Teste principal"""
    print("🚀 TESTE DO FLUXO COMPLETO DE BUSCA DE OS")
    print("=" * 50)
    
    # OS para testar (que provavelmente não existe)
    os_numero = "99999"
    
    print(f"\n1️⃣ VERIFICANDO OS {os_numero} NO BANCO...")
    os_existe_antes = verificar_os_no_banco(os_numero)
    
    print(f"\n2️⃣ FAZENDO LOGIN...")
    session = fazer_login_simples()
    if not session:
        print("❌ Teste interrompido - sem login")
        return
    
    print(f"\n3️⃣ TESTANDO ENDPOINT DE BUSCA...")
    sucesso = testar_endpoint_os(session, os_numero)
    
    print(f"\n4️⃣ VERIFICANDO OS NO BANCO APÓS ENDPOINT...")
    os_existe_depois = verificar_os_no_banco(os_numero)
    
    print(f"\n" + "=" * 50)
    print("📊 RESULTADO DO TESTE:")
    print(f"   OS existia antes: {'✅' if os_existe_antes else '❌'}")
    print(f"   Endpoint funcionou: {'✅' if sucesso else '❌'}")
    print(f"   OS existe depois: {'✅' if os_existe_depois else '❌'}")
    
    if not os_existe_antes and sucesso and os_existe_depois:
        print("\n🎉 FLUXO COMPLETO FUNCIONANDO!")
        print("   ✅ OS não existia")
        print("   ✅ Scraping executado")
        print("   ✅ OS criada no banco")
    elif os_existe_antes and sucesso:
        print("\n✅ BUSCA NO BANCO FUNCIONANDO!")
        print("   ✅ OS encontrada no banco")
        print("   ✅ Dados retornados corretamente")
    else:
        print("\n⚠️ VERIFICAR CONFIGURAÇÃO")
        print("   - Arquivo .env pode estar faltando")
        print("   - Credenciais de scraping podem estar incorretas")

if __name__ == "__main__":
    main()
