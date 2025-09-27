#!/usr/bin/env python3
"""
VERIFICAR DISCREPÂNCIA NO BANCO
==============================

Verificar por que há diferença entre teste direto e endpoint.
"""

import sqlite3
import requests

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def verificar_banco_direto():
    """Verificar banco diretamente"""
    print("🔍 Verificando banco diretamente...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar todas as programações
        cursor.execute("SELECT id, responsavel_id, status FROM programacoes ORDER BY id DESC LIMIT 10")
        all_progs = cursor.fetchall()
        
        print(f"📋 Últimas 10 programações:")
        for prog in all_progs:
            print(f"   ID {prog[0]}: responsavel_id={prog[1]}, status={prog[2]}")
        
        # Verificar especificamente user_id = 1
        cursor.execute("SELECT COUNT(*) FROM programacoes WHERE responsavel_id = 1")
        count_1 = cursor.fetchone()[0]
        
        cursor.execute("SELECT id, status FROM programacoes WHERE responsavel_id = 1")
        progs_1 = cursor.fetchall()
        
        print(f"\n📊 Programações para responsavel_id=1: {count_1}")
        for prog in progs_1:
            print(f"   ID {prog[0]}: status={prog[1]}")
        
        # Verificar se há diferença de tipos
        cursor.execute("SELECT DISTINCT typeof(responsavel_id) FROM programacoes")
        types = cursor.fetchall()
        print(f"\n🔍 Tipos de responsavel_id no banco: {types}")
        
        # Verificar valores NULL
        cursor.execute("SELECT COUNT(*) FROM programacoes WHERE responsavel_id IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"📊 Programações com responsavel_id NULL: {null_count}")
        
        conn.close()
        return count_1
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return 0

def verificar_endpoint():
    """Verificar via endpoint"""
    print("\n🔍 Verificando via endpoint...")
    
    session = requests.Session()
    
    # Login
    response = session.post(LOGIN_URL, json=ADMIN_USER)
    if response.status_code != 200:
        print("❌ Erro no login")
        return 0
    
    # Testar endpoint
    response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes-v2")
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Resposta do endpoint: {data}")
        return data.get('count', 0)
    else:
        print(f"❌ Erro no endpoint: {response.status_code}")
        return 0

def verificar_usuario_logado():
    """Verificar qual usuário está logado"""
    print("\n🔍 Verificando usuário logado...")
    
    session = requests.Session()
    
    # Login
    response = session.post(LOGIN_URL, json=ADMIN_USER)
    if response.status_code != 200:
        print("❌ Erro no login")
        return
    
    # Verificar usuário
    response = session.get(f"{BASE_URL}/api/desenvolvimento/test-programacoes")
    if response.status_code == 200:
        data = response.json()
        print(f"👤 Usuário logado: {data}")
    else:
        print(f"❌ Erro: {response.status_code}")

def main():
    """Função principal"""
    print("🔧 VERIFICAR DISCREPÂNCIA NO BANCO")
    print("=" * 40)
    
    # 1. Verificar banco direto
    count_banco = verificar_banco_direto()
    
    # 2. Verificar usuário logado
    verificar_usuario_logado()
    
    # 3. Verificar endpoint
    count_endpoint = verificar_endpoint()
    
    # 4. Comparar
    print(f"\n📊 COMPARAÇÃO:")
    print(f"   Banco direto: {count_banco} programações")
    print(f"   Endpoint: {count_endpoint} programações")
    
    if count_banco != count_endpoint:
        print("\n⚠️ DISCREPÂNCIA DETECTADA!")
        print("   Possíveis causas:")
        print("   1. Usuário logado diferente do esperado")
        print("   2. Banco de dados diferente")
        print("   3. Problema de tipos de dados")
        print("   4. Transação não commitada")
    else:
        print("\n✅ Dados consistentes")

if __name__ == "__main__":
    main()
