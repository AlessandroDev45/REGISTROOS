#!/usr/bin/env python3
"""
CRIAR DADOS REALISTAS COMPLETOS PARA TESTE
==========================================

Cria 15 registros de cada tipo usando dados reais da API:
- Apontamentos com departamentos, setores, usuários, atividades, máquinas, testes
- Pendências relacionadas aos apontamentos
- Programações com dados consistentes
- Resultados de testes com observações
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

def obter_dados_base():
    """Obtém dados base do banco para criar registros realistas"""
    conn = conectar_banco()
    if not conn:
        return None
    
    cursor = conn.cursor()
    dados = {}
    
    try:
        # Departamentos
        cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos")
        dados['departamentos'] = cursor.fetchall()
        
        # Setores de produção
        cursor.execute("SELECT id, nome, id_departamento FROM tipo_setores WHERE permite_apontamento = 1")
        dados['setores'] = cursor.fetchall()
        
        # Usuários de produção
        cursor.execute("SELECT id, nome_completo, id_setor, id_departamento FROM tipo_usuarios WHERE trabalha_producao = 1 AND is_approved = 1")
        dados['usuarios'] = cursor.fetchall()
        
        # Tipos de atividades
        cursor.execute("SELECT id, nome_tipo FROM tipo_atividade")
        dados['atividades'] = cursor.fetchall()
        
        # Descrições de atividades
        cursor.execute("SELECT id, nome_tipo FROM tipo_descricao_atividade")
        dados['descricoes'] = cursor.fetchall()
        
        # Tipos de máquinas
        cursor.execute("SELECT id, nome FROM tipos_maquina")
        dados['maquinas'] = cursor.fetchall()
        
        # Tipos de testes
        cursor.execute("SELECT id, nome_tipo FROM tipo_teste")
        dados['testes'] = cursor.fetchall()
        
        # Clientes
        cursor.execute("SELECT id, razao_social FROM clientes")
        dados['clientes'] = cursor.fetchall()
        
        # Equipamentos
        cursor.execute("SELECT id, descricao FROM equipamentos")
        dados['equipamentos'] = cursor.fetchall()
        
        conn.close()
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao obter dados base: {e}")
        conn.close()
        return None

def criar_ordens_servico(dados, quantidade=15):
    """Cria ordens de serviço realistas"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    ordens_criadas = []
    
    print(f"📋 Criando {quantidade} Ordens de Serviço...")
    
    for i in range(quantidade):
        try:
            # Dados aleatórios mas realistas
            cliente = random.choice(dados['clientes'])
            equipamento = random.choice(dados['equipamentos'])
            
            numero_os = f"OS{datetime.now().year}{str(i+1).zfill(4)}"
            data_abertura = datetime.now() - timedelta(days=random.randint(1, 30))
            
            cursor.execute("""
                INSERT INTO ordens_servico (
                    numero_os, cliente, equipamento, data_abertura, 
                    status, prioridade, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_os,
                cliente[1],  # razao_social
                equipamento[1][:100],  # descricao (limitada)
                data_abertura.isoformat(),
                'ABERTA',
                random.choice(['NORMAL', 'ALTA', 'URGENTE']),
                f"OS criada para teste - Cliente: {cliente[1]}"
            ))
            
            ordens_criadas.append(numero_os)
            print(f"   ✅ {i+1:2d}. OS: {numero_os} | Cliente: {cliente[1]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar OS {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(ordens_criadas)} Ordens de Serviço criadas!")
    return ordens_criadas

def criar_apontamentos_detalhados(dados, ordens_servico, quantidade=15):
    """Cria apontamentos detalhados realistas"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    print(f"\n📊 Criando {quantidade} Apontamentos Detalhados...")
    
    for i in range(quantidade):
        try:
            # Selecionar dados relacionados
            usuario = random.choice(dados['usuarios'])
            setor = next((s for s in dados['setores'] if s[0] == usuario[2]), random.choice(dados['setores']))
            departamento = next((d for d in dados['departamentos'] if d[0] == usuario[3]), random.choice(dados['departamentos']))
            
            atividade = random.choice(dados['atividades'])
            descricao = random.choice(dados['descricoes'])
            maquina = random.choice(dados['maquinas'])
            
            numero_os = random.choice(ordens_servico)
            data_inicio = datetime.now() - timedelta(days=random.randint(0, 7))
            data_fim = data_inicio + timedelta(hours=random.randint(1, 8))
            
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
                data_fim.isoformat(),
                horas_trabalhadas,
                usuario[0],  # id
                setor[0],    # id
                departamento[0],  # id
                atividade[0],     # id
                descricao[0],     # id
                maquina[0],       # id
                f"Apontamento realizado por {usuario[1]} no setor {setor[1]} - Atividade: {atividade[1]}",
                'FINALIZADO'
            ))
            
            apontamento_id = cursor.lastrowid
            apontamentos_criados.append(apontamento_id)
            
            print(f"   ✅ {i+1:2d}. ID: {apontamento_id} | OS: {numero_os} | Usuário: {usuario[1][:20]} | Setor: {setor[1]}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar apontamento {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(apontamentos_criados)} Apontamentos criados!")
    return apontamentos_criados

def criar_resultados_testes(dados, apontamentos, quantidade=15):
    """Cria resultados de testes para os apontamentos"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    resultados_criados = []
    
    print(f"\n🧪 Criando {quantidade} Resultados de Testes...")
    
    for i in range(min(quantidade, len(apontamentos))):
        try:
            apontamento_id = apontamentos[i]
            teste = random.choice(dados['testes'])
            
            # Resultados realistas
            resultado = random.choice(['APROVADO', 'REPROVADO', 'CONDICIONAL'])
            valor_medido = round(random.uniform(10.0, 100.0), 2)
            valor_especificado = round(valor_medido * random.uniform(0.9, 1.1), 2)
            
            observacoes = [
                f"Teste {teste[1]} executado conforme procedimento",
                f"Valor medido: {valor_medido} - Especificado: {valor_especificado}",
                f"Equipamento calibrado e em condições normais",
                f"Teste realizado em ambiente controlado",
                f"Resultado dentro dos parâmetros esperados" if resultado == 'APROVADO' else f"Necessário retrabalho - {resultado}"
            ]
            
            cursor.execute("""
                INSERT INTO resultados_teste (
                    id_apontamento, id_tipo_teste, resultado,
                    valor_medido, valor_especificado, observacoes,
                    data_teste
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                apontamento_id,
                teste[0],
                resultado,
                valor_medido,
                valor_especificado,
                random.choice(observacoes),
                datetime.now().isoformat()
            ))
            
            resultado_id = cursor.lastrowid
            resultados_criados.append(resultado_id)
            
            print(f"   ✅ {i+1:2d}. ID: {resultado_id} | Apontamento: {apontamento_id} | Teste: {teste[1]} | Resultado: {resultado}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar resultado {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(resultados_criados)} Resultados de Teste criados!")
    return resultados_criados

def main():
    """Função principal"""
    print("🚀 CRIANDO DADOS REALISTAS COMPLETOS")
    print("=" * 60)
    
    # 1. Obter dados base
    print("📊 Obtendo dados base do banco...")
    dados = obter_dados_base()
    
    if not dados:
        print("❌ Falha ao obter dados base!")
        return
    
    print(f"✅ Dados obtidos:")
    print(f"   - Departamentos: {len(dados['departamentos'])}")
    print(f"   - Setores: {len(dados['setores'])}")
    print(f"   - Usuários: {len(dados['usuarios'])}")
    print(f"   - Atividades: {len(dados['atividades'])}")
    print(f"   - Descrições: {len(dados['descricoes'])}")
    print(f"   - Máquinas: {len(dados['maquinas'])}")
    print(f"   - Testes: {len(dados['testes'])}")
    print(f"   - Clientes: {len(dados['clientes'])}")
    print(f"   - Equipamentos: {len(dados['equipamentos'])}")
    
    # 2. Criar ordens de serviço
    ordens_servico = criar_ordens_servico(dados, 15)
    
    if not ordens_servico:
        print("❌ Falha ao criar ordens de serviço!")
        return
    
    # 3. Criar apontamentos detalhados
    apontamentos = criar_apontamentos_detalhados(dados, ordens_servico, 15)
    
    if not apontamentos:
        print("❌ Falha ao criar apontamentos!")
        return
    
    # 4. Criar resultados de testes
    resultados = criar_resultados_testes(dados, apontamentos, 15)
    
    print("\n" + "=" * 60)
    print("🎉 DADOS REALISTAS CRIADOS COM SUCESSO!")
    print(f"📋 {len(ordens_servico)} Ordens de Serviço")
    print(f"📊 {len(apontamentos)} Apontamentos Detalhados")
    print(f"🧪 {len(resultados)} Resultados de Teste")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Execute o script de criação de pendências")
    print("2. Execute o script de criação de programações")
    print("3. Teste o Dashboard e funcionalidades")

if __name__ == "__main__":
    main()
