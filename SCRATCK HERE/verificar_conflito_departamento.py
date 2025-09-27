#!/usr/bin/env python3
"""
VERIFICAR CONFLITO DE DEPARTAMENTO
==================================

Verifica se há conflito de nomes de departamentos no banco.
"""

import sqlite3
import os

# Configurações
BACKEND_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
DB_PATH = os.path.join(BACKEND_PATH, "registroos_new.db")

def conectar_banco():
    """Conecta ao banco de dados"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_departamentos(conn):
    """Verifica todos os departamentos"""
    cursor = conn.cursor()
    
    print("📋 DEPARTAMENTOS EXISTENTES:")
    cursor.execute("SELECT id, nome_tipo, descricao, ativo FROM tipo_departamentos ORDER BY id")
    departamentos = cursor.fetchall()
    
    for dept in departamentos:
        status = "✅ ATIVO" if dept['ativo'] else "❌ INATIVO"
        print(f"   ID: {dept['id']}, Nome: '{dept['nome_tipo']}', {status}")
        print(f"      Descrição: {dept['descricao']}")
    
    return departamentos

def verificar_conflito_nome(conn, nome_teste):
    """Verifica se há conflito com um nome específico"""
    cursor = conn.cursor()
    
    print(f"\n🔍 VERIFICANDO CONFLITO COM NOME: '{nome_teste}'")
    cursor.execute("SELECT id, nome_tipo, ativo FROM tipo_departamentos WHERE nome_tipo = ?", (nome_teste,))
    conflitos = cursor.fetchall()
    
    if conflitos:
        print(f"⚠️ CONFLITO ENCONTRADO! {len(conflitos)} departamento(s) com o nome '{nome_teste}':")
        for conflito in conflitos:
            status = "ATIVO" if conflito['ativo'] else "INATIVO"
            print(f"   ID: {conflito['id']}, Status: {status}")
        return True
    else:
        print(f"✅ Nenhum conflito encontrado para o nome '{nome_teste}'")
        return False

def simular_update(conn, dept_id, novo_nome):
    """Simula o update que está falhando"""
    cursor = conn.cursor()
    
    print(f"\n🔄 SIMULANDO UPDATE DO DEPARTAMENTO ID {dept_id} PARA '{novo_nome}'")
    
    # Verificar se o departamento existe
    cursor.execute("SELECT id, nome_tipo, ativo FROM tipo_departamentos WHERE id = ?", (dept_id,))
    dept_atual = cursor.fetchone()
    
    if not dept_atual:
        print(f"❌ Departamento ID {dept_id} não encontrado!")
        return False
    
    print(f"📋 Departamento atual: ID {dept_atual['id']}, Nome: '{dept_atual['nome_tipo']}'")
    
    # Verificar se o novo nome já existe (exceto para o próprio departamento)
    cursor.execute("""
        SELECT id, nome_tipo, ativo 
        FROM tipo_departamentos 
        WHERE nome_tipo = ? AND id != ?
    """, (novo_nome, dept_id))
    
    conflitos = cursor.fetchall()
    
    if conflitos:
        print(f"❌ ERRO: Já existe outro departamento com o nome '{novo_nome}':")
        for conflito in conflitos:
            status = "ATIVO" if conflito['ativo'] else "INATIVO"
            print(f"   ID: {conflito['id']}, Status: {status}")
        return False
    else:
        print(f"✅ Update seria bem-sucedido - nenhum conflito encontrado")
        return True

def main():
    """Função principal"""
    print("🚀 VERIFICANDO CONFLITOS DE DEPARTAMENTOS")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # 1. Listar todos os departamentos
        departamentos = verificar_departamentos(conn)
        
        # 2. Verificar conflito com o nome que está causando erro
        verificar_conflito_nome(conn, "T5AT4E")
        
        # 3. Simular o update que está falhando
        simular_update(conn, 1, "T5AT4E")
        
        # 4. Verificar outros nomes similares
        print(f"\n" + "="*40)
        verificar_conflito_nome(conn, "MOTORES")
        verificar_conflito_nome(conn, "TRANSFORMADORES")
        verificar_conflito_nome(conn, "TESTE")
        
        print(f"\n🎉 VERIFICAÇÃO CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
