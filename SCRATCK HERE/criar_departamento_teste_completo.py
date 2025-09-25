#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar departamento TESTE com toda a hierarquia necessária
"""

import sys
import os
from datetime import datetime
import json

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import sessionmaker
from config.database_config import engine
from app.database_models import (
    Departamento, Setor, TipoMaquina, TipoTeste, TipoAtividade, 
    TipoDescricaoAtividade, TipoFalha, TipoCausaRetrabalho
)

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def criar_departamento_teste():
    """Cria o departamento TESTE"""
    print("🏢 Criando departamento TESTE...")
    
    # Verificar se já existe
    dept_existente = session.query(Departamento).filter_by(nome_tipo="TESTE").first()
    if dept_existente:
        print(f"   ✅ Departamento TESTE já existe (ID: {dept_existente.id})")
        return dept_existente
    
    # Criar novo departamento
    departamento = Departamento(
        nome_tipo="TESTE",
        descricao="Departamento de Testes e Validação",
        ativo=True,
        data_criacao=datetime.now(),
        data_ultima_atualizacao=datetime.now()
    )
    
    session.add(departamento)
    session.flush()  # Para obter o ID
    
    print(f"   ✅ Departamento TESTE criado (ID: {departamento.id})")
    return departamento

def criar_setor_testes(departamento):
    """Cria o setor TESTES"""
    print("🏭 Criando setor TESTES...")
    
    # Verificar se já existe
    setor_existente = session.query(Setor).filter_by(
        nome="TESTES", 
        departamento="TESTE"
    ).first()
    
    if setor_existente:
        print(f"   ✅ Setor TESTES já existe (ID: {setor_existente.id})")
        return setor_existente
    
    # Criar novo setor
    setor = Setor(
        nome="TESTES",
        departamento="TESTE",
        descricao="Setor de Testes e Validação de Equipamentos",
        ativo=True,
        data_criacao=datetime.now(),
        data_ultima_atualizacao=datetime.now(),
        id_departamento=departamento.id,
        area_tipo="TESTE",  # Campo obrigatório
        supervisor_responsavel=1,  # ID do admin como supervisor padrão
        permite_apontamento=True  # Permitir apontamentos
    )
    
    session.add(setor)
    session.flush()
    
    print(f"   ✅ Setor TESTES criado (ID: {setor.id})")
    return setor

def criar_tipos_maquina():
    """Cria tipos de máquina para o departamento TESTE"""
    print("🔧 Criando tipos de máquina...")
    
    tipos_maquina = [
        {
            "nome_tipo": "EQUIPAMENTO TESTE A",
            "categoria": "CATEGORIA_A",
            "subcategoria": ["SUB_A1", "SUB_A2", "SUB_A3"],
            "descricao": "Equipamento de teste categoria A para validação"
        },
        {
            "nome_tipo": "EQUIPAMENTO TESTE B", 
            "categoria": "CATEGORIA_B",
            "subcategoria": ["SUB_B1", "SUB_B2"],
            "descricao": "Equipamento de teste categoria B para validação"
        },
        {
            "nome_tipo": "EQUIPAMENTO TESTE C",
            "categoria": "CATEGORIA_C", 
            "subcategoria": ["SUB_C1", "SUB_C2", "SUB_C3", "SUB_C4"],
            "descricao": "Equipamento de teste categoria C para validação"
        }
    ]
    
    maquinas_criadas = []
    
    for tipo_data in tipos_maquina:
        # Verificar se já existe
        existente = session.query(TipoMaquina).filter_by(
            nome_tipo=tipo_data["nome_tipo"],
            departamento="TESTE"
        ).first()
        
        if existente:
            print(f"   ✅ {tipo_data['nome_tipo']} já existe")
            maquinas_criadas.append(existente)
            continue
        
        # Criar novo tipo
        maquina = TipoMaquina(
            nome_tipo=tipo_data["nome_tipo"],
            categoria=tipo_data["categoria"],
            subcategoria=json.dumps(tipo_data["subcategoria"]),
            descricao=tipo_data["descricao"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now(),
            departamento="TESTE",
            setor="TESTES"
        )
        
        session.add(maquina)
        session.flush()
        maquinas_criadas.append(maquina)
        
        print(f"   ✅ {tipo_data['nome_tipo']} criado (ID: {maquina.id})")
    
    return maquinas_criadas

def criar_tipos_teste():
    """Cria tipos de teste para o departamento TESTE"""
    print("🧪 Criando tipos de teste...")
    
    tipos_teste = [
        {
            "nome": "TESTE FUNCIONAL BÁSICO",
            "tipo_teste": "FUNCIONAL",
            "descricao": "Teste básico de funcionamento do equipamento",
            "categoria": "BASICO"
        },
        {
            "nome": "TESTE DE PERFORMANCE",
            "tipo_teste": "PERFORMANCE", 
            "descricao": "Teste de performance e eficiência",
            "categoria": "AVANCADO"
        },
        {
            "nome": "TESTE DE SEGURANÇA",
            "tipo_teste": "SEGURANCA",
            "descricao": "Teste de segurança e proteções",
            "categoria": "CRITICO"
        },
        {
            "nome": "TESTE DE DURABILIDADE",
            "tipo_teste": "DURABILIDADE",
            "descricao": "Teste de resistência e durabilidade",
            "categoria": "AVANCADO"
        },
        {
            "nome": "TESTE DE CALIBRAÇÃO",
            "tipo_teste": "CALIBRACAO",
            "descricao": "Teste de calibração e precisão",
            "categoria": "BASICO"
        }
    ]
    
    testes_criados = []
    
    for teste_data in tipos_teste:
        # Verificar se já existe
        existente = session.query(TipoTeste).filter_by(
            nome=teste_data["nome"],
            departamento="TESTE"
        ).first()
        
        if existente:
            print(f"   ✅ {teste_data['nome']} já existe")
            testes_criados.append(existente)
            continue
        
        # Criar novo teste
        teste = TipoTeste(
            nome=teste_data["nome"],
            departamento="TESTE",
            setor="TESTES",
            tipo_teste=teste_data["tipo_teste"],
            descricao=teste_data["descricao"],
            categoria=teste_data["categoria"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        session.add(teste)
        session.flush()
        testes_criados.append(teste)
        
        print(f"   ✅ {teste_data['nome']} criado (ID: {teste.id})")
    
    return testes_criados

def criar_atividades():
    """Cria atividades para o departamento TESTE"""
    print("📋 Criando atividades...")
    
    atividades = [
        {
            "nome_tipo": "PREPARAÇÃO DE TESTE",
            "categoria": "PREPARACAO",
            "descricao": "Atividade de preparação e setup para testes"
        },
        {
            "nome_tipo": "EXECUÇÃO DE TESTE",
            "categoria": "EXECUCAO", 
            "descricao": "Atividade de execução dos testes"
        },
        {
            "nome_tipo": "ANÁLISE DE RESULTADOS",
            "categoria": "ANALISE",
            "descricao": "Atividade de análise e interpretação dos resultados"
        },
        {
            "nome_tipo": "DOCUMENTAÇÃO",
            "categoria": "DOCUMENTACAO",
            "descricao": "Atividade de documentação dos testes realizados"
        }
    ]
    
    atividades_criadas = []
    
    for ativ_data in atividades:
        # Verificar se já existe
        existente = session.query(TipoAtividade).filter_by(
            nome_tipo=ativ_data["nome_tipo"],
            departamento="TESTE"
        ).first()
        
        if existente:
            print(f"   ✅ {ativ_data['nome_tipo']} já existe")
            atividades_criadas.append(existente)
            continue
        
        # Criar nova atividade
        atividade = TipoAtividade(
            nome_tipo=ativ_data["nome_tipo"],
            categoria=ativ_data["categoria"],
            descricao=ativ_data["descricao"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now(),
            departamento="TESTE",
            setor="TESTES"
        )
        
        session.add(atividade)
        session.flush()
        atividades_criadas.append(atividade)
        
        print(f"   ✅ {ativ_data['nome_tipo']} criado (ID: {atividade.id})")
    
    return atividades_criadas

def criar_descricoes_atividade():
    """Cria descrições de atividade para o departamento TESTE"""
    print("📄 Criando descrições de atividade...")

    descricoes = [
        {
            "codigo": "PREP_001",
            "descricao": "PREPARAÇÃO INICIAL - Setup básico do equipamento",
            "categoria": "PREPARACAO"
        },
        {
            "codigo": "PREP_002",
            "descricao": "PREPARAÇÃO AVANÇADA - Configuração completa",
            "categoria": "PREPARACAO"
        },
        {
            "codigo": "EXEC_001",
            "descricao": "EXECUÇÃO BÁSICA - Testes funcionais simples",
            "categoria": "EXECUCAO"
        },
        {
            "codigo": "EXEC_002",
            "descricao": "EXECUÇÃO AVANÇADA - Testes complexos",
            "categoria": "EXECUCAO"
        },
        {
            "codigo": "ANAL_001",
            "descricao": "ANÁLISE PRELIMINAR - Verificação inicial",
            "categoria": "ANALISE"
        },
        {
            "codigo": "ANAL_002",
            "descricao": "ANÁLISE DETALHADA - Estudo completo dos resultados",
            "categoria": "ANALISE"
        },
        {
            "codigo": "DOC_001",
            "descricao": "DOCUMENTAÇÃO BÁSICA - Relatório simples",
            "categoria": "DOCUMENTACAO"
        },
        {
            "codigo": "DOC_002",
            "descricao": "DOCUMENTAÇÃO COMPLETA - Relatório detalhado",
            "categoria": "DOCUMENTACAO"
        }
    ]

    descricoes_criadas = []

    for desc_data in descricoes:
        # Verificar se já existe
        existente = session.query(TipoDescricaoAtividade).filter_by(
            codigo=desc_data["codigo"],
            departamento="TESTE"
        ).first()

        if existente:
            print(f"   ✅ {desc_data['codigo']} já existe")
            descricoes_criadas.append(existente)
            continue

        # Criar nova descrição
        descricao = TipoDescricaoAtividade(
            codigo=desc_data["codigo"],
            descricao=desc_data["descricao"],
            categoria=desc_data["categoria"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now(),
            departamento="TESTE",
            setor="TESTES"
        )

        session.add(descricao)
        session.flush()
        descricoes_criadas.append(descricao)

        print(f"   ✅ {desc_data['codigo']} criado (ID: {descricao.id})")

    return descricoes_criadas

def criar_tipos_falha():
    """Cria tipos de falha para o departamento TESTE"""
    print("⚠️ Criando tipos de falha...")

    tipos_falha = [
        {
            "codigo": "FALHA_001",
            "descricao": "FALHA DE COMUNICAÇÃO - Problema na comunicação",
            "categoria": "COMUNICACAO",
            "severidade": "MEDIA"
        },
        {
            "codigo": "FALHA_002",
            "descricao": "FALHA ELÉTRICA - Problema elétrico",
            "categoria": "ELETRICA",
            "severidade": "ALTA"
        },
        {
            "codigo": "FALHA_003",
            "descricao": "FALHA MECÂNICA - Problema mecânico",
            "categoria": "MECANICA",
            "severidade": "ALTA"
        },
        {
            "codigo": "FALHA_004",
            "descricao": "FALHA DE SOFTWARE - Problema no software",
            "categoria": "SOFTWARE",
            "severidade": "MEDIA"
        },
        {
            "codigo": "FALHA_005",
            "descricao": "FALHA DE CALIBRAÇÃO - Descalibração",
            "categoria": "CALIBRACAO",
            "severidade": "BAIXA"
        },
        {
            "codigo": "FALHA_006",
            "descricao": "FALHA CRÍTICA - Falha que impede funcionamento",
            "categoria": "CRITICA",
            "severidade": "CRITICA"
        }
    ]

    falhas_criadas = []

    for falha_data in tipos_falha:
        # Verificar se já existe
        existente = session.query(TipoFalha).filter_by(
            codigo=falha_data["codigo"]
        ).first()

        if existente:
            print(f"   ✅ {falha_data['codigo']} já existe")
            falhas_criadas.append(existente)
            continue

        # Criar nova falha
        falha = TipoFalha(
            codigo=falha_data["codigo"],
            descricao=falha_data["descricao"],
            categoria=falha_data["categoria"],
            severidade=falha_data["severidade"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        session.add(falha)
        session.flush()
        falhas_criadas.append(falha)

        print(f"   ✅ {falha_data['codigo']} criado (ID: {falha.id})")

    return falhas_criadas

def criar_causas_retrabalho(departamento):
    """Cria causas de retrabalho para o departamento TESTE"""
    print("🔄 Criando causas de retrabalho...")

    causas = [
        {
            "codigo": "RETR_001",
            "descricao": "ERRO NA PREPARAÇÃO - Preparação inadequada"
        },
        {
            "codigo": "RETR_002",
            "descricao": "FALHA NO EQUIPAMENTO - Equipamento apresentou falha"
        },
        {
            "codigo": "RETR_003",
            "descricao": "ERRO HUMANO - Erro do operador"
        },
        {
            "codigo": "RETR_004",
            "descricao": "CONDIÇÕES AMBIENTAIS - Condições inadequadas"
        },
        {
            "codigo": "RETR_005",
            "descricao": "MATERIAL DEFEITUOSO - Material com defeito"
        },
        {
            "codigo": "RETR_006",
            "descricao": "PROCEDIMENTO INCORRETO - Procedimento não seguido"
        }
    ]

    causas_criadas = []

    for causa_data in causas:
        # Verificar se já existe
        existente = session.query(TipoCausaRetrabalho).filter_by(
            codigo=causa_data["codigo"],
            id_departamento=departamento.id
        ).first()

        if existente:
            print(f"   ✅ {causa_data['codigo']} já existe")
            causas_criadas.append(existente)
            continue

        # Criar nova causa
        causa = TipoCausaRetrabalho(
            codigo=causa_data["codigo"],
            descricao=causa_data["descricao"],
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now(),
            id_departamento=departamento.id
        )

        session.add(causa)
        session.flush()
        causas_criadas.append(causa)

        print(f"   ✅ {causa_data['codigo']} criado (ID: {causa.id})")

    return causas_criadas

def main():
    """Função principal para criar toda a hierarquia"""
    print("🚀 CRIANDO DEPARTAMENTO TESTE COM HIERARQUIA COMPLETA")
    print("=" * 60)

    try:
        # 1. Criar departamento
        departamento = criar_departamento_teste()

        # 2. Criar setor
        setor = criar_setor_testes(departamento)

        # 3. Criar tipos de máquina
        maquinas = criar_tipos_maquina()

        # 4. Criar tipos de teste
        testes = criar_tipos_teste()

        # 5. Criar atividades
        atividades = criar_atividades()

        # 6. Criar descrições de atividade
        descricoes = criar_descricoes_atividade()

        # 7. Criar tipos de falha
        falhas = criar_tipos_falha()

        # 8. Criar causas de retrabalho
        causas = criar_causas_retrabalho(departamento)

        # Commit das alterações
        session.commit()

        print("\n" + "=" * 60)
        print("🎯 RESUMO DA CRIAÇÃO:")
        print(f"   🏢 Departamento: TESTE (ID: {departamento.id})")
        print(f"   🏭 Setor: TESTES (ID: {setor.id})")
        print(f"   🔧 Tipos de Máquina: {len(maquinas)} criados")
        print(f"   🧪 Tipos de Teste: {len(testes)} criados")
        print(f"   📋 Atividades: {len(atividades)} criadas")
        print(f"   📄 Descrições: {len(descricoes)} criadas")
        print(f"   ⚠️ Tipos de Falha: {len(falhas)} criados")
        print(f"   🔄 Causas Retrabalho: {len(causas)} criadas")

        print("\n✅ HIERARQUIA COMPLETA CRIADA COM SUCESSO!")

        # Verificar estrutura criada
        verificar_estrutura_criada(departamento)

    except Exception as e:
        print(f"\n❌ ERRO durante a criação: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def verificar_estrutura_criada(departamento):
    """Verifica se toda a estrutura foi criada corretamente"""
    print("\n🔍 VERIFICANDO ESTRUTURA CRIADA:")

    # Verificar departamento
    dept = session.query(Departamento).filter_by(id=departamento.id).first()
    print(f"   🏢 Departamento: {dept.nome_tipo if dept else 'NÃO ENCONTRADO'}")

    # Verificar setor
    setor = session.query(Setor).filter_by(departamento="TESTE").first()
    print(f"   🏭 Setor: {setor.nome if setor else 'NÃO ENCONTRADO'}")

    # Contar registros criados
    count_maquinas = session.query(TipoMaquina).filter_by(departamento="TESTE").count()
    count_testes = session.query(TipoTeste).filter_by(departamento="TESTE").count()
    count_atividades = session.query(TipoAtividade).filter_by(departamento="TESTE").count()
    count_descricoes = session.query(TipoDescricaoAtividade).filter_by(departamento="TESTE").count()
    count_falhas = session.query(TipoFalha).count()
    count_causas = session.query(TipoCausaRetrabalho).filter_by(id_departamento=departamento.id).count()

    print(f"   🔧 Tipos de Máquina: {count_maquinas}")
    print(f"   🧪 Tipos de Teste: {count_testes}")
    print(f"   📋 Atividades: {count_atividades}")
    print(f"   📄 Descrições: {count_descricoes}")
    print(f"   ⚠️ Tipos de Falha: {count_falhas}")
    print(f"   🔄 Causas Retrabalho: {count_causas}")

    print("\n🌳 ESTRUTURA HIERÁRQUICA COMPLETA:")
    print("   TESTE (Departamento)")
    print("   └── TESTES (Setor)")
    print("       ├── EQUIPAMENTO TESTE A, B, C (Máquinas)")
    print("       ├── 5 Tipos de Teste (Funcional, Performance, etc.)")
    print("       ├── 4 Atividades (Preparação, Execução, etc.)")
    print("       ├── 8 Descrições de Atividade")
    print("       ├── 6 Tipos de Falha")
    print("       └── 6 Causas de Retrabalho")

if __name__ == "__main__":
    main()
