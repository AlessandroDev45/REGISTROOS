#!/usr/bin/env python3
"""
CRIAR DADOS DE TESTE COMPLETOS E VÁLIDOS
========================================

Cria 15 registros de cada tipo usando apenas status válidos:
- Apontamentos: ABERTO, EM_ANDAMENTO, FINALIZADO
- Pendências: ABERTA, FECHADA  
- Programações: ENVIADA, EM_ANDAMENTO, CONCLUIDA
- Ordens: ABERTA, EM_ANDAMENTO, CONCLUIDA
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

def conectar_banco():
    """Conecta ao banco de dados"""
    db_path = "RegistroOS/registrooficial/backend/app/registroos_new.db"
    
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
        cursor.execute("DELETE FROM resultados_teste WHERE id_apontamento IN (SELECT id FROM apontamentos_detalhados WHERE numero_os LIKE 'OS2025%')")
        cursor.execute("DELETE FROM pendencias WHERE numero_os LIKE 'OS2025%'")
        cursor.execute("DELETE FROM programacoes WHERE numero_os LIKE 'OS2025%'")
        cursor.execute("DELETE FROM apontamentos_detalhados WHERE numero_os LIKE 'OS2025%'")
        cursor.execute("DELETE FROM ordens_servico WHERE numero_os LIKE 'OS2025%'")
        
        conn.commit()
        print("✅ Dados de teste anteriores removidos")
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados: {e}")
    
    conn.close()

def obter_dados_validos():
    """Obtém dados válidos do banco"""
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
        cursor.execute("SELECT id, nome_tipo FROM tipo_descricao_atividade WHERE ativo = 1")
        dados['descricoes'] = cursor.fetchall()
        
        # Tipos de máquinas ativas
        cursor.execute("SELECT id, nome FROM tipos_maquina WHERE ativo = 1")
        dados['maquinas'] = cursor.fetchall()
        
        # Clientes ativos
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

def criar_ordens_servico_validas(dados, quantidade=15):
    """Cria ordens de serviço com status válidos"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    ordens_criadas = []
    
    print(f"📋 Criando {quantidade} Ordens de Serviço...")
    
    status_validos = ['ABERTA', 'EM_ANDAMENTO', 'CONCLUIDA']
    prioridades_validas = ['BAIXA', 'NORMAL', 'ALTA', 'URGENTE']
    
    for i in range(quantidade):
        try:
            cliente = random.choice(dados['clientes'])
            equipamento = random.choice(dados['equipamentos'])
            
            numero_os = f"OS2025{str(i+1).zfill(4)}"
            data_abertura = datetime.now() - timedelta(days=random.randint(1, 30))
            status = random.choice(status_validos)
            prioridade = random.choice(prioridades_validas)
            
            cursor.execute("""
                INSERT INTO ordens_servico (
                    numero_os, cliente, equipamento, data_abertura, 
                    status, prioridade, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_os,
                cliente[1],  # razao_social
                equipamento[1][:100],  # descricao limitada
                data_abertura.isoformat(),
                status,
                prioridade,
                f"OS de teste - Cliente: {cliente[1]} - Equipamento: {equipamento[1][:50]}"
            ))
            
            ordens_criadas.append(numero_os)
            print(f"   ✅ {i+1:2d}. {numero_os} | {status} | {prioridade} | {cliente[1][:30]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar OS {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(ordens_criadas)} Ordens de Serviço criadas!")
    return ordens_criadas

def criar_apontamentos_validos(dados, ordens_servico, quantidade=15):
    """Cria apontamentos com dados válidos"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    print(f"\n📊 Criando {quantidade} Apontamentos...")
    
    status_validos = ['ABERTO', 'EM_ANDAMENTO', 'FINALIZADO']
    
    for i in range(quantidade):
        try:
            # Selecionar dados relacionados válidos
            usuario = random.choice(dados['usuarios'])
            
            # Encontrar setor do usuário ou usar um aleatório
            setor = None
            if usuario[2]:  # id_setor
                setor = next((s for s in dados['setores'] if s[0] == usuario[2]), None)
            if not setor:
                setor = random.choice(dados['setores'])
            
            # Encontrar departamento do usuário ou usar um aleatório
            departamento = None
            if usuario[3]:  # id_departamento
                departamento = next((d for d in dados['departamentos'] if d[0] == usuario[3]), None)
            if not departamento:
                departamento = random.choice(dados['departamentos'])
            
            atividade = random.choice(dados['atividades'])
            descricao = random.choice(dados['descricoes'])
            maquina = random.choice(dados['maquinas'])
            
            numero_os = random.choice(ordens_servico)
            data_inicio = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            
            status = random.choice(status_validos)
            
            # Se finalizado, definir data_fim
            data_fim = None
            horas_trabalhadas = 0
            if status == 'FINALIZADO':
                data_fim = data_inicio + timedelta(hours=random.randint(1, 8), minutes=random.randint(0, 59))
                horas_trabalhadas = round((data_fim - data_inicio).total_seconds() / 3600, 2)
            
            cursor.execute("""
                INSERT INTO apontamentos_detalhados (
                    numero_os, data_inicio, data_fim, horas_trabalhadas,
                    id_usuario, id_setor, id_departamento,
                    tipo_atividade, descricao_atividade, tipo_maquina,
                    observacao_geral, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_os,
                data_inicio.isoformat(),
                data_fim.isoformat() if data_fim else None,
                horas_trabalhadas,
                usuario[0],      # id
                setor[0],        # id
                departamento[0], # id
                atividade[0],    # id
                descricao[0],    # id
                maquina[0],      # id
                f"Apontamento de teste - {usuario[1][:30]} - {atividade[1][:30]} - {maquina[1][:30]}",
                status
            ))
            
            apontamento_id = cursor.lastrowid
            apontamentos_criados.append(apontamento_id)
            
            print(f"   ✅ {i+1:2d}. ID:{apontamento_id} | {numero_os} | {status} | {usuario[1][:20]} | {setor[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar apontamento {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(apontamentos_criados)} Apontamentos criados!")
    return apontamentos_criados

def criar_pendencias_validas(dados, ordens_servico, apontamentos, quantidade=15):
    """Cria pendências com status válidos"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    pendencias_criadas = []
    
    print(f"\n⚠️ Criando {quantidade} Pendências...")
    
    status_validos = ['ABERTA', 'FECHADA']
    
    for i in range(min(quantidade, len(ordens_servico))):
        try:
            numero_os = ordens_servico[i]
            usuario = random.choice(dados['usuarios'])
            apontamento_origem = random.choice(apontamentos) if apontamentos else None
            
            status = random.choice(status_validos)
            data_inicio = datetime.now() - timedelta(days=random.randint(1, 15))
            
            # Se fechada, definir data_fechamento
            data_fechamento = None
            if status == 'FECHADA':
                data_fechamento = data_inicio + timedelta(days=random.randint(1, 10))
            
            descricoes_pendencia = [
                "Necessário ajuste na calibração do equipamento",
                "Peça com defeito identificado durante inspeção",
                "Documentação técnica incompleta",
                "Teste adicional requerido pelo cliente",
                "Aguardando aprovação do supervisor",
                "Material em falta no estoque",
                "Equipamento apresentou falha durante teste",
                "Revisão de procedimento necessária",
                "Aguardando liberação do laboratório",
                "Componente fora de especificação"
            ]
            
            cursor.execute("""
                INSERT INTO pendencias (
                    numero_os, cliente, data_inicio, id_responsavel_inicio,
                    tipo_maquina, descricao_maquina, descricao_pendencia,
                    status, data_fechamento, id_apontamento_origem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_os,
                random.choice(dados['clientes'])[1],  # razao_social
                data_inicio.isoformat(),
                usuario[0],  # id
                random.choice(dados['maquinas'])[1],  # nome
                f"Equipamento de teste - {random.choice(dados['equipamentos'])[1][:50]}",
                random.choice(descricoes_pendencia),
                status,
                data_fechamento.isoformat() if data_fechamento else None,
                apontamento_origem
            ))
            
            pendencia_id = cursor.lastrowid
            pendencias_criadas.append(pendencia_id)
            
            print(f"   ✅ {i+1:2d}. ID:{pendencia_id} | {numero_os} | {status} | {usuario[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(pendencias_criadas)} Pendências criadas!")
    return pendencias_criadas

def criar_programacoes_validas(dados, ordens_servico, quantidade=15):
    """Cria programações com status válidos"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    programacoes_criadas = []
    
    print(f"\n📅 Criando {quantidade} Programações...")
    
    status_validos = ['ENVIADA', 'EM_ANDAMENTO', 'CONCLUIDA']
    
    for i in range(min(quantidade, len(ordens_servico))):
        try:
            numero_os = ordens_servico[i]
            usuario = random.choice(dados['usuarios'])
            setor = random.choice(dados['setores'])
            
            status = random.choice(status_validos)
            data_criacao = datetime.now() - timedelta(days=random.randint(1, 20))
            data_programada = data_criacao + timedelta(days=random.randint(1, 10))
            
            # Se concluída, definir data_finalizacao
            data_finalizacao = None
            if status == 'CONCLUIDA':
                data_finalizacao = data_programada + timedelta(days=random.randint(0, 5))
            
            observacoes_programacao = [
                "Programação criada conforme cronograma",
                "Prioridade alta - cliente VIP",
                "Aguardando disponibilidade de equipamento",
                "Programação normal de produção",
                "Teste especial solicitado pelo cliente",
                "Retrabalho programado",
                "Inspeção adicional necessária",
                "Programação de manutenção preventiva",
                "Teste de validação de processo",
                "Programação de emergência"
            ]
            
            cursor.execute("""
                INSERT INTO programacoes (
                    numero_os, data_criacao, data_programada, data_finalizacao,
                    usuario_criacao, setor_responsavel, status, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_os,
                data_criacao.isoformat(),
                data_programada.isoformat(),
                data_finalizacao.isoformat() if data_finalizacao else None,
                usuario[0],  # id
                setor[1],    # nome
                status,
                random.choice(observacoes_programacao)
            ))
            
            programacao_id = cursor.lastrowid
            programacoes_criadas.append(programacao_id)
            
            print(f"   ✅ {i+1:2d}. ID:{programacao_id} | {numero_os} | {status} | {setor[1][:20]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(programacoes_criadas)} Programações criadas!")
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 CRIANDO DADOS DE TESTE COMPLETOS E VÁLIDOS")
    print("=" * 60)
    
    # 1. Limpar dados anteriores
    limpar_dados_teste()
    
    # 2. Obter dados válidos
    print("\n📊 Obtendo dados válidos do banco...")
    dados = obter_dados_validos()
    
    if not dados:
        print("❌ Falha ao obter dados válidos!")
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
    ordens = criar_ordens_servico_validas(dados, 15)
    apontamentos = criar_apontamentos_validos(dados, ordens, 15)
    pendencias = criar_pendencias_validas(dados, ordens, apontamentos, 15)
    programacoes = criar_programacoes_validas(dados, ordens, 15)
    
    print("\n" + "=" * 60)
    print("🎉 DADOS DE TESTE CRIADOS COM SUCESSO!")
    print(f"📋 {len(ordens)} Ordens de Serviço")
    print(f"📊 {len(apontamentos)} Apontamentos")
    print(f"⚠️ {len(pendencias)} Pendências")
    print(f"📅 {len(programacoes)} Programações")
    
    print("\n💡 TODOS OS STATUS SÃO VÁLIDOS:")
    print("   - Ordens: ABERTA, EM_ANDAMENTO, CONCLUIDA")
    print("   - Apontamentos: ABERTO, EM_ANDAMENTO, FINALIZADO")
    print("   - Pendências: ABERTA, FECHADA")
    print("   - Programações: ENVIADA, EM_ANDAMENTO, CONCLUIDA")
    
    print("\n🎯 AGORA VOCÊ PODE TESTAR:")
    print("   1. Dashboard com dados realistas")
    print("   2. Funcionalidades de pendências")
    print("   3. Funcionalidades de programações")
    print("   4. Apontamentos com relacionamentos corretos")

if __name__ == "__main__":
    main()
