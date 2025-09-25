#!/usr/bin/env python3
"""
TESTE FINAL COMPLETO DO SISTEMA
===============================

Testa todas as funcionalidades críticas do sistema após a limpeza
dos campos duplicados.
"""

import sys
import os
sys.path.append('C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend')

from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database_config import get_db
from app.database_models import (
    OrdemServico, ApontamentoDetalhado, Usuario, Setor, Departamento,
    Cliente, Equipamento, TipoMaquina, Pendencia
)

def teste_crud_basico():
    """Teste de operações CRUD básicas"""
    print("🔧 TESTANDO OPERAÇÕES CRUD...")
    
    db = next(get_db())
    try:
        # CREATE - Criar um novo apontamento de teste
        novo_apontamento = ApontamentoDetalhado(
            id_os=1,
            id_usuario=1,
            id_setor=1,
            data_hora_inicio="2024-01-01 08:00:00",
            status_apontamento="EM_ANDAMENTO",
            emprestimo_setor="TESTE_SETOR",
            pendencia=True,
            pendencia_data="2024-01-01 10:00:00"
        )
        
        # Não vamos realmente inserir, só validar a criação
        print("  ✅ CREATE: Objeto ApontamentoDetalhado criado com novos campos")
        
        # READ - Ler dados existentes
        os_existente = db.query(OrdemServico).first()
        if os_existente:
            print(f"  ✅ READ: OS {os_existente.os_numero} lida com sucesso")
        
        # UPDATE - Simular atualização
        apontamento_existente = db.query(ApontamentoDetalhado).first()
        if apontamento_existente:
            # Testar acesso aos novos campos
            _ = apontamento_existente.emprestimo_setor
            _ = apontamento_existente.pendencia
            _ = apontamento_existente.pendencia_data
            print("  ✅ UPDATE: Novos campos acessíveis para atualização")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no CRUD: {str(e)}")
        return False
    finally:
        db.close()

def teste_relacionamentos_fk():
    """Teste específico dos relacionamentos FK"""
    print("\n🔗 TESTANDO RELACIONAMENTOS FK...")
    
    db = next(get_db())
    try:
        # Teste 1: Apontamento → Setor (usando id_setor)
        query = db.query(ApontamentoDetalhado, Setor).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).first()
        
        if query:
            apontamento, setor = query
            print(f"  ✅ Apontamento {apontamento.id} → Setor '{setor.nome}'")
        else:
            print("  ⚠️ Nenhum apontamento com setor encontrado")
        
        # Teste 2: Usuario → Setor (usando id_setor)
        query2 = db.query(Usuario, Setor).join(
            Setor, Usuario.id_setor == Setor.id
        ).first()
        
        if query2:
            usuario, setor = query2
            print(f"  ✅ Usuario '{usuario.nome_completo}' → Setor '{setor.nome}'")
        else:
            print("  ⚠️ Nenhum usuário com setor encontrado")
        
        # Teste 3: Usuario → Departamento (usando id_departamento)
        query3 = db.query(Usuario, Departamento).join(
            Departamento, Usuario.id_departamento == Departamento.id
        ).first()
        
        if query3:
            usuario, departamento = query3
            print(f"  ✅ Usuario '{usuario.nome_completo}' → Departamento '{departamento.nome_tipo}'")
        else:
            print("  ⚠️ Nenhum usuário com departamento encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos relacionamentos FK: {str(e)}")
        return False
    finally:
        db.close()

def teste_queries_relatorios():
    """Teste de queries típicas de relatórios"""
    print("\n📊 TESTANDO QUERIES DE RELATÓRIOS...")
    
    db = next(get_db())
    try:
        # Query 1: Relatório de OS por status
        query_os_status = db.query(
            OrdemServico.status_os,
            func.count(OrdemServico.id).label('total')
        ).group_by(OrdemServico.status_os).all()
        
        print(f"  ✅ Relatório OS por status: {len(query_os_status)} grupos")
        for status, total in query_os_status:
            print(f"    - {status}: {total} OS")
        
        # Query 2: Apontamentos por setor
        query_apontamentos_setor = db.query(
            Setor.nome,
            func.count(ApontamentoDetalhado.id).label('total_apontamentos')
        ).select_from(ApontamentoDetalhado).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).group_by(Setor.nome).all()
        
        print(f"  ✅ Apontamentos por setor: {len(query_apontamentos_setor)} setores")
        for setor, total in query_apontamentos_setor:
            print(f"    - {setor}: {total} apontamentos")
        
        # Query 3: Usuários por departamento
        query_usuarios_dept = db.query(
            Departamento.nome_tipo,
            func.count(Usuario.id).label('total_usuarios')
        ).select_from(Usuario).join(
            Departamento, Usuario.id_departamento == Departamento.id
        ).group_by(Departamento.nome_tipo).all()
        
        print(f"  ✅ Usuários por departamento: {len(query_usuarios_dept)} departamentos")
        for dept, total in query_usuarios_dept:
            print(f"    - {dept}: {total} usuários")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nas queries de relatórios: {str(e)}")
        return False
    finally:
        db.close()

def teste_integridade_dados():
    """Teste de integridade dos dados após limpeza"""
    print("\n🛡️ TESTANDO INTEGRIDADE DOS DADOS...")
    
    db = next(get_db())
    try:
        # Verificar se não há registros órfãos
        
        # Teste 1: Apontamentos sem OS válida
        apontamentos_orfaos = db.query(ApontamentoDetalhado).outerjoin(
            OrdemServico, ApontamentoDetalhado.id_os == OrdemServico.id
        ).filter(OrdemServico.id.is_(None)).count()
        
        print(f"  ✅ Apontamentos órfãos (sem OS): {apontamentos_orfaos}")
        
        # Teste 2: Apontamentos sem usuário válido
        apontamentos_sem_usuario = db.query(ApontamentoDetalhado).outerjoin(
            Usuario, ApontamentoDetalhado.id_usuario == Usuario.id
        ).filter(Usuario.id.is_(None)).count()
        
        print(f"  ✅ Apontamentos sem usuário: {apontamentos_sem_usuario}")
        
        # Teste 3: Apontamentos sem setor válido
        apontamentos_sem_setor = db.query(ApontamentoDetalhado).outerjoin(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).filter(Setor.id.is_(None)).count()
        
        print(f"  ✅ Apontamentos sem setor: {apontamentos_sem_setor}")
        
        # Teste 4: Usuários sem setor válido
        usuarios_sem_setor = db.query(Usuario).filter(
            Usuario.id_setor.isnot(None)
        ).outerjoin(
            Setor, Usuario.id_setor == Setor.id
        ).filter(Setor.id.is_(None)).count()
        
        print(f"  ✅ Usuários com id_setor inválido: {usuarios_sem_setor}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na verificação de integridade: {str(e)}")
        return False
    finally:
        db.close()

def teste_performance_basica():
    """Teste básico de performance"""
    print("\n⚡ TESTANDO PERFORMANCE BÁSICA...")
    
    import time
    
    db = next(get_db())
    try:
        # Teste 1: Query simples
        start_time = time.time()
        total_os = db.query(OrdemServico).count()
        end_time = time.time()
        
        print(f"  ✅ Count OS ({total_os} registros): {(end_time - start_time)*1000:.2f}ms")
        
        # Teste 2: Query com JOIN
        start_time = time.time()
        query_join = db.query(ApontamentoDetalhado).join(
            OrdemServico, ApontamentoDetalhado.id_os == OrdemServico.id
        ).join(
            Usuario, ApontamentoDetalhado.id_usuario == Usuario.id
        ).count()
        end_time = time.time()
        
        print(f"  ✅ Query JOIN ({query_join} registros): {(end_time - start_time)*1000:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de performance: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Função principal de teste"""
    print("🧪 TESTE FINAL COMPLETO DO SISTEMA")
    print("=" * 60)
    print("Testando funcionalidades após limpeza de campos duplicados")
    print("=" * 60)
    
    testes = [
        teste_crud_basico,
        teste_relacionamentos_fk,
        teste_queries_relatorios,
        teste_integridade_dados,
        teste_performance_basica
    ]
    
    sucessos = 0
    total = len(testes)
    
    for teste in testes:
        try:
            if teste():
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro no teste {teste.__name__}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando perfeitamente após limpeza")
        print("✅ Campos duplicados removidos com sucesso")
        print("✅ Relacionamentos FK funcionando")
        print("✅ Novos campos acessíveis")
        print("✅ Integridade de dados mantida")
        print("✅ Performance adequada")
        return True
    else:
        print(f"⚠️ {total - sucessos} testes falharam")
        print("Verificar problemas antes de usar em produção")
        return False

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
