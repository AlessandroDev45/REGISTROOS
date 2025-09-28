#!/usr/bin/env python3
"""
Script para verificar por que o usuário alessandro.souza@data.com.br não tem setor
"""

import sqlite3
import os
from datetime import datetime

# Caminho do banco de dados
db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def verificar_usuario_alessandro():
    """Verificar dados do usuário alessandro.souza@data.com.br"""
    print("🔍 Verificando usuário alessandro.souza@data.com.br...")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Buscar o usuário alessandro
        print("\n📋 1. DADOS DO USUÁRIO:")
        cursor.execute("""
            SELECT id, email, nome_completo, primeiro_nome, privilege_level, 
                   id_setor, setor, id_departamento, departamento, trabalha_producao,
                   status, data_criacao
            FROM tipo_usuarios 
            WHERE email = 'alessandro.souza@data.com.br'
        """)
        
        usuario = cursor.fetchone()
        if usuario:
            print(f"   ✅ Usuário encontrado:")
            print(f"      ID: {usuario[0]}")
            print(f"      Email: {usuario[1]}")
            print(f"      Nome: {usuario[2]}")
            print(f"      Primeiro Nome: {usuario[3]}")
            print(f"      Nível: {usuario[4]}")
            print(f"      ID Setor: {usuario[5]}")
            print(f"      Setor (string): {usuario[6]}")
            print(f"      ID Departamento: {usuario[7]}")
            print(f"      Departamento (string): {usuario[8]}")
            print(f"      Trabalha Produção: {usuario[9]}")
            print(f"      Status: {usuario[10]}")
            print(f"      Data Criação: {usuario[11]}")
            
            id_setor = usuario[5]
            id_departamento = usuario[7]
            
        else:
            print("   ❌ Usuário não encontrado!")
            return
        
        # 2. Verificar setores disponíveis
        print("\n🏭 2. SETORES DISPONÍVEIS:")
        cursor.execute("""
            SELECT id, nome, departamento, id_departamento, ativo, descricao
            FROM tipo_setores 
            ORDER BY id
        """)
        
        setores = cursor.fetchall()
        print(f"   📊 Total de setores: {len(setores)}")
        
        for setor in setores:
            status_icon = "✅" if setor[4] else "❌"
            print(f"      {status_icon} ID: {setor[0]} | Nome: {setor[1]} | Dept: {setor[2]} | ID_Dept: {setor[3]} | Ativo: {setor[4]}")
        
        # 3. Verificar departamentos disponíveis
        print("\n🏢 3. DEPARTAMENTOS DISPONÍVEIS:")
        cursor.execute("""
            SELECT id, nome_tipo, descricao, ativo
            FROM tipo_departamentos 
            ORDER BY id
        """)
        
        departamentos = cursor.fetchall()
        print(f"   📊 Total de departamentos: {len(departamentos)}")
        
        for dept in departamentos:
            status_icon = "✅" if dept[3] else "❌"
            print(f"      {status_icon} ID: {dept[0]} | Nome: {dept[1]} | Descrição: {dept[2]} | Ativo: {dept[3]}")
        
        # 4. Verificar se o setor/departamento do usuário existe
        if id_setor:
            print(f"\n🔍 4. VERIFICANDO SETOR DO USUÁRIO (ID: {id_setor}):")
            cursor.execute("""
                SELECT id, nome, departamento, ativo
                FROM tipo_setores 
                WHERE id = ?
            """, (id_setor,))
            
            setor_usuario = cursor.fetchone()
            if setor_usuario:
                print(f"   ✅ Setor encontrado: {setor_usuario[1]} (Ativo: {setor_usuario[3]})")
            else:
                print(f"   ❌ Setor ID {id_setor} não encontrado na tabela tipo_setores!")
        else:
            print("\n⚠️ 4. USUÁRIO NÃO TEM ID_SETOR DEFINIDO")
        
        if id_departamento:
            print(f"\n🔍 5. VERIFICANDO DEPARTAMENTO DO USUÁRIO (ID: {id_departamento}):")
            cursor.execute("""
                SELECT id, nome_tipo, ativo
                FROM tipo_departamentos 
                WHERE id = ?
            """, (id_departamento,))
            
            dept_usuario = cursor.fetchone()
            if dept_usuario:
                print(f"   ✅ Departamento encontrado: {dept_usuario[1]} (Ativo: {dept_usuario[2]})")
            else:
                print(f"   ❌ Departamento ID {id_departamento} não encontrado na tabela tipo_departamentos!")
        else:
            print("\n⚠️ 5. USUÁRIO NÃO TEM ID_DEPARTAMENTO DEFINIDO")
        
        # 6. Sugestões de correção
        print("\n💡 6. SUGESTÕES DE CORREÇÃO:")
        
        if not id_setor and not id_departamento:
            print("   🔧 PROBLEMA: Usuário não tem setor nem departamento definidos")
            print("   📝 SOLUÇÃO: Atualizar o usuário com setor e departamento válidos")
            
            # Sugerir setores ativos
            setores_ativos = [s for s in setores if s[4]]  # s[4] é o campo 'ativo'
            if setores_ativos:
                print(f"   🎯 Setores ativos disponíveis para atribuir:")
                for setor in setores_ativos[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"      - ID: {setor[0]} | Nome: {setor[1]} | Departamento: {setor[2]}")
                
                # Gerar comando SQL para atualizar
                primeiro_setor = setores_ativos[0]
                print(f"\n   🔧 COMANDO SQL PARA CORRIGIR:")
                print(f"   UPDATE tipo_usuarios SET")
                print(f"      id_setor = {primeiro_setor[0]},")
                print(f"      setor = '{primeiro_setor[1]}',")
                print(f"      id_departamento = {primeiro_setor[3]},")
                print(f"      departamento = '{primeiro_setor[2]}'")
                print(f"   WHERE email = 'alessandro.souza@data.com.br';")
        
        elif id_setor and not setor_usuario:
            print(f"   🔧 PROBLEMA: Usuário tem id_setor={id_setor} mas o setor não existe")
            print("   📝 SOLUÇÃO: Atualizar com setor válido ou criar o setor faltante")
        
        elif id_departamento and not dept_usuario:
            print(f"   🔧 PROBLEMA: Usuário tem id_departamento={id_departamento} mas o departamento não existe")
            print("   📝 SOLUÇÃO: Atualizar com departamento válido ou criar o departamento faltante")
        
        else:
            print("   ✅ Usuário parece ter setor e departamento válidos")
            print("   🔍 Verifique se o problema está no frontend ou na autenticação")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")

def corrigir_usuario_alessandro():
    """Corrigir o usuário alessandro atribuindo um setor válido"""
    print("\n🔧 CORRIGINDO USUÁRIO ALESSANDRO...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar primeiro setor ativo
        cursor.execute("""
            SELECT id, nome, departamento, id_departamento
            FROM tipo_setores 
            WHERE ativo = 1
            ORDER BY id
            LIMIT 1
        """)
        
        setor = cursor.fetchone()
        if not setor:
            print("❌ Nenhum setor ativo encontrado!")
            return
        
        # Atualizar usuário
        cursor.execute("""
            UPDATE tipo_usuarios SET
                id_setor = ?,
                setor = ?,
                id_departamento = ?,
                departamento = ?
            WHERE email = 'alessandro.souza@data.com.br'
        """, (setor[0], setor[1], setor[3], setor[2]))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Usuário atualizado com sucesso!")
            print(f"   Setor: {setor[1]} (ID: {setor[0]})")
            print(f"   Departamento: {setor[2]} (ID: {setor[3]})")
        else:
            print("❌ Nenhum usuário foi atualizado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao corrigir usuário: {e}")

if __name__ == "__main__":
    verificar_usuario_alessandro()
    
    # Perguntar se quer corrigir
    resposta = input("\n❓ Deseja corrigir o usuário automaticamente? (s/n): ").lower().strip()
    if resposta in ['s', 'sim', 'y', 'yes']:
        corrigir_usuario_alessandro()
        print("\n🔄 Verificando novamente após correção:")
        verificar_usuario_alessandro()
    else:
        print("✋ Correção cancelada pelo usuário")
