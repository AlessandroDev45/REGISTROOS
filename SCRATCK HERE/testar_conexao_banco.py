#!/usr/bin/env python3
"""
Script para testar qual banco o servidor está usando
"""

import sys
import os
import sqlite3
import requests

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_banco_config():
    """Verifica qual banco está configurado"""
    try:
        from config.database_config import DATABASE_URL, db_path
        
        print("🔍 Verificando configuração do banco...")
        print(f"  📂 DATABASE_URL: {DATABASE_URL}")
        print(f"  📂 db_path: {db_path}")
        
        # Verificar se o arquivo existe
        if os.path.exists(db_path):
            print(f"  ✅ Arquivo do banco EXISTE")
            
            # Verificar usuários no banco configurado
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
            count = cursor.fetchone()[0]
            print(f"  📊 Usuários no banco configurado: {count}")
            
            # Verificar se o usuário específico existe
            cursor.execute("SELECT email FROM tipo_usuarios WHERE email = ?", ('user.mecanica_dia@registroos.com',))
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"  ✅ Usuário user.mecanica_dia@registroos.com ENCONTRADO no banco configurado")
            else:
                print(f"  ❌ Usuário user.mecanica_dia@registroos.com NÃO ENCONTRADO no banco configurado")
            
            conn.close()
        else:
            print(f"  ❌ Arquivo do banco NÃO EXISTE: {db_path}")
        
        return db_path
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return None

def testar_endpoint_usuarios():
    """Testa o endpoint de usuários do servidor"""
    try:
        print(f"\n🔍 Testando endpoint do servidor...")
        
        # Testar endpoint de setores (que funciona)
        response = requests.get("http://localhost:8000/api/admin/setores/")
        if response.status_code == 200:
            setores = response.json()
            print(f"  ✅ Endpoint setores funcionando: {len(setores)} setores")
        else:
            print(f"  ❌ Endpoint setores falhou: {response.status_code}")
        
        # Testar login com dados conhecidos
        login_data = {
            "username": "user.mecanica_dia@registroos.com",
            "password": "123456"  # Senha padrão
        }
        
        response = requests.post("http://localhost:8000/api/token", data=login_data)
        print(f"  📊 Teste de login: {response.status_code}")
        
        if response.status_code == 401:
            print(f"  ❌ Login falhou - usuário não encontrado ou senha incorreta")
        elif response.status_code == 200:
            print(f"  ✅ Login funcionou!")
        else:
            print(f"  ⚠️ Resposta inesperada: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def verificar_modelo_usuario():
    """Verifica se o modelo Usuario está correto"""
    try:
        print(f"\n🔍 Verificando modelo Usuario...")
        
        from app.database_models import Usuario
        
        print(f"  📋 Tabela do modelo Usuario: {Usuario.__tablename__}")
        
        # Testar conexão direta com o modelo
        from config.database_config import SessionLocal
        
        db = SessionLocal()
        
        # Contar usuários usando o modelo
        count = db.query(Usuario).count()
        print(f"  📊 Usuários via modelo: {count}")
        
        # Buscar usuário específico
        usuario = db.query(Usuario).filter(Usuario.email == 'user.mecanica_dia@registroos.com').first()
        
        if usuario:
            print(f"  ✅ Usuário encontrado via modelo: {usuario.email}")
            print(f"    Nome: {usuario.nome_completo}")
            print(f"    Aprovado: {usuario.is_approved}")
        else:
            print(f"  ❌ Usuário NÃO encontrado via modelo")
            
            # Listar alguns usuários
            usuarios = db.query(Usuario).limit(5).all()
            print(f"  📋 Primeiros 5 usuários via modelo:")
            for u in usuarios:
                print(f"    - {u.email}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {e}")
        return False

def main():
    print("🔍 Diagnóstico completo do problema de login...")
    print("=" * 60)
    
    # 1. Verificar configuração do banco
    banco_config = verificar_banco_config()
    
    # 2. Testar endpoints
    testar_endpoint_usuarios()
    
    # 3. Verificar modelo
    verificar_modelo_usuario()
    
    print(f"\n🎯 Diagnóstico concluído!")
    
    if banco_config:
        print(f"✅ Banco configurado: {os.path.basename(banco_config)}")
    else:
        print(f"❌ Problema na configuração do banco")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
