#!/usr/bin/env python3
"""
Script para verificar exatamente qual banco o servidor está usando
"""

import sys
import os
import sqlite3
import requests

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_caminhos():
    """Verifica todos os caminhos possíveis"""
    try:
        print("🔍 Verificando caminhos de banco...")
        
        from config.database_config import DATABASE_URL, db_path
        
        print(f"  📂 DATABASE_URL configurado: {DATABASE_URL}")
        print(f"  📂 db_path configurado: {db_path}")
        print(f"  📂 Arquivo existe: {os.path.exists(db_path)}")
        
        # Verificar caminhos relativos possíveis
        caminhos_possiveis = [
            db_path,
            os.path.join(os.getcwd(), 'registroos.db'),
            os.path.join(os.getcwd(), 'RegistroOS', 'registrooficial', 'backend', 'registroos.db'),
            os.path.join(backend_path, 'registroos.db'),
            'registroos.db'
        ]
        
        print(f"\n📋 Verificando caminhos possíveis:")
        for i, caminho in enumerate(caminhos_possiveis, 1):
            existe = os.path.exists(caminho)
            if existe:
                size = os.path.getsize(caminho)
                print(f"  {i}. ✅ {caminho} ({size} bytes)")
                
                # Verificar usuários neste banco
                try:
                    conn = sqlite3.connect(caminho)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
                    count = cursor.fetchone()[0]
                    print(f"      👥 {count} usuários")
                    conn.close()
                except:
                    print(f"      ❌ Erro ao ler banco")
            else:
                print(f"  {i}. ❌ {caminho}")
        
        return db_path
        
    except Exception as e:
        print(f"❌ Erro ao verificar caminhos: {e}")
        return None

def testar_endpoint_debug():
    """Testa o endpoint de debug do servidor"""
    try:
        print(f"\n🔍 Testando endpoint de debug do servidor...")
        
        response = requests.get("http://localhost:8000/api/debug-users")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  📊 Resposta do servidor:")
            print(f"    Total usuários: {data.get('total_usuarios', 'N/A')}")
            print(f"    Database path: {data.get('database_path', 'N/A')}")
            print(f"    Status: {data.get('status', 'N/A')}")
            
            if data.get('usuarios'):
                print(f"    Usuários encontrados:")
                for user in data['usuarios'][:3]:
                    print(f"      - {user.get('email', 'N/A')}")
            
            return data
        else:
            print(f"  ❌ Erro no endpoint: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return None

def verificar_working_directory():
    """Verifica o diretório de trabalho atual"""
    try:
        print(f"\n🔍 Verificando diretório de trabalho...")
        
        cwd = os.getcwd()
        print(f"  📂 Current working directory: {cwd}")
        
        # Verificar se existe registroos.db no diretório atual
        banco_local = os.path.join(cwd, 'registroos.db')
        if os.path.exists(banco_local):
            print(f"  ✅ Encontrado registroos.db no diretório atual")
            
            # Verificar usuários
            conn = sqlite3.connect(banco_local)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
            count = cursor.fetchone()[0]
            print(f"      👥 {count} usuários")
            conn.close()
        else:
            print(f"  ❌ Não existe registroos.db no diretório atual")
        
        return cwd
        
    except Exception as e:
        print(f"❌ Erro ao verificar working directory: {e}")
        return None

def main():
    print("🔍 Debug completo dos caminhos de banco...")
    print("=" * 60)
    
    # 1. Verificar caminhos
    verificar_caminhos()
    
    # 2. Verificar working directory
    verificar_working_directory()
    
    # 3. Testar endpoint do servidor
    testar_endpoint_debug()
    
    print(f"\n🎯 Debug concluído!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
