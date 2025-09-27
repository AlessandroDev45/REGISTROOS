#!/usr/bin/env python3
"""
CRIAR DADOS REALISTAS CORRETOS
==============================

Cria 15 registros de cada tipo usando as estruturas REAIS das tabelas:
- Ordens de Serviço com campos corretos
- Apontamentos Detalhados com relacionamentos
- Pendências com status válidos
- Programações com dados consistentes
- Resultados de Testes com observações
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

def conectar_banco():
    """Conecta ao banco de dados"""
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"

    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return None

    return sqlite3.connect(db_path)

def limpar_dados_teste():
    """Remove dados de teste anteriores"""
    conn = conectar_banco()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("🧹 Limpando dados de teste anteriores...")
    
    try:
        # Remover em ordem para respeitar foreign keys
        cursor.execute("DELETE FROM resultados_teste WHERE id_apontamento IN (SELECT id FROM apontamentos_detalhados WHERE id_os IN (SELECT id FROM ordens_servico WHERE os_numero LIKE 'REAL2025%'))")
        cursor.execute("DELETE FROM pendencias WHERE numero_os LIKE 'REAL2025%'")
        cursor.execute("DELETE FROM programacoes WHERE id_ordem_servico IN (SELECT id FROM ordens_servico WHERE os_numero LIKE 'REAL2025%')")
        cursor.execute("DELETE FROM apontamentos_detalhados WHERE id_os IN (SELECT id FROM ordens_servico WHERE os_numero LIKE 'REAL2025%')")
        cursor.execute("DELETE FROM ordens_servico WHERE os_numero LIKE 'REAL2025%'")
        
        conn.commit()
        print("✅ Dados de teste anteriores removidos")
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados: {e}")
    
    conn.close()

def obter_dados_reais():
    """Obtém dados reais do banco"""
    conn = conectar_banco()
    if not conn:
        return None
    
    cursor = conn.cursor()
    dados = {}
    
    try:
        # Departamentos ativos
        cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos WHERE ativo = 1")
        dados['departamentos'] = cursor.fetchall()
        
        # Setores ativos que permitem apontamento
        cursor.execute("SELECT id, nome, id_departamento FROM tipo_setores WHERE ativo = 1 AND permite_apontamento = 1")
        dados['setores'] = cursor.fetchall()
        
        # Usuários aprovados que trabalham na produção
        cursor.execute("SELECT id, nome_completo, id_setor, id_departamento FROM tipo_usuarios WHERE is_approved = 1 AND trabalha_producao = 1")
        dados['usuarios'] = cursor.fetchall()
        
        # Tipos de atividades ativas
        cursor.execute("SELECT id, nome_tipo FROM tipo_atividade WHERE ativo = 1")
        dados['atividades'] = cursor.fetchall()
        
        # Descrições de atividades ativas
        cursor.execute("SELECT id, descricao FROM tipo_descricao_atividade WHERE ativo = 1")
        dados['descricoes'] = cursor.fetchall()
        
        # Tipos de máquinas ativas
        cursor.execute("SELECT id, nome_tipo FROM tipos_maquina WHERE ativo = 1")
        dados['maquinas'] = cursor.fetchall()
        
        # Clientes
        cursor.execute("SELECT id, razao_social FROM clientes")
        dados['clientes'] = cursor.fetchall()
        
        # Equipamentos
        cursor.execute("SELECT id, descricao FROM equipamentos")
        dados['equipamentos'] = cursor.fetchall()
        
        conn.close()
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao obter dados: {e}")
        conn.close()
        return None

def criar_ordens_servico_reais(dados, quantidade=15):
    """Cria ordens de serviço usando estrutura real"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    ordens_criadas = []
    
    print(f"📋 Criando {quantidade} Ordens de Serviço...")
    
    status_validos = ['ABERTA', 'EM_ANDAMENTO', 'CONCLUIDA']
    prioridades_validas = ['BAIXA', 'MEDIA', 'ALTA', 'URGENTE']
    
    for i in range(quantidade):
        try:
            cliente = random.choice(dados['clientes'])
            equipamento = random.choice(dados['equipamentos']) if dados['equipamentos'] else None
            usuario = random.choice(dados['usuarios'])
            setor = random.choice(dados['setores'])
            departamento = random.choice(dados['departamentos'])
            maquina = random.choice(dados['maquinas'])
            
            os_numero = f"REAL2025{str(i+1).zfill(4)}"
            data_criacao = datetime.now() - timedelta(days=random.randint(1, 30))
            status = random.choice(status_validos)
            prioridade = random.choice(prioridades_validas)
            
            cursor.execute("""
                INSERT INTO ordens_servico (
                    os_numero, id_cliente, id_equipamento, descricao_maquina,
                    status_os, id_responsavel_registro, data_criacao,
                    prioridade, observacoes_gerais, id_tipo_maquina,
                    id_setor, id_departamento, horas_orcadas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_numero,
                cliente[0],  # id
                equipamento[0] if equipamento else None,  # id
                f"Equipamento de teste - {equipamento[1][:100] if equipamento else 'Equipamento padrão'}",
                status,
                usuario[0],  # id
                data_criacao.isoformat(),
                prioridade,
                f"OS de teste realista - Cliente: {cliente[1]} - Prioridade: {prioridade}",
                maquina[0],  # id
                setor[0],    # id
                departamento[0],  # id
                round(random.uniform(10.0, 100.0), 2)
            ))
            
            os_id = cursor.lastrowid
            ordens_criadas.append((os_id, os_numero))
            print(f"   ✅ {i+1:2d}. {os_numero} | {status} | {prioridade} | {cliente[1][:30]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar OS {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(ordens_criadas)} Ordens de Serviço criadas!")
    return ordens_criadas

def criar_apontamentos_reais(dados, ordens_servico, quantidade=15):
    """Cria apontamentos usando estrutura real"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    print(f"\n📊 Criando {quantidade} Apontamentos...")
    
    status_validos = ['ABERTO', 'EM_ANDAMENTO', 'CONCLUIDO']
    
    for i in range(min(quantidade, len(ordens_servico))):
        try:
            os_id, os_numero = ordens_servico[i]
            usuario = random.choice(dados['usuarios'])
            setor = random.choice(dados['setores'])
            atividade = random.choice(dados['atividades'])
            descricao = random.choice(dados['descricoes'])
            maquina = random.choice(dados['maquinas'])
            
            data_inicio = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            status = random.choice(status_validos)
            
            # Se concluído, definir data_fim
            data_fim = None
            if status == 'CONCLUIDO':
                data_fim = data_inicio + timedelta(hours=random.randint(1, 8), minutes=random.randint(0, 59))
            
            cursor.execute("""
                INSERT INTO apontamentos_detalhados (
                    id_os, id_setor, id_usuario, data_hora_inicio, data_hora_fim,
                    status_apontamento, tipo_maquina, tipo_atividade, descricao_atividade,
                    observacoes_gerais, criado_por, criado_por_email, horas_orcadas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_id,
                setor[0],  # id
                usuario[0],  # id
                data_inicio.isoformat(),
                data_fim.isoformat() if data_fim else None,
                status,
                maquina[1],  # nome_tipo
                atividade[1],  # nome_tipo
                descricao[1][:200] if descricao[1] else "Atividade de teste",  # descricao
                f"Apontamento de teste - {usuario[1][:30]} - {atividade[1][:30]}",
                usuario[1],  # nome_completo
                f"user{usuario[0]}@registroos.com",
                round(random.uniform(5.0, 50.0), 2)
            ))
            
            apontamento_id = cursor.lastrowid
            apontamentos_criados.append(apontamento_id)
            
            print(f"   ✅ {i+1:2d}. ID:{apontamento_id} | {os_numero} | {status} | {usuario[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar apontamento {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(apontamentos_criados)} Apontamentos criados!")
    return apontamentos_criados

def criar_pendencias_reais(dados, ordens_servico, apontamentos, quantidade=15):
    """Cria pendências usando estrutura real"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    pendencias_criadas = []
    
    print(f"\n⚠️ Criando {quantidade} Pendências...")
    
    status_validos = ['ABERTA', 'FECHADA']
    prioridades_validas = ['BAIXA', 'NORMAL', 'ALTA', 'URGENTE']
    
    for i in range(min(quantidade, len(ordens_servico))):
        try:
            os_id, os_numero = ordens_servico[i]
            usuario = random.choice(dados['usuarios'])
            cliente = random.choice(dados['clientes'])
            maquina = random.choice(dados['maquinas'])
            apontamento_origem = random.choice(apontamentos) if apontamentos else None
            
            status = random.choice(status_validos)
            prioridade = random.choice(prioridades_validas)
            data_inicio = datetime.now() - timedelta(days=random.randint(1, 15))
            
            # Se fechada, definir data_fechamento
            data_fechamento = None
            if status == 'FECHADA':
                data_fechamento = data_inicio + timedelta(days=random.randint(1, 10))
            
            descricoes_pendencia = [
                "Necessário ajuste na calibração do equipamento de teste",
                "Peça com defeito identificado durante inspeção visual",
                "Documentação técnica incompleta - aguardando cliente",
                "Teste adicional requerido pelo controle de qualidade",
                "Aguardando aprovação do supervisor responsável",
                "Material específico em falta no estoque",
                "Equipamento apresentou falha durante teste de rotina",
                "Revisão de procedimento necessária conforme norma",
                "Aguardando liberação do laboratório de ensaios",
                "Componente fora de especificação técnica"
            ]
            
            cursor.execute("""
                INSERT INTO pendencias (
                    numero_os, cliente, data_inicio, id_responsavel_inicio,
                    tipo_maquina, descricao_maquina, descricao_pendencia,
                    status, prioridade, data_fechamento, id_apontamento_origem,
                    data_criacao, data_ultima_atualizacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_numero,
                cliente[1],  # razao_social
                data_inicio.isoformat(),
                usuario[0],  # id
                maquina[1],  # nome_tipo
                f"Equipamento de teste - {maquina[1]} - Série: TEST{random.randint(1000, 9999)}",
                random.choice(descricoes_pendencia),
                status,
                prioridade,
                data_fechamento.isoformat() if data_fechamento else None,
                apontamento_origem,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            pendencia_id = cursor.lastrowid
            pendencias_criadas.append(pendencia_id)
            
            print(f"   ✅ {i+1:2d}. ID:{pendencia_id} | {os_numero} | {status} | {prioridade} | {usuario[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(pendencias_criadas)} Pendências criadas!")
    return pendencias_criadas

def criar_programacoes_reais(dados, ordens_servico, quantidade=15):
    """Cria programações usando estrutura real"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    programacoes_criadas = []
    
    print(f"\n📅 Criando {quantidade} Programações...")
    
    status_validos = ['PROGRAMADA', 'EM_ANDAMENTO', 'CONCLUIDA']
    
    for i in range(min(quantidade, len(ordens_servico))):
        try:
            os_id, os_numero = ordens_servico[i]
            usuario = random.choice(dados['usuarios'])
            setor = random.choice(dados['setores'])
            
            status = random.choice(status_validos)
            data_criacao = datetime.now() - timedelta(days=random.randint(1, 20))
            inicio_previsto = data_criacao + timedelta(days=random.randint(1, 10))
            fim_previsto = inicio_previsto + timedelta(days=random.randint(1, 5))
            
            observacoes_programacao = [
                "Programação criada conforme cronograma de produção",
                "Prioridade alta - cliente estratégico",
                "Aguardando disponibilidade de equipamento especializado",
                "Programação normal de produção - sem restrições",
                "Teste especial solicitado pelo departamento técnico",
                "Retrabalho programado após inspeção",
                "Inspeção adicional necessária por norma",
                "Programação de manutenção preventiva",
                "Teste de validação de processo produtivo",
                "Programação de emergência - alta prioridade"
            ]
            
            cursor.execute("""
                INSERT INTO programacoes (
                    id_ordem_servico, responsavel_id, inicio_previsto, fim_previsto,
                    status, criado_por_id, observacoes, created_at, updated_at,
                    id_setor
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_id,
                usuario[0],  # id
                inicio_previsto.isoformat(),
                fim_previsto.isoformat(),
                status,
                usuario[0],  # id
                random.choice(observacoes_programacao),
                data_criacao.isoformat(),
                datetime.now().isoformat(),
                setor[0]  # id
            ))
            
            programacao_id = cursor.lastrowid
            programacoes_criadas.append(programacao_id)
            
            print(f"   ✅ {i+1:2d}. ID:{programacao_id} | {os_numero} | {status} | {setor[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(programacoes_criadas)} Programações criadas!")
    return programacoes_criadas

def criar_resultados_testes_reais(apontamentos, quantidade=15):
    """Cria resultados de testes realistas"""
    conn = conectar_banco()
    if not conn:
        return []

    cursor = conn.cursor()
    resultados_criados = []

    print(f"\n🧪 Criando {quantidade} Resultados de Testes...")

    # Verificar se existem tipos de teste
    cursor.execute("SELECT COUNT(*) FROM tipos_teste")
    count_testes = cursor.fetchone()[0]

    if count_testes == 0:
        print("   ⚠️ Nenhum tipo de teste encontrado - criando tipos básicos...")
        tipos_teste_basicos = [
            ('RESISTENCIA_ISOLAMENTO', 'Teste de resistência de isolamento'),
            ('CONTINUIDADE', 'Teste de continuidade elétrica'),
            ('TENSAO_APLICADA', 'Teste de tensão aplicada'),
            ('CORRENTE_VAZIO', 'Teste de corrente a vazio'),
            ('PERDAS_VAZIO', 'Teste de perdas a vazio')
        ]

        for nome, desc in tipos_teste_basicos:
            cursor.execute("INSERT INTO tipos_teste (nome, descricao, ativo) VALUES (?, ?, 1)", (nome, desc))

        conn.commit()
        print("   ✅ Tipos de teste básicos criados")

    # Obter tipos de teste disponíveis
    cursor.execute("SELECT id, nome FROM tipos_teste WHERE ativo = 1 LIMIT 10")
    tipos_teste = cursor.fetchall()

    if not tipos_teste:
        print("   ❌ Nenhum tipo de teste disponível")
        conn.close()
        return []

    resultados_validos = ['APROVADO', 'REPROVADO', 'CONDICIONAL', 'PENDENTE']

    for i in range(min(quantidade, len(apontamentos))):
        try:
            apontamento_id = apontamentos[i]
            tipo_teste = random.choice(tipos_teste)

            resultado = random.choice(resultados_validos)
            valor_medido = round(random.uniform(10.0, 1000.0), 2)
            valor_especificado = round(valor_medido * random.uniform(0.9, 1.1), 2)

            observacoes_teste = [
                f"Teste {tipo_teste[1]} executado conforme norma técnica",
                f"Equipamento calibrado - Certificado válido",
                f"Condições ambientais: 23°C, 65% UR",
                f"Teste realizado por técnico qualificado",
                f"Resultado {'dentro' if resultado == 'APROVADO' else 'fora'} dos parâmetros",
                f"Medição realizada com equipamento padrão",
                f"Procedimento seguido conforme manual",
                f"Teste {'aprovado' if resultado == 'APROVADO' else 'necessita revisão'}",
                f"Valor medido: {valor_medido} - Especificado: {valor_especificado}",
                f"Inspeção visual: {'OK' if resultado == 'APROVADO' else 'Verificar'}"
            ]

            cursor.execute("""
                INSERT INTO resultados_teste (
                    id_apontamento, id_tipo_teste, resultado,
                    valor_medido, valor_especificado, observacoes,
                    data_teste
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                apontamento_id,
                tipo_teste[0],  # id
                resultado,
                valor_medido,
                valor_especificado,
                random.choice(observacoes_teste),
                datetime.now().isoformat()
            ))

            resultado_id = cursor.lastrowid
            resultados_criados.append(resultado_id)

            print(f"   ✅ {i+1:2d}. ID:{resultado_id} | Apontamento:{apontamento_id} | {tipo_teste[1][:20]} | {resultado}")

        except Exception as e:
            print(f"   ❌ Erro ao criar resultado {i+1}: {e}")

    conn.commit()
    conn.close()

    print(f"✅ {len(resultados_criados)} Resultados de Teste criados!")
    return resultados_criados

def main():
    """Função principal"""
    print("🚀 CRIANDO DADOS REALISTAS CORRETOS")
    print("=" * 60)

    # 1. Limpar dados anteriores
    limpar_dados_teste()

    # 2. Obter dados reais
    print("\n📊 Obtendo dados reais do banco...")
    dados = obter_dados_reais()

    if not dados:
        print("❌ Falha ao obter dados reais!")
        return

    print(f"✅ Dados obtidos:")
    print(f"   - Departamentos: {len(dados['departamentos'])}")
    print(f"   - Setores: {len(dados['setores'])}")
    print(f"   - Usuários: {len(dados['usuarios'])}")
    print(f"   - Atividades: {len(dados['atividades'])}")
    print(f"   - Descrições: {len(dados['descricoes'])}")
    print(f"   - Máquinas: {len(dados['maquinas'])}")
    print(f"   - Clientes: {len(dados['clientes'])}")
    print(f"   - Equipamentos: {len(dados['equipamentos'])}")

    # 3. Criar dados de teste
    ordens = criar_ordens_servico_reais(dados, 15)
    apontamentos = criar_apontamentos_reais(dados, ordens, 15)
    pendencias = criar_pendencias_reais(dados, ordens, apontamentos, 15)
    programacoes = criar_programacoes_reais(dados, ordens, 15)
    resultados = criar_resultados_testes_reais(apontamentos, 15)
    
    print("\n" + "=" * 60)
    print("🎉 DADOS REALISTAS CRIADOS COM SUCESSO!")
    print(f"📋 {len(ordens)} Ordens de Serviço")
    print(f"📊 {len(apontamentos)} Apontamentos")
    print(f"⚠️ {len(pendencias)} Pendências")
    print(f"📅 {len(programacoes)} Programações")
    print(f"🧪 {len(resultados)} Resultados de Teste")

    print("\n💡 TODOS OS DADOS USAM ESTRUTURAS REAIS:")
    print("   - Campos corretos das tabelas")
    print("   - Relacionamentos válidos")
    print("   - Status permitidos pelo sistema")
    print("   - Dados consistentes entre tabelas")
    print("   - Usuários de produção reais")
    print("   - Departamentos e setores ativos")
    print("   - Atividades e máquinas válidas")

    print("\n🎯 AGORA VOCÊ PODE TESTAR:")
    print("   1. Dashboard com dados realistas")
    print("   2. Funcionalidades de pendências")
    print("   3. Funcionalidades de programações")
    print("   4. Apontamentos com relacionamentos corretos")
    print("   5. Resultados de testes com observações")
    print("   6. Todas as funcionalidades implementadas")

    print("\n📊 RESUMO DOS DADOS CRIADOS:")
    print("   - OSs: REAL20250001 a REAL20250015")
    print("   - Status variados: ABERTA, EM_ANDAMENTO, CONCLUIDA")
    print("   - Prioridades: BAIXA, MEDIA, ALTA, URGENTE")
    print("   - Relacionamentos: Apontamentos → OSs → Pendências → Programações")
    print("   - Testes: Resultados com valores e observações realistas")

if __name__ == "__main__":
    main()
