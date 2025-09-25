#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text

def debug_supervisor_setores():
    try:
        db = next(get_db())
        
        print("🔍 DEBUGGING: Por que SUPERVISOR não vê setores")
        print("=" * 60)
        
        # 1. Verificar usuários SUPERVISOR
        print("\n1️⃣ USUÁRIOS SUPERVISOR:")
        result = db.execute(text("""
            SELECT u.id, u.nome_completo, u.email, u.privilege_level, u.trabalha_producao,
                   u.id_setor, u.id_departamento,
                   s.nome as setor_nome, d.nome_tipo as departamento_nome
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON u.id_departamento = d.id
            WHERE u.privilege_level = 'SUPERVISOR' AND u.is_approved = 1
            ORDER BY u.nome_completo
        """))
        supervisores = [dict(row._mapping) for row in result]
        
        for sup in supervisores:
            print(f"  📋 {sup['nome_completo']}")
            print(f"     Email: {sup['email']}")
            print(f"     Trabalha Produção: {sup['trabalha_producao']}")
            print(f"     ID Setor: {sup['id_setor']}")
            print(f"     ID Departamento: {sup['id_departamento']}")
            print(f"     Setor Nome: {sup['setor_nome']}")
            print(f"     Departamento Nome: {sup['departamento_nome']}")
            print()
        
        # 2. Verificar setores disponíveis
        print("\n2️⃣ SETORES DISPONÍVEIS:")
        result = db.execute(text("""
            SELECT id, nome, descricao, id_departamento, ativo
            FROM tipo_setores 
            WHERE ativo = 1
            ORDER BY nome
        """))
        setores = [dict(row._mapping) for row in result]
        
        for setor in setores:
            print(f"  🏭 {setor['nome']} (ID: {setor['id']})")
            print(f"     Departamento ID: {setor['id_departamento']}")
            print(f"     Ativo: {setor['ativo']}")
            print()
        
        # 3. Verificar departamentos
        print("\n3️⃣ DEPARTAMENTOS DISPONÍVEIS:")
        result = db.execute(text("""
            SELECT id, nome_tipo, descricao, ativo
            FROM tipo_departamentos 
            WHERE ativo = 1
            ORDER BY nome_tipo
        """))
        departamentos = [dict(row._mapping) for row in result]
        
        for dept in departamentos:
            print(f"  🏢 {dept['nome_tipo']} (ID: {dept['id']})")
            print(f"     Descrição: {dept['descricao']}")
            print(f"     Ativo: {dept['ativo']}")
            print()
        
        # 4. Verificar mapeamento setor → departamento
        print("\n4️⃣ MAPEAMENTO SETOR → DEPARTAMENTO:")
        result = db.execute(text("""
            SELECT s.id as setor_id, s.nome as setor_nome, 
                   s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE s.ativo = 1
            ORDER BY d.nome_tipo, s.nome
        """))
        mapeamentos = [dict(row._mapping) for row in result]
        
        for map in mapeamentos:
            print(f"  🔗 Setor: {map['setor_nome']} → Departamento: {map['departamento_nome']}")
            print(f"     Setor ID: {map['setor_id']}, Dept ID: {map['id_departamento']}")
            print()
        
        # 5. Simular filtro para cada supervisor
        print("\n5️⃣ SIMULAÇÃO DE FILTROS PARA SUPERVISORES:")
        for sup in supervisores:
            print(f"\n👤 SUPERVISOR: {sup['nome_completo']}")
            
            # Filtro 1: Por ID do setor do usuário
            if sup['id_setor']:
                result = db.execute(text("""
                    SELECT s.id, s.nome, d.nome_tipo as departamento
                    FROM tipo_setores s
                    LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
                    WHERE s.id = :id_setor AND s.ativo = 1
                """), {"id_setor": sup['id_setor']})
                setores_por_id = [dict(row._mapping) for row in result]
                print(f"  🎯 Setores por ID do usuário ({sup['id_setor']}): {len(setores_por_id)}")
                for s in setores_por_id:
                    print(f"     - {s['nome']} (Dept: {s['departamento']})")
            
            # Filtro 2: Por departamento do usuário
            if sup['id_departamento']:
                result = db.execute(text("""
                    SELECT s.id, s.nome, d.nome_tipo as departamento
                    FROM tipo_setores s
                    LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
                    WHERE s.id_departamento = :id_dept AND s.ativo = 1
                """), {"id_dept": sup['id_departamento']})
                setores_por_dept = [dict(row._mapping) for row in result]
                print(f"  🏢 Setores por departamento ({sup['id_departamento']}): {len(setores_por_dept)}")
                for s in setores_por_dept:
                    print(f"     - {s['nome']} (Dept: {s['departamento']})")
            
            # Filtro 3: Por nome do setor (campo texto)
            if sup['setor_nome']:
                result = db.execute(text("""
                    SELECT s.id, s.nome, d.nome_tipo as departamento
                    FROM tipo_setores s
                    LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
                    WHERE s.nome = :setor_nome AND s.ativo = 1
                """), {"setor_nome": sup['setor_nome']})
                setores_por_nome = [dict(row._mapping) for row in result]
                print(f"  📝 Setores por nome '{sup['setor_nome']}': {len(setores_por_nome)}")
                for s in setores_por_nome:
                    print(f"     - {s['nome']} (Dept: {s['departamento']})")

            # Filtro 4: Por nome do departamento (campo texto)
            if sup['departamento_nome']:
                result = db.execute(text("""
                    SELECT s.id, s.nome, d.nome_tipo as departamento
                    FROM tipo_setores s
                    LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
                    WHERE d.nome_tipo = :dept_nome AND s.ativo = 1
                """), {"dept_nome": sup['departamento_nome']})
                setores_por_dept_nome = [dict(row._mapping) for row in result]
                print(f"  🏢 Setores por departamento '{sup['departamento_nome']}': {len(setores_por_dept_nome)}")
                for s in setores_por_dept_nome:
                    print(f"     - {s['nome']} (Dept: {s['departamento']})")
        
        # 6. Verificar endpoint /setores
        print("\n6️⃣ TESTE DO ENDPOINT /setores:")
        result = db.execute(text("""
            SELECT s.id, s.nome, s.descricao, s.id_departamento, s.ativo
            FROM tipo_setores s
            WHERE s.ativo = 1
            ORDER BY s.nome
        """))
        setores_endpoint = [dict(row._mapping) for row in result]
        print(f"  📊 Total de setores ativos: {len(setores_endpoint)}")
        
        # Simular resposta do endpoint
        setores_response = []
        for setor in setores_endpoint:
            setores_response.append({
                "id": setor['id'],
                "nome": setor['nome'],
                "descricao": setor['descricao'],
                "id_departamento": setor['id_departamento'],
                "ativo": setor['ativo']
            })
        
        print(f"  📋 Setores que seriam retornados pelo endpoint:")
        for s in setores_response[:5]:  # Mostrar apenas os primeiros 5
            print(f"     - {s['nome']} (ID: {s['id']}, Dept ID: {s['id_departamento']})")
        if len(setores_response) > 5:
            print(f"     ... e mais {len(setores_response) - 5} setores")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_supervisor_setores()
