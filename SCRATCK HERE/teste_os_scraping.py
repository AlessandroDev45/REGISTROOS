#!/usr/bin/env python3
"""
Teste completo da funcionalidade de busca de OS com scraping automático
"""

import requests
import json
import sqlite3

def verificar_banco_dados():
    """Verifica se a base de dados está no local correto"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['ordens_servico', 'clientes', 'equipamentos', 'tipo_usuarios']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"❌ Tabelas ausentes: {missing_tables}")
            return False
            
        # Verificar se há usuários
        cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
        user_count = cursor.fetchone()[0]
        
        print(f"✅ Base de dados OK - {len(tables)} tabelas, {user_count} usuários")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na base de dados: {e}")
        return False

def testar_backend():
    """Testa se o backend está rodando"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend não está rodando: {e}")
        return False

def fazer_login():
    """Tenta fazer login com diferentes credenciais"""
    session = requests.Session()
    
    # Lista de credenciais para testar
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "admin", "password": "admin"},
        {"username": "admin@admin.com", "password": "admin123"},
    ]
    
    for cred in credenciais:
        try:
            print(f"🔐 Tentando login com: {cred['username']}")
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Login realizado com sucesso: {cred['username']}")
                return session
            else:
                print(f"❌ Login falhou: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
    
    print("❌ Nenhuma credencial funcionou")
    return None

def main():
    """Função principal do teste"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA DE OS COM SCRAPING")
    print("=" * 60)
    
    # 1. Verificar base de dados
    print("\n1️⃣ VERIFICANDO BASE DE DADOS...")
    if not verificar_banco_dados():
        print("❌ Teste interrompido - problema na base de dados")
        return
    
    # 2. Verificar backend
    print("\n2️⃣ VERIFICANDO BACKEND...")
    if not testar_backend():
        print("❌ Teste interrompido - backend não está rodando")
        return
    
    # 3. Fazer login
    print("\n3️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - não foi possível fazer login")
        return
    
    print("\n✅ SISTEMA BÁSICO FUNCIONANDO!")
    print("📋 PRÓXIMOS PASSOS:")
    print("   1. Verificar arquivo .env em: RegistroOS/registrooficial/backend/scripts/.env")
    print("   2. Configurar variáveis: SITE_URL, USERNAME, PASSWORD")
    print("   3. Testar busca de OS no desenvolvimento")

if __name__ == "__main__":
    main()
