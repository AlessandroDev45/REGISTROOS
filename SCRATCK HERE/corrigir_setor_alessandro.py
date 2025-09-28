#!/usr/bin/env python3
"""
Script para corrigir o setor do usuário alessandro.souza@data.com.br
para LABORATORIO DE ENSAIOS ELETRICOS
"""

import sqlite3
import os

# Caminho do banco de dados
db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def corrigir_setor_alessandro():
    """Corrigir o setor do usuário alessandro para LABORATORIO DE ENSAIOS ELETRICOS"""
    print("🔧 Corrigindo setor do usuário alessandro.souza@data.com.br...")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Buscar o setor LABORATORIO DE ENSAIOS ELETRICOS
        cursor.execute("""
            SELECT id, nome, departamento, id_departamento
            FROM tipo_setores 
            WHERE nome = 'LABORATORIO DE ENSAIOS ELETRICOS'
            AND ativo = 1
        """)
        
        setor = cursor.fetchone()
        if not setor:
            print("❌ Setor 'LABORATORIO DE ENSAIOS ELETRICOS' não encontrado!")
            
            # Listar setores disponíveis
            cursor.execute("SELECT id, nome, departamento FROM tipo_setores WHERE ativo = 1")
            setores = cursor.fetchall()
            print("📋 Setores disponíveis:")
            for s in setores:
                print(f"   ID: {s[0]} | Nome: {s[1]} | Departamento: {s[2]}")
            return
        
        print(f"✅ Setor encontrado:")
        print(f"   ID: {setor[0]}")
        print(f"   Nome: {setor[1]}")
        print(f"   Departamento: {setor[2]}")
        print(f"   ID Departamento: {setor[3]}")
        
        # 2. Verificar dados atuais do usuário
        cursor.execute("""
            SELECT id, nome_completo, setor, departamento, id_setor, id_departamento
            FROM tipo_usuarios 
            WHERE email = 'alessandro.souza@data.com.br'
        """)
        
        usuario = cursor.fetchone()
        if not usuario:
            print("❌ Usuário alessandro.souza@data.com.br não encontrado!")
            return
        
        print(f"\n👤 Dados atuais do usuário:")
        print(f"   ID: {usuario[0]}")
        print(f"   Nome: {usuario[1]}")
        print(f"   Setor atual: {usuario[2]}")
        print(f"   Departamento atual: {usuario[3]}")
        print(f"   ID Setor atual: {usuario[4]}")
        print(f"   ID Departamento atual: {usuario[5]}")
        
        # 3. Atualizar o usuário
        cursor.execute("""
            UPDATE tipo_usuarios SET
                setor = ?,
                departamento = ?,
                id_setor = ?,
                id_departamento = ?
            WHERE email = 'alessandro.souza@data.com.br'
        """, (setor[1], setor[2], setor[0], setor[3]))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n✅ Usuário atualizado com sucesso!")
            print(f"   Novo setor: {setor[1]} (ID: {setor[0]})")
            print(f"   Novo departamento: {setor[2]} (ID: {setor[3]})")
            
            # 4. Verificar se a atualização foi aplicada
            cursor.execute("""
                SELECT setor, departamento, id_setor, id_departamento
                FROM tipo_usuarios 
                WHERE email = 'alessandro.souza@data.com.br'
            """)
            
            dados_atualizados = cursor.fetchone()
            print(f"\n🔍 Verificação pós-atualização:")
            print(f"   Setor: {dados_atualizados[0]}")
            print(f"   Departamento: {dados_atualizados[1]}")
            print(f"   ID Setor: {dados_atualizados[2]}")
            print(f"   ID Departamento: {dados_atualizados[3]}")
            
        else:
            print("❌ Nenhum usuário foi atualizado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao corrigir usuário: {e}")

if __name__ == "__main__":
    corrigir_setor_alessandro()
