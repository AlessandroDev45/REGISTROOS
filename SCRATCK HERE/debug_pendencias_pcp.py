#!/usr/bin/env python3
"""
Debug das pendências no PCP
"""

import requests
import json
import sqlite3
import os

BASE_URL = "http://localhost:8000"

def verificar_banco():
    print("🔍 VERIFICANDO PENDÊNCIAS NO BANCO")
    print("=" * 60)
    
    # Conectar ao banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar se tabela pendencias existe
        print("1. 📋 Verificando tabela pendencias:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pendencias'")
        tabela_existe = cursor.fetchone()
        
        if tabela_existe:
            print("   ✅ Tabela 'pendencias' existe")
            
            # Estrutura da tabela
            cursor.execute("PRAGMA table_info(pendencias)")
            colunas = cursor.fetchall()
            print(f"   📊 Colunas: {[col[1] for col in colunas]}")
            
            # Contar pendências
            cursor.execute("SELECT COUNT(*) FROM pendencias")
            total = cursor.fetchone()[0]
            print(f"   📊 Total de pendências: {total}")
            
            if total > 0:
                # Mostrar algumas pendências
                cursor.execute("SELECT * FROM pendencias LIMIT 5")
                pendencias = cursor.fetchall()
                
                print(f"   📋 Primeiras {len(pendencias)} pendências:")
                for i, pend in enumerate(pendencias, 1):
                    print(f"      {i}. ID: {pend[0]} | OS: {pend[1] if len(pend) > 1 else 'N/A'} | Status: {pend[2] if len(pend) > 2 else 'N/A'}")
            else:
                print("   ⚠️ Nenhuma pendência encontrada no banco")
        else:
            print("   ❌ Tabela 'pendencias' NÃO existe")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

def testar_api():
    print("\n🔍 TESTANDO API DO PCP")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Login como PCP
    print("1. 🔐 Login como PCP...")
    login_data = {
        "username": "pcp@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor: {user_data.get('setor', 'N/A')}")
            print(f"   🏭 Departamento: {user_data.get('departamento', 'N/A')}")
            print(f"   🔑 Nível: {user_data.get('privilege_level', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            # Tentar com admin
            print("   🔄 Tentando com admin...")
            login_data = {
                "username": "admin@registroos.com", 
                "password": "123456"
            }
            login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
            if login_response.status_code == 200:
                user_data = login_response.json().get('user', {})
                print(f"   ✅ Login Admin: {user_data.get('nome_completo', 'N/A')}")
            else:
                print(f"   ❌ Erro no login admin: {login_response.status_code}")
                return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint de pendências PCP
    print("\n2. 🏭 Testando endpoint PCP pendências:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} pendências retornadas")
            
            if data:
                for i, pend in enumerate(data[:3], 1):
                    print(f"      {i}. ID: {pend.get('id')} | OS: {pend.get('numero_os')} | Status: {pend.get('status')}")
            else:
                print("   📋 Lista vazia - nenhuma pendência encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar endpoint de desenvolvimento para comparar
    print("\n3. 🔧 Testando endpoint Desenvolvimento pendências:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} pendências retornadas")
            
            if data:
                for i, pend in enumerate(data[:3], 1):
                    print(f"      {i}. ID: {pend.get('id')} | OS: {pend.get('numero_os')} | Status: {pend.get('status')}")
            else:
                print("   📋 Lista vazia - nenhuma pendência encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def main():
    print("🚨 DEBUG: PENDÊNCIAS PCP")
    print("=" * 80)
    
    verificar_banco()
    testar_api()
    
    print("\n" + "=" * 80)
    print("🎯 DEBUG CONCLUÍDO!")
    print("\n📋 VERIFICAÇÕES:")
    print("1. ✅ Tabela pendencias existe?")
    print("2. ✅ Há pendências no banco?")
    print("3. ✅ API PCP retorna pendências?")
    print("4. ✅ API Desenvolvimento retorna pendências?")

if __name__ == "__main__":
    main()
