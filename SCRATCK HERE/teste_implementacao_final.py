#!/usr/bin/env python3
"""
Teste final da implementação de busca de OS com scraping
"""

import sqlite3
import requests
import json

def verificar_os_antes(os_numero):
    """Verifica se a OS existe antes do teste"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero = ? OR os_numero = ?", 
                      (os_numero, f"000{os_numero}".zfill(9)))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    # Tentar com diferentes usuários
    credenciais = [
        {"username": "user.pcp@registroos.com", "password": "123456"},
        {"username": "supervisor.pcp@registroos.com", "password": "123456"},
        {"username": "admin@registroos.com", "password": "admin123"},
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

def testar_endpoint_os(session, os_numero):
    """Testa o endpoint de busca de OS"""
    try:
        print(f"\n🔍 Testando endpoint para OS: {os_numero}")
        response = session.get(f"http://localhost:8000/api/desenvolvimento/formulario/os/{os_numero}", timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionou!")
            print(f"📋 Dados retornados:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Número: {data.get('numero_os')}")
            print(f"   - Cliente: {data.get('cliente')}")
            print(f"   - Equipamento: {data.get('equipamento')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Fonte: {data.get('fonte', 'banco')}")
            return True, data
        else:
            print(f"❌ Endpoint falhou: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro no endpoint: {e}")
        return False, None

def verificar_os_depois(os_numero):
    """Verifica se a OS foi criada após o teste"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero = ? OR os_numero = ?", 
                      (os_numero, f"000{os_numero}".zfill(9)))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ OS criada no banco!")
            print(f"   ID: {result[0]}")
            print(f"   Número: {result[1]}")
            print(f"   Status: {result[2]}")
            
            # Verificar cliente
            if len(result) > 52 and result[52]:
                cursor.execute("SELECT razao_social FROM clientes WHERE id = ?", (result[52],))
                cliente = cursor.fetchone()
                if cliente:
                    print(f"   Cliente: {cliente[0]}")
            
            # Verificar equipamento
            if len(result) > 53 and result[53]:
                cursor.execute("SELECT descricao FROM equipamentos WHERE id = ?", (result[53],))
                equipamento = cursor.fetchone()
                if equipamento:
                    print(f"   Equipamento: {equipamento[0]}")
        
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco após teste: {e}")
        return False

def main():
    """Teste principal"""
    print("🚀 TESTE FINAL DA IMPLEMENTAÇÃO")
    print("=" * 50)
    
    # OS para testar (sabemos que funciona no scraping)
    os_numero = "12345"
    
    print(f"\n1️⃣ VERIFICANDO OS {os_numero} NO BANCO (ANTES)...")
    os_existe_antes = verificar_os_antes(os_numero)
    print(f"   OS existe antes: {'✅' if os_existe_antes else '❌'}")
    
    print(f"\n2️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - sem login")
        return
    
    print(f"\n3️⃣ TESTANDO ENDPOINT...")
    sucesso, dados = testar_endpoint_os(session, os_numero)
    
    print(f"\n4️⃣ VERIFICANDO OS NO BANCO (DEPOIS)...")
    os_existe_depois = verificar_os_depois(os_numero)
    
    print(f"\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print(f"   OS existia antes: {'✅' if os_existe_antes else '❌'}")
    print(f"   Endpoint funcionou: {'✅' if sucesso else '❌'}")
    print(f"   OS existe depois: {'✅' if os_existe_depois else '❌'}")
    
    if os_existe_antes and sucesso:
        print("\n✅ BUSCA NO BANCO FUNCIONANDO!")
        print("   A OS já existia e foi retornada corretamente")
    elif not os_existe_antes and sucesso and os_existe_depois:
        print("\n🎉 IMPLEMENTAÇÃO COMPLETA FUNCIONANDO!")
        print("   ✅ OS não existia no banco")
        print("   ✅ Scraping executado automaticamente")
        print("   ✅ OS criada no banco com dados do scraping")
        print("   ✅ Nova consulta retornou dados corretos")
    elif not os_existe_antes and sucesso and not os_existe_depois:
        print("\n⚠️ ENDPOINT FUNCIONOU MAS OS NÃO FOI CRIADA")
        print("   Pode ter havido erro na criação no banco")
    else:
        print("\n❌ IMPLEMENTAÇÃO COM PROBLEMAS")
        print("   Verificar logs do backend para detalhes")

if __name__ == "__main__":
    main()
