#!/usr/bin/env python3
"""
Script para verificar usuário específico e testar login
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_usuarios():
    """Verifica todos os usuários na tabela tipo_usuarios"""
    try:
        banco = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco)
        cursor = conn.cursor()
        
        print("🔍 Verificando usuários na tabela tipo_usuarios...")
        
        # Buscar todos os usuários
        cursor.execute("SELECT id, email, nome_usuario, cargo, setor, departamento, is_approved FROM tipo_usuarios")
        usuarios = cursor.fetchall()
        
        print(f"📊 Total de usuários: {len(usuarios)}")
        print(f"📋 Lista de usuários:")
        
        for usuario in usuarios:
            id_user, email, nome_usuario, cargo, setor, departamento, is_approved = usuario
            status = "✅ APROVADO" if is_approved else "❌ NÃO APROVADO"
            print(f"  {id_user:2d}. {email}")
            print(f"      Nome: {nome_usuario}")
            print(f"      Cargo: {cargo}")
            print(f"      Setor: {setor}")
            print(f"      Departamento: {departamento}")
            print(f"      Status: {status}")
            print()
        
        # Verificar se o usuário específico existe
        email_procurado = 'user.mecanica_dia@registroos.com'
        cursor.execute("SELECT * FROM tipo_usuarios WHERE email = ?", (email_procurado,))
        usuario_especifico = cursor.fetchone()
        
        if usuario_especifico:
            print(f"✅ Usuário {email_procurado} ENCONTRADO!")
            print(f"   Dados completos: {usuario_especifico}")
        else:
            print(f"❌ Usuário {email_procurado} NÃO ENCONTRADO")
            
            # Buscar usuários similares
            cursor.execute("SELECT email FROM tipo_usuarios WHERE email LIKE '%mecanica%'")
            similares = cursor.fetchall()
            if similares:
                print(f"🔍 Usuários similares encontrados:")
                for similar in similares:
                    print(f"   - {similar[0]}")
            else:
                print(f"🔍 Nenhum usuário com 'mecanica' no email encontrado")
        
        conn.close()
        return len(usuarios)
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")
        return 0

def verificar_estrutura_login():
    """Verifica se a estrutura de login está correta"""
    try:
        banco = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificando estrutura para login...")
        
        # Verificar campos necessários para login
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        colunas = cursor.fetchall()
        
        campos_login = ['email', 'senha_hash', 'is_approved']
        campos_existentes = [col[1] for col in colunas]
        
        print(f"📋 Campos necessários para login:")
        for campo in campos_login:
            if campo in campos_existentes:
                print(f"  ✅ {campo} - EXISTE")
            else:
                print(f"  ❌ {campo} - FALTANDO")
        
        # Verificar se há usuários aprovados
        cursor.execute("SELECT COUNT(*) FROM tipo_usuarios WHERE is_approved = 1")
        aprovados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tipo_usuarios WHERE is_approved = 0")
        nao_aprovados = cursor.fetchone()[0]
        
        print(f"\n📊 Status dos usuários:")
        print(f"  ✅ Aprovados: {aprovados}")
        print(f"  ❌ Não aprovados: {nao_aprovados}")
        
        # Mostrar alguns usuários aprovados
        if aprovados > 0:
            cursor.execute("SELECT email, nome_usuario FROM tipo_usuarios WHERE is_approved = 1 LIMIT 5")
            usuarios_aprovados = cursor.fetchall()
            
            print(f"\n📋 Usuários aprovados (primeiros 5):")
            for email, nome in usuarios_aprovados:
                print(f"  - {email} ({nome})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def main():
    print("🔍 Verificação de usuários e estrutura de login...")
    print("=" * 60)
    
    # Verificar usuários
    total_usuarios = verificar_usuarios()
    
    # Verificar estrutura de login
    verificar_estrutura_login()
    
    print(f"\n🎯 Verificação concluída!")
    print(f"📊 Total de usuários encontrados: {total_usuarios}")
    
    if total_usuarios > 0:
        print(f"✅ Existem usuários na base de dados")
        print(f"🔑 Verifique se o email e senha estão corretos")
        print(f"🔑 Verifique se o usuário está aprovado (is_approved = 1)")
    else:
        print(f"❌ Nenhum usuário encontrado na base de dados")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
