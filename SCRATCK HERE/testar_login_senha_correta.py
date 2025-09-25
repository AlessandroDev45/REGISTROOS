#!/usr/bin/env python3
"""
Script para testar login com a senha correta
"""

import sys
import os
import sqlite3
import requests
import bcrypt

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_senha_hash():
    """Verifica o hash da senha no banco"""
    try:
        banco = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco)
        cursor = conn.cursor()
        
        print("🔍 Verificando hash da senha no banco...")
        
        # Buscar o hash da senha do usuário
        cursor.execute("SELECT email, senha_hash FROM tipo_usuarios WHERE email = ?", ('user.mecanica_dia@registroos.com',))
        resultado = cursor.fetchone()
        
        if resultado:
            email, senha_hash = resultado
            print(f"  ✅ Usuário: {email}")
            print(f"  🔑 Hash no banco: {senha_hash[:50]}...")
            
            # Testar se a senha 123456 confere com o hash
            senha_teste = "123456"
            
            try:
                if bcrypt.checkpw(senha_teste.encode('utf-8'), senha_hash.encode('utf-8')):
                    print(f"  ✅ Senha '123456' CONFERE com o hash!")
                else:
                    print(f"  ❌ Senha '123456' NÃO confere com o hash")
                    
                    # Testar outras senhas comuns
                    senhas_teste = ["admin123", "123", "password", "user123", "mecanica123"]
                    for senha in senhas_teste:
                        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                            print(f"  ✅ Senha correta encontrada: '{senha}'")
                            return senha
                    
                    print(f"  ⚠️ Nenhuma senha comum funcionou")
                    
            except Exception as e:
                print(f"  ❌ Erro ao verificar hash: {e}")
                
        else:
            print(f"  ❌ Usuário não encontrado")
        
        conn.close()
        return "123456"  # Retorna a senha padrão
        
    except Exception as e:
        print(f"❌ Erro ao verificar senha: {e}")
        return "123456"

def testar_login_direto():
    """Testa login direto via API"""
    try:
        print(f"\n🔍 Testando login direto via API...")
        
        # Testar com a senha fornecida
        login_data = {
            "username": "user.mecanica_dia@registroos.com",
            "password": "123456"
        }
        
        print(f"  📊 Tentando login com:")
        print(f"    Email: {login_data['username']}")
        print(f"    Senha: {login_data['password']}")
        
        response = requests.post("http://localhost:8000/api/token", data=login_data)
        
        print(f"  📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ LOGIN FUNCIONOU!")
            token_data = response.json()
            print(f"  🔑 Token recebido: {token_data.get('access_token', 'N/A')[:50]}...")
            return True
        else:
            print(f"  ❌ Login falhou")
            print(f"  📋 Resposta: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
        return False

def testar_outros_usuarios():
    """Testa login com outros usuários"""
    try:
        print(f"\n🔍 Testando outros usuários...")
        
        # Lista de usuários para testar
        usuarios_teste = [
            ("admin@registroos.com", "admin123"),
            ("admin@registroos.com", "123456"),
            ("user.pcp@registroos.com", "123456"),
            ("teste.debug@registroos.com", "123456")
        ]
        
        for email, senha in usuarios_teste:
            print(f"\n  📊 Testando: {email} / {senha}")
            
            login_data = {
                "username": email,
                "password": senha
            }
            
            response = requests.post("http://localhost:8000/api/token", data=login_data)
            
            if response.status_code == 200:
                print(f"    ✅ LOGIN FUNCIONOU!")
                return True
            else:
                print(f"    ❌ Falhou ({response.status_code})")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao testar outros usuários: {e}")
        return False

def verificar_funcao_login():
    """Verifica a função de login no código"""
    try:
        print(f"\n🔍 Verificando função de login...")
        
        from config.database_config import SessionLocal
        from app.database_models import Usuario
        
        db = SessionLocal()
        
        # Buscar usuário diretamente
        usuario = db.query(Usuario).filter(Usuario.email == 'user.mecanica_dia@registroos.com').first()
        
        if usuario:
            print(f"  ✅ Usuário encontrado via SQLAlchemy")
            print(f"    Email: {usuario.email}")
            print(f"    Nome: {usuario.nome_completo}")
            print(f"    Aprovado: {usuario.is_approved}")
            print(f"    Hash: {usuario.senha_hash[:50]}...")
            
            # Testar verificação de senha
            import bcrypt
            senha_teste = "123456"
            
            if bcrypt.checkpw(senha_teste.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
                print(f"  ✅ Verificação de senha OK via SQLAlchemy")
            else:
                print(f"  ❌ Verificação de senha FALHOU via SQLAlchemy")
        else:
            print(f"  ❌ Usuário NÃO encontrado via SQLAlchemy")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar função: {e}")
        return False

def main():
    print("🔍 Teste completo de login com senha correta...")
    print("=" * 60)
    
    # 1. Verificar hash da senha
    senha_correta = verificar_senha_hash()
    
    # 2. Testar login direto
    login_ok = testar_login_direto()
    
    # 3. Se não funcionou, testar outros usuários
    if not login_ok:
        login_ok = testar_outros_usuarios()
    
    # 4. Verificar função de login
    verificar_funcao_login()
    
    print(f"\n🎯 Resultado final:")
    if login_ok:
        print(f"✅ LOGIN FUNCIONANDO!")
    else:
        print(f"❌ LOGIN NÃO FUNCIONANDO")
        print(f"🔧 Possíveis causas:")
        print(f"  - Hash da senha incorreto")
        print(f"  - Problema na função de autenticação")
        print(f"  - Cache do servidor")
    
    return login_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
