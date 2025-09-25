#!/usr/bin/env python3
"""
Script para copiar usuários do banco correto para o banco que o servidor está usando
"""

import sys
import os
import sqlite3
import shutil

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def copiar_usuarios():
    """Copia usuários do banco correto para o banco que o servidor está usando"""
    try:
        print("🔄 Copiando usuários para o banco que o servidor está usando...")
        
        # Caminhos dos bancos
        banco_correto = os.path.join(backend_path, 'registroos.db')
        banco_servidor = os.path.join(backend_path, 'registroos_new.db')
        
        print(f"  📂 Banco correto: {banco_correto}")
        print(f"  📂 Banco servidor: {banco_servidor}")
        
        # Verificar se os bancos existem
        if not os.path.exists(banco_correto):
            print(f"  ❌ Banco correto não existe")
            return False
        
        if not os.path.exists(banco_servidor):
            print(f"  ⚠️ Banco do servidor não existe - copiando banco completo...")
            shutil.copy2(banco_correto, banco_servidor)
            print(f"  ✅ Banco copiado completamente!")
            return True
        
        # Conectar aos bancos
        conn_correto = sqlite3.connect(banco_correto)
        conn_servidor = sqlite3.connect(banco_servidor)
        
        cursor_correto = conn_correto.cursor()
        cursor_servidor = conn_servidor.cursor()
        
        # Verificar usuários no banco correto
        cursor_correto.execute("SELECT COUNT(*) FROM tipo_usuarios")
        usuarios_correto = cursor_correto.fetchone()[0]
        print(f"  📊 Usuários no banco correto: {usuarios_correto}")
        
        # Verificar usuários no banco do servidor
        try:
            cursor_servidor.execute("SELECT COUNT(*) FROM tipo_usuarios")
            usuarios_servidor = cursor_servidor.fetchone()[0]
            print(f"  📊 Usuários no banco servidor: {usuarios_servidor}")
        except:
            print(f"  ⚠️ Tabela tipo_usuarios não existe no banco servidor")
            usuarios_servidor = 0
        
        if usuarios_correto == 0:
            print(f"  ⚠️ Nenhum usuário no banco correto")
            return False
        
        # Limpar tabela no banco servidor
        try:
            cursor_servidor.execute("DELETE FROM tipo_usuarios")
            print(f"  🗑️ Tabela tipo_usuarios limpa no banco servidor")
        except:
            print(f"  ⚠️ Erro ao limpar tabela - pode não existir")
        
        # Obter estrutura da tabela
        cursor_correto.execute("PRAGMA table_info(tipo_usuarios)")
        colunas_info = cursor_correto.fetchall()
        colunas = [col[1] for col in colunas_info]
        
        print(f"  📋 Colunas a copiar: {len(colunas)}")
        
        # Buscar todos os usuários
        colunas_str = ', '.join(colunas)
        cursor_correto.execute(f"SELECT {colunas_str} FROM tipo_usuarios")
        usuarios = cursor_correto.fetchall()
        
        print(f"  📊 Usuários encontrados: {len(usuarios)}")
        
        # Inserir usuários no banco servidor
        placeholders = ', '.join(['?' for _ in colunas])
        insert_sql = f"INSERT OR REPLACE INTO tipo_usuarios ({colunas_str}) VALUES ({placeholders})"
        
        cursor_servidor.executemany(insert_sql, usuarios)
        conn_servidor.commit()
        
        print(f"  ✅ {len(usuarios)} usuários copiados!")
        
        # Verificar resultado
        cursor_servidor.execute("SELECT COUNT(*) FROM tipo_usuarios")
        usuarios_final = cursor_servidor.fetchone()[0]
        print(f"  📊 Usuários no banco servidor após cópia: {usuarios_final}")
        
        # Mostrar alguns exemplos
        cursor_servidor.execute("SELECT email, nome_completo FROM tipo_usuarios LIMIT 3")
        exemplos = cursor_servidor.fetchall()
        
        print(f"  📋 Exemplos copiados:")
        for email, nome in exemplos:
            print(f"    - {email} ({nome})")
        
        conn_correto.close()
        conn_servidor.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao copiar usuários: {e}")
        return False

def verificar_resultado():
    """Verifica se a cópia funcionou"""
    try:
        print(f"\n🔍 Verificando resultado...")
        
        banco_servidor = os.path.join(backend_path, 'registroos_new.db')
        
        if not os.path.exists(banco_servidor):
            print(f"  ❌ Banco servidor não existe")
            return False
        
        conn = sqlite3.connect(banco_servidor)
        cursor = conn.cursor()
        
        # Contar usuários
        cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
        count = cursor.fetchone()[0]
        print(f"  📊 Total de usuários: {count}")
        
        if count > 0:
            # Buscar usuário específico
            cursor.execute("SELECT email FROM tipo_usuarios WHERE email = ?", ('admin@registroos.com',))
            admin = cursor.fetchone()
            
            if admin:
                print(f"  ✅ Usuário admin encontrado: {admin[0]}")
            else:
                print(f"  ⚠️ Usuário admin não encontrado")
            
            # Buscar usuário de teste
            cursor.execute("SELECT email FROM tipo_usuarios WHERE email = ?", ('user.mecanica_dia@registroos.com',))
            user = cursor.fetchone()
            
            if user:
                print(f"  ✅ Usuário teste encontrado: {user[0]}")
            else:
                print(f"  ⚠️ Usuário teste não encontrado")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar resultado: {e}")
        return False

def main():
    print("🔄 Copiando usuários para o banco que o servidor está usando...")
    print("=" * 60)
    
    # 1. Copiar usuários
    sucesso = copiar_usuarios()
    
    # 2. Verificar resultado
    if sucesso:
        verificar_resultado()
    
    print(f"\n🎯 Processo concluído!")
    
    if sucesso:
        print(f"✅ Usuários copiados com sucesso!")
        print(f"🔄 Reinicie o servidor para aplicar as mudanças")
    else:
        print(f"❌ Falha ao copiar usuários")
    
    return sucesso

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
