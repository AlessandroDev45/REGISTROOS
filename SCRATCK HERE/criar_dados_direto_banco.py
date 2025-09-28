#!/usr/bin/env python3
"""
Script para criar dados reais inserindo diretamente no banco de dados:
- 15 Apontamentos
- 15 Pendências  
- 15 Programações
Todos com setores de produção reais
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

# Configurações
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def obter_setores_producao():
    """Obter setores de produção do banco de dados"""
    print("🏭 Obtendo setores de produção...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT s.id, s.nome, s.departamento, s.id_departamento
            FROM tipo_setores s
            WHERE s.ativo = 1
            AND s.nome NOT LIKE '%COMERCIAL%'
            AND s.nome NOT LIKE '%GESTAO%'
            AND s.nome NOT LIKE '%ADMINISTRATIVO%'
            ORDER BY s.nome
        """)
        
        setores = cursor.fetchall()
        conn.close()
        
        print(f"✅ Encontrados {len(setores)} setores de produção")
        return setores
        
    except Exception as e:
        print(f"❌ Erro ao obter setores: {e}")
        return []

def obter_usuarios_producao(setores):
    """Obter usuários dos setores de produção"""
    print("👥 Obtendo usuários de produção...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        setor_ids = [str(s[0]) for s in setores]
        
        cursor.execute(f"""
            SELECT id, nome_completo, email, setor, id_setor
            FROM tipo_usuarios
            WHERE id_setor IN ({','.join(setor_ids)})
            AND is_approved = 1
            ORDER BY nome_completo
        """)
        
        usuarios = cursor.fetchall()
        conn.close()
        
        print(f"✅ Encontrados {len(usuarios)} usuários de produção")
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao obter usuários: {e}")
        return []

def gerar_numero_os():
    """Gerar número de OS aleatório"""
    return random.randint(20000, 99999)

def criar_os_se_necessario(numero_os, conn):
    """Criar OS se não existir"""
    cursor = conn.cursor()

    # Verificar se OS existe (tabela correta: ordens_servico)
    cursor.execute("SELECT id FROM ordens_servico WHERE os_numero = ?", (str(numero_os),))
    os_existente = cursor.fetchone()

    if os_existente:
        return os_existente[0]

    # Criar nova OS
    cursor.execute("""
        INSERT INTO ordens_servico (
            os_numero, cliente, equipamento, status_os, data_criacao
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        str(numero_os),
        f"Cliente OS {numero_os}",
        f"Equipamento OS {numero_os}",
        "ATIVA",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    return cursor.lastrowid

def criar_apontamentos_banco(usuarios, setores):
    """Criar 15 apontamentos diretamente no banco"""
    print("\n📝 Criando apontamentos no banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        apontamentos_criados = 0
        
        for i in range(15):
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            numero_os = gerar_numero_os()
            os_id = criar_os_se_necessario(numero_os, conn)
            
            # Data aleatória nos últimos 30 dias
            data_base = datetime.now() - timedelta(days=random.randint(1, 30))
            hora_inicio = f"{random.randint(7, 16):02d}:{random.choice(['00', '30'])}"
            hora_fim_int = int(hora_inicio.split(':')[0]) + random.randint(1, 8)
            hora_fim = f"{min(hora_fim_int, 23):02d}:{random.choice(['00', '30'])}"
            
            # Inserir apontamento (tabela correta: apontamentos_detalhados)
            cursor.execute("""
                INSERT INTO apontamentos_detalhados (
                    numero_os, id_ordem_servico, cliente, equipamento,
                    tipo_maquina, tipo_atividade, descricao_atividade,
                    data_inicio, hora_inicio, data_fim, hora_fim,
                    observacao, observacao_geral, resultado_global,
                    retrabalho, setor, departamento, usuario_id,
                    data_criacao, status_apontamento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(numero_os), os_id, f"Cliente {i+1}", f"Equipamento {setor[1][:10]}",
                "PRODUCAO", "MANUTENCAO", f"Atividade de produção {i+1}",
                data_base.strftime("%Y-%m-%d"), hora_inicio,
                data_base.strftime("%Y-%m-%d"), hora_fim,
                f"Apontamento {i+1} - {setor[1]}", f"Observação geral {i+1}",
                random.choice(["APROVADO", "APROVADO", "PENDENTE"]),
                random.choice([0, 0, 0, 1]), setor[1], setor[2], usuario[0],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "FINALIZADO"
            ))
            
            apontamentos_criados += 1
            print(f"✅ Apontamento {i+1}/15 criado - OS {numero_os} ({setor[1]})")
        
        conn.commit()
        conn.close()
        
        return apontamentos_criados
        
    except Exception as e:
        print(f"❌ Erro ao criar apontamentos: {e}")
        return 0

def criar_pendencias_banco(usuarios, setores):
    """Criar 15 pendências diretamente no banco"""
    print("\n⚠️ Criando pendências no banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        pendencias_criadas = 0
        
        tipos_pendencia = [
            "MATERIAL_FALTANTE", "EQUIPAMENTO_DEFEITO", 
            "DOCUMENTACAO_PENDENTE", "QUALIDADE_REJEITADA", "PROCESSO_BLOQUEADO"
        ]
        
        for i in range(15):
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            numero_os = gerar_numero_os()
            data_base = datetime.now() - timedelta(days=random.randint(1, 15))
            status = random.choice(["ABERTA", "ABERTA", "ABERTA", "FECHADA"])
            
            # Inserir pendência (tabela correta: pendencias)
            cursor.execute("""
                INSERT INTO pendencias (
                    numero_os, cliente, tipo_maquina, descricao_maquina,
                    descricao_pendencia, prioridade, status,
                    id_usuario_criacao, setor_origem, departamento_origem,
                    data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(numero_os), f"Cliente {i+1}", "PRODUCAO",
                f"Equipamento {setor[1][:10]}",
                f"Pendência {i+1} - {random.choice(['Material em falta', 'Equipamento com defeito', 'Documentação pendente'])}",
                random.choice(["BAIXA", "MEDIA", "ALTA"]), status,
                usuario[0], setor[1], setor[2],
                data_base.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            pendencias_criadas += 1
            print(f"✅ Pendência {i+1}/15 criada - OS {numero_os} ({setor[1]}) - {status}")
        
        conn.commit()
        conn.close()
        
        return pendencias_criadas
        
    except Exception as e:
        print(f"❌ Erro ao criar pendências: {e}")
        return 0

def criar_programacoes_banco(usuarios, setores):
    """Criar 15 programações diretamente no banco"""
    print("\n📅 Criando programações no banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        programacoes_criadas = 0
        
        for i in range(15):
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            numero_os = gerar_numero_os()
            os_id = criar_os_se_necessario(numero_os, conn)
            
            # Data de início nos próximos 30 dias
            data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
            data_fim = data_inicio + timedelta(hours=random.randint(4, 16))
            
            status = random.choice(["PROGRAMADA", "PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA"])
            
            # Inserir programação (tabela correta: programacoes)
            cursor.execute("""
                INSERT INTO programacoes (
                    id_ordem_servico, inicio_previsto, fim_previsto,
                    id_departamento, id_setor, responsavel_id,
                    observacoes, prioridade, status, data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_id,
                data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                setor[3], setor[0], usuario[0],
                f"Programação {i+1} - {setor[1]}",
                random.choice(["BAIXA", "MEDIA", "ALTA"]), status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            programacoes_criadas += 1
            print(f"✅ Programação {i+1}/15 criada - OS {numero_os} ({setor[1]}) - {status}")
        
        conn.commit()
        conn.close()
        
        return programacoes_criadas
        
    except Exception as e:
        print(f"❌ Erro ao criar programações: {e}")
        return 0

def main():
    """Função principal"""
    print("🚀 CRIANDO DADOS REAIS DIRETAMENTE NO BANCO")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return
    
    # Obter dados base
    setores = obter_setores_producao()
    if not setores:
        print("❌ Nenhum setor de produção encontrado!")
        return
    
    usuarios = obter_usuarios_producao(setores)
    if not usuarios:
        print("❌ Nenhum usuário de produção encontrado!")
        return
    
    # Criar registros
    print(f"\n🎯 Criando registros com {len(setores)} setores e {len(usuarios)} usuários...")
    
    apontamentos = criar_apontamentos_banco(usuarios, setores)
    pendencias = criar_pendencias_banco(usuarios, setores)
    programacoes = criar_programacoes_banco(usuarios, setores)
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA CRIAÇÃO:")
    print(f"   ✅ Apontamentos criados: {apontamentos}/15")
    print(f"   ✅ Pendências criadas: {pendencias}/15")
    print(f"   ✅ Programações criadas: {programacoes}/15")
    
    total_criados = apontamentos + pendencias + programacoes
    print(f"\n🎉 Total de registros criados: {total_criados}/45")
    
    if total_criados == 45:
        print("✅ TODOS OS DADOS FORAM CRIADOS COM SUCESSO!")
    else:
        print("⚠️ Alguns registros não foram criados. Verifique os logs acima.")
    
    print("\n💡 Agora você pode:")
    print("1. Acessar o dashboard para ver os dados")
    print("2. Verificar os gráficos atualizados")
    print("3. Testar as funcionalidades com dados reais")

if __name__ == "__main__":
    main()
