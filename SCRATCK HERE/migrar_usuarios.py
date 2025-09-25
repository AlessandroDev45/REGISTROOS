#!/usr/bin/env python3
"""
Script para migrar dados da tabela usuarios
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def migrar_usuarios():
    """Migra dados da tabela usuarios"""
    try:
        banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print("📋 Migrando tabela usuarios...")
        
        # Verificar se a tabela existe no banco origem
        cursor_origem.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor_origem.fetchone():
            print("  ⚠️ Tabela usuarios não existe no banco origem")
            return 0
        
        # Buscar dados da origem
        cursor_origem.execute("SELECT * FROM usuarios")
        dados_origem = cursor_origem.fetchall()
        
        # Obter nomes das colunas da origem
        cursor_origem.execute("PRAGMA table_info(usuarios)")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        # Obter nomes das colunas do destino
        cursor_destino.execute("PRAGMA table_info(usuarios)")
        colunas_destino = [col[1] for col in cursor_destino.fetchall()]
        
        print(f"  📊 Registros na origem: {len(dados_origem)}")
        print(f"  📋 Colunas origem: {colunas_origem}")
        print(f"  📋 Colunas destino: {colunas_destino}")
        
        # Encontrar colunas em comum
        colunas_comuns = [col for col in colunas_origem if col in colunas_destino]
        print(f"  📋 Colunas comuns: {colunas_comuns}")
        
        if not colunas_comuns:
            print("  ⚠️ Nenhuma coluna em comum")
            return 0
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM usuarios")
        
        # Processar cada registro
        registros_inseridos = 0
        for linha in dados_origem:
            try:
                # Criar dicionário com os dados
                dados_dict = dict(zip(colunas_origem, linha))
                
                # Preparar dados para inserção (apenas colunas que existem no destino)
                dados_para_inserir = []
                colunas_para_inserir = []
                
                for col in colunas_comuns:
                    if col in dados_dict:
                        colunas_para_inserir.append(col)
                        valor = dados_dict[col]
                        
                        # Tratar campos específicos se necessário
                        if col in ['setor', 'departamento'] and valor is None:
                            valor = 'GERAL'
                        
                        dados_para_inserir.append(valor)
                
                # Inserir no destino
                placeholders = ', '.join(['?' for _ in colunas_para_inserir])
                colunas_str = ', '.join(colunas_para_inserir)
                sql = f"INSERT INTO usuarios ({colunas_str}) VALUES ({placeholders})"
                
                cursor_destino.execute(sql, dados_para_inserir)
                registros_inseridos += 1
                
                email = dados_dict.get('email', dados_dict.get('nome_usuario', f'Usuario_{registros_inseridos}'))
                print(f"  ✅ Registro {registros_inseridos}: {email}")
                
            except Exception as e:
                print(f"  ❌ Erro no registro {linha}: {e}")
        
        conn_destino.commit()
        conn_origem.close()
        conn_destino.close()
        
        print(f"  🎉 {registros_inseridos} registros inseridos em usuarios")
        return registros_inseridos
        
    except Exception as e:
        print(f"❌ Erro ao migrar usuarios: {e}")
        return 0

def verificar_usuarios():
    """Verifica os usuários migrados"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_destino)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificando usuários migrados...")
        
        # Contar usuários
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"  📊 Total de usuários: {count}")
        
        # Mostrar alguns exemplos
        cursor.execute("SELECT email, nome_usuario, cargo FROM usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        
        print(f"  📋 Exemplos de usuários:")
        for i, (email, nome_usuario, cargo) in enumerate(usuarios, 1):
            print(f"    {i}. {email} ({nome_usuario}) - {cargo}")
        
        # Verificar se o usuário específico existe
        cursor.execute("SELECT * FROM usuarios WHERE email = 'user.mecanica_dia@registroos.com'")
        usuario_especifico = cursor.fetchone()
        
        if usuario_especifico:
            print(f"  ✅ Usuário user.mecanica_dia@registroos.com encontrado!")
        else:
            print(f"  ⚠️ Usuário user.mecanica_dia@registroos.com NÃO encontrado")
            
            # Listar todos os emails para debug
            cursor.execute("SELECT email FROM usuarios")
            emails = [row[0] for row in cursor.fetchall()]
            print(f"  📧 Emails disponíveis: {emails[:10]}...")  # Primeiros 10
        
        conn.close()
        return count
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return 0

def main():
    print("🚀 Migrando tabela usuarios...")
    print("=" * 50)
    
    # Migrar usuarios
    usuarios_migrados = migrar_usuarios()
    
    # Verificar resultado
    total_verificado = verificar_usuarios()
    
    print(f"\n🎉 MIGRAÇÃO DE USUÁRIOS CONCLUÍDA!")
    print(f"✅ Usuários migrados: {usuarios_migrados}")
    print(f"✅ Total verificado: {total_verificado}")
    
    if usuarios_migrados > 0:
        print(f"🎯 SUCESSO! Usuários migrados com sucesso.")
        print(f"🔑 Agora você pode fazer login no sistema.")
    else:
        print(f"⚠️ Nenhum usuário foi migrado.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
