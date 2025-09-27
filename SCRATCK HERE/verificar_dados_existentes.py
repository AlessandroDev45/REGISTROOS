#!/usr/bin/env python3
"""
Verificar dados existentes no banco para criar dados de teste realistas
"""

import sqlite3
import os

def verificar_dados_banco():
    """Verifica dados existentes no banco"""
    db_path = "RegistroOS/registrooficial/backend/app/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO DADOS EXISTENTES NO BANCO")
        print("=" * 60)
        
        # 1. Departamentos
        print("\n1. 🏢 DEPARTAMENTOS:")
        cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos")
        departamentos = cursor.fetchall()
        for row in departamentos:
            print(f"   ID: {row[0]}, Nome: {row[1]}")
        
        # 2. Setores de produção
        print("\n2. 🏭 SETORES (PRODUÇÃO):")
        cursor.execute("PRAGMA table_info(tipo_setores)")
        colunas_setores = [row[1] for row in cursor.fetchall()]
        print(f"   Colunas disponíveis: {colunas_setores}")

        cursor.execute("SELECT id, nome FROM tipo_setores LIMIT 15")
        setores = cursor.fetchall()
        for row in setores:
            print(f"   ID: {row[0]}, Nome: {row[1]}")

        # 3. Usuários de produção
        print("\n3. 👤 USUÁRIOS (PRODUÇÃO):")
        cursor.execute("SELECT id, nome_completo, setor, departamento, privilege_level FROM tipo_usuarios WHERE trabalha_producao = 1 LIMIT 15")
        usuarios = cursor.fetchall()
        for row in usuarios:
            print(f"   ID: {row[0]}, Nome: {row[1]}, Setor: {row[2]}, Dept: {row[3]}, Nível: {row[4]}")

        # 4. Tipos de Atividades
        print("\n4. 🔧 TIPOS DE ATIVIDADES:")
        cursor.execute("SELECT id, nome_tipo FROM tipo_atividade LIMIT 15")
        atividades = cursor.fetchall()
        for row in atividades:
            print(f"   ID: {row[0]}, Nome: {row[1]}")
        
        # 5. Descrições de Atividades
        print("\n5. 📝 DESCRIÇÕES DE ATIVIDADES:")
        cursor.execute("SELECT id, nome_tipo FROM tipo_descricao_atividade LIMIT 15")
        descricoes = cursor.fetchall()
        for row in descricoes:
            print(f"   ID: {row[0]}, Nome: {row[1]}")

        # 6. Tipos de Máquinas
        print("\n6. 🏭 TIPOS DE MÁQUINAS:")
        cursor.execute("SELECT id, nome FROM tipos_maquina LIMIT 15")
        maquinas = cursor.fetchall()
        for row in maquinas:
            print(f"   ID: {row[0]}, Nome: {row[1]}")

        # 7. Tipos de Testes
        print("\n7. 🧪 TIPOS DE TESTES:")
        cursor.execute("SELECT id, nome_tipo FROM tipo_teste LIMIT 15")
        testes = cursor.fetchall()
        for row in testes:
            print(f"   ID: {row[0]}, Nome: {row[1]}")
        
        # 8. Clientes
        print("\n8. 🏢 CLIENTES:")
        cursor.execute("SELECT id, razao_social, nome_fantasia FROM clientes LIMIT 10")
        clientes = cursor.fetchall()
        for row in clientes:
            print(f"   ID: {row[0]}, Razão: {row[1]}, Fantasia: {row[2]}")
        
        # 9. Equipamentos
        print("\n9. 🔧 EQUIPAMENTOS:")
        cursor.execute("SELECT id, descricao, tipo, fabricante FROM equipamentos LIMIT 10")
        equipamentos = cursor.fetchall()
        for row in equipamentos:
            print(f"   ID: {row[0]}, Desc: {row[1][:30]}..., Tipo: {row[2]}, Fab: {row[3]}")
        
        # 10. Ordens de Serviço existentes
        print("\n10. 📋 ORDENS DE SERVIÇO:")
        cursor.execute("SELECT numero_os, cliente, equipamento FROM ordens_servico LIMIT 10")
        ordens = cursor.fetchall()
        for row in ordens:
            print(f"   OS: {row[0]}, Cliente: {row[1]}, Equip: {row[2][:30]}...")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICAÇÃO CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    verificar_dados_banco()
