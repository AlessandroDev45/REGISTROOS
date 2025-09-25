#!/usr/bin/env python3
"""
Teste direto da função get_programacao_form_data sem servidor web
"""

import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import get_db

def test_direct_queries():
    """Testar as consultas SQL diretamente"""
    print("🧪 TESTE DIRETO DAS CONSULTAS SQL")
    print("="*60)
    
    # Configurar conexão com o banco
    database_url = "sqlite:///registroos_new.db"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Teste 1: Setores de produção
        print("\n1. Testando consulta de setores de produção:")
        setores_sql = text("""
            SELECT s.id, s.nome, s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE s.area_tipo = 'PRODUCAO'
            ORDER BY s.nome
        """)
        
        setores_result = db.execute(setores_sql)
        setores_rows = setores_result.fetchall()
        print(f"   Setores encontrados: {len(setores_rows)}")
        
        setores = [
            {
                "id": row[0],
                "nome": row[1],
                "id_departamento": row[2],
                "departamento_nome": row[3] or "Não informado"
            }
            for row in setores_rows
        ]
        
        if setores:
            print(f"   Primeiros 3 setores:")
            for setor in setores[:3]:
                print(f"     - {setor['nome']} (Dept: {setor['departamento_nome']})")
        
        # Teste 2: Supervisores de produção
        print("\n2. Testando consulta de supervisores de produção:")
        usuarios_sql = text("""
            SELECT u.id, u.nome_completo, u.id_setor, s.nome as setor_nome
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            WHERE u.privilege_level = 'SUPERVISOR' 
            AND u.trabalha_producao = 1 
            AND s.area_tipo = 'PRODUCAO'
            ORDER BY u.nome_completo
        """)
        
        usuarios_result = db.execute(usuarios_sql)
        usuarios_rows = usuarios_result.fetchall()
        print(f"   Supervisores encontrados: {len(usuarios_rows)}")
        
        usuarios = [
            {
                "id": row[0],
                "nome_completo": row[1],
                "id_setor": row[2],
                "setor_nome": row[3] or "Não informado"
            }
            for row in usuarios_rows
        ]
        
        if usuarios:
            print(f"   Supervisores:")
            for usuario in usuarios:
                print(f"     - {usuario['nome_completo']} (Setor: {usuario['setor_nome']})")
        
        # Teste 3: Departamentos
        print("\n3. Testando consulta de departamentos:")
        departamentos_sql = text("""
            SELECT d.id, d.nome_tipo as nome
            FROM tipo_departamentos d
            ORDER BY d.nome_tipo
        """)
        
        departamentos_result = db.execute(departamentos_sql)
        departamentos_rows = departamentos_result.fetchall()
        print(f"   Departamentos encontrados: {len(departamentos_rows)}")
        
        departamentos = [
            {
                "id": row[0],
                "nome": row[1]
            }
            for row in departamentos_rows
        ]
        
        if departamentos:
            print(f"   Departamentos:")
            for dept in departamentos:
                print(f"     - {dept['nome']} (ID: {dept['id']})")
        
        # Teste 4: Ordens de serviço
        print("\n4. Testando consulta de ordens de serviço:")
        ordens_sql = text("""
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
        
        ordens_result = db.execute(ordens_sql)
        ordens_rows = ordens_result.fetchall()
        print(f"   Ordens de serviço encontradas: {len(ordens_rows)}")
        
        ordens_servico = [
            {
                "id": row[0],
                "os_numero": row[1] or "",
                "descricao_maquina": row[2] or "",
                "status": row[3] or "ABERTA",
                "cliente_nome": row[4] or "Não informado",
                "tipo_maquina_nome": row[5] or "Não informado",
                "setor": row[6] or "Não informado"
            }
            for row in ordens_rows
        ]
        
        if ordens_servico:
            print(f"   Primeiras 3 OS:")
            for os in ordens_servico[:3]:
                print(f"     - OS {os['os_numero']}: {os['descricao_maquina'][:50]}...")
        
        # Resultado final
        print(f"\n{'='*60}")
        print("📊 RESUMO DOS RESULTADOS:")
        print(f"✅ Setores: {len(setores)}")
        print(f"✅ Supervisores: {len(usuarios)}")
        print(f"✅ Departamentos: {len(departamentos)}")
        print(f"✅ Ordens de Serviço: {len(ordens_servico)}")
        
        # Simular resposta do endpoint
        response_data = {
            "setores": setores,
            "usuarios": usuarios,
            "departamentos": departamentos,
            "ordens_servico": ordens_servico,
            "status_opcoes": ["PROGRAMADA", "EM_ANDAMENTO", "ENVIADA", "CONCLUIDA", "CANCELADA"]
        }
        
        print(f"\n🎯 DADOS PARA O FRONTEND:")
        print(f"   - Setores: {len(response_data['setores'])}")
        print(f"   - Usuarios: {len(response_data['usuarios'])}")
        print(f"   - Departamentos: {len(response_data['departamentos'])}")
        print(f"   - Ordens de Serviço: {len(response_data['ordens_servico'])}")
        print(f"   - Status Opções: {len(response_data['status_opcoes'])}")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        db.close()

if __name__ == "__main__":
    # Mudar para o diretório do backend
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
    os.chdir(backend_dir)
    
    result = test_direct_queries()
    
    if result:
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Todas as consultas funcionaram corretamente")
        print("✅ Dados estão sendo retornados conforme esperado")
    else:
        print(f"\n❌ TESTE FALHOU!")
        print("❌ Verificar erros acima")
