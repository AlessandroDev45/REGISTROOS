#!/usr/bin/env python3
"""
Teste direto no banco de dados para verificar se os dados existem
"""

import sqlite3
import os

def main():
    print("🧪 TESTE DIRETO NO BANCO DE DADOS")
    print("=" * 50)
    
    # Caminho para o banco de dados
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados")
        
        # Teste 1: Verificar setores de produção
        print("\n1. 🏢 SETORES DE PRODUÇÃO:")
        cursor.execute("""
            SELECT s.id, s.nome, s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE s.area_tipo = 'PRODUCAO'
            ORDER BY s.nome
        """)
        setores = cursor.fetchall()
        print(f"   Encontrados: {len(setores)} setores")
        for setor in setores[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - ID: {setor[0]}, Nome: {setor[1]}, Depto: {setor[3] or 'N/A'}")
        
        # Teste 2: Verificar supervisores de produção
        print("\n2. 👥 SUPERVISORES DE PRODUÇÃO:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.id_setor, s.nome as setor_nome
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            WHERE u.privilege_level = 'SUPERVISOR'
            AND u.trabalha_producao = 1
            AND s.area_tipo = 'PRODUCAO'
            ORDER BY u.nome_completo
        """)
        usuarios = cursor.fetchall()
        print(f"   Encontrados: {len(usuarios)} supervisores")
        for usuario in usuarios:
            print(f"   - ID: {usuario[0]}, Nome: {usuario[1]}, Setor: {usuario[3] or 'N/A'}")
        
        # Teste 3: Verificar departamentos
        print("\n3. 🏛️ DEPARTAMENTOS:")
        cursor.execute("""
            SELECT d.id, d.nome_tipo as nome
            FROM tipo_departamentos d
            ORDER BY d.nome_tipo
        """)
        departamentos = cursor.fetchall()
        print(f"   Encontrados: {len(departamentos)} departamentos")
        for dept in departamentos:
            print(f"   - ID: {dept[0]}, Nome: {dept[1]}")
        
        # Teste 4: Verificar ordens de serviço
        print("\n4. 📋 ORDENS DE SERVIÇO:")
        cursor.execute("""
            SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os,
                   c.nome as cliente_nome, tm.nome as tipo_maquina_nome,
                   s.nome as setor_nome
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN tipo_maquinas tm ON os.id_tipo_maquina = tm.id
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            WHERE os.status_os IN ('ABERTA', 'EM_ANDAMENTO', 'PROGRAMADA')
            ORDER BY os.os_numero DESC
            LIMIT 10
        """)
        ordens = cursor.fetchall()
        print(f"   Encontradas: {len(ordens)} ordens de serviço")
        for ordem in ordens[:3]:  # Mostrar apenas as primeiras 3
            print(f"   - ID: {ordem[0]}, OS: {ordem[1]}, Status: {ordem[3]}")
        
        # Teste 5: Verificar se MOTORES e LABORATORIO existem
        print("\n5. 🔍 VERIFICAÇÃO ESPECÍFICA:")
        
        # Departamento MOTORES
        cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos WHERE nome_tipo = 'MOTORES'")
        motores = cursor.fetchone()
        if motores:
            print(f"   ✅ Departamento MOTORES encontrado: ID {motores[0]}")
        else:
            print("   ❌ Departamento MOTORES não encontrado")
        
        # Setor LABORATORIO DE ENSAIOS ELETRICOS
        cursor.execute("SELECT id, nome, id_departamento FROM tipo_setores WHERE nome LIKE '%LABORATORIO%ENSAIOS%ELETRICOS%'")
        lab = cursor.fetchone()
        if lab:
            print(f"   ✅ Setor LABORATORIO DE ENSAIOS ELETRICOS encontrado: ID {lab[0]}, Depto ID {lab[2]}")
        else:
            print("   ❌ Setor LABORATORIO DE ENSAIOS ELETRICOS não encontrado")
        
        conn.close()
        print("\n🏁 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
