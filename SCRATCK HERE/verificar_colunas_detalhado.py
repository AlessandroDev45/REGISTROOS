#!/usr/bin/env python3
"""
Script para verificar as colunas reais das tabelas em detalhes
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def mostrar_estrutura_detalhada(cursor, nome_tabela):
    """Mostra a estrutura detalhada de uma tabela"""
    try:
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        if not cursor.fetchone():
            print(f"  ❌ Tabela {nome_tabela} NÃO EXISTE")
            return []
        
        # Obter estrutura detalhada da tabela
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas = cursor.fetchall()
        
        print(f"\n📋 TABELA: {nome_tabela.upper()}")
        print(f"  📊 Total de colunas: {len(colunas)}")
        print(f"  📋 Estrutura detalhada:")
        
        nomes_colunas = []
        for col in colunas:
            cid, name, type_name, notnull, default_value, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            primary = "PRIMARY KEY" if pk else ""
            default = f"DEFAULT {default_value}" if default_value is not None else ""
            
            info_extra = " ".join(filter(None, [nullable, primary, default]))
            print(f"    {cid+1:2d}. {name:<30} {type_name:<15} {info_extra}")
            nomes_colunas.append(name)
        
        return nomes_colunas
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar {nome_tabela}: {e}")
        return []

def comparar_com_esquema(nome_tabela, colunas_reais, colunas_esperadas):
    """Compara colunas reais com esperadas"""
    print(f"\n🔍 COMPARAÇÃO: {nome_tabela.upper()}")
    
    # Campos faltantes
    faltantes = [col for col in colunas_esperadas if col not in colunas_reais]
    if faltantes:
        print(f"  ❌ CAMPOS FALTANTES ({len(faltantes)}):")
        for campo in faltantes:
            print(f"    - {campo}")
    
    # Campos extras
    extras = [col for col in colunas_reais if col not in colunas_esperadas]
    if extras:
        print(f"  ⚠️ CAMPOS EXTRAS ({len(extras)}):")
        for campo in extras:
            print(f"    + {campo}")
    
    # Status
    if not faltantes and not extras:
        print(f"  ✅ ESTRUTURA CORRETA!")
        return True
    else:
        print(f"  ❌ ESTRUTURA DIVERGENTE")
        return False

def main():
    print("🔍 Verificação DETALHADA das colunas das tabelas...")
    print("=" * 80)
    
    # Conectar ao banco
    banco = os.path.join(backend_path, 'registroos.db')
    if not os.path.exists(banco):
        print(f"❌ Banco não encontrado: {banco}")
        return False
    
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    
    # Verificar algumas tabelas principais
    tabelas_para_verificar = {
        'ordens_servico': [
            'id', 'os_numero', 'status_os', 'prioridade', 'id_responsavel_registro',
            'id_responsavel_pcp', 'id_responsavel_final', 'data_inicio_prevista',
            'data_fim_prevista', 'data_criacao', 'data_ultima_atualizacao',
            'criado_por', 'status_geral', 'valor_total_previsto', 'valor_total_real',
            'observacoes_gerais', 'id_tipo_maquina', 'custo_total_real',
            'horas_previstas', 'horas_reais', 'data_programacao', 'horas_orcadas',
            'testes_iniciais_finalizados', 'testes_parciais_finalizados',
            'testes_finais_finalizados', 'data_testes_iniciais_finalizados',
            'data_testes_parciais_finalizados', 'data_testes_finais_finalizados',
            'id_usuario_testes_iniciais', 'id_usuario_testes_parciais',
            'id_usuario_testes_finais', 'testes_exclusivo_os', 'id_cliente',
            'id_equipamento', 'id_setor', 'id_departamento', 'inicio_os',
            'fim_os', 'descricao_maquina'
        ],
        'tipo_usuarios': [
            'id', 'nome_completo', 'nome_usuario', 'email', 'matricula',
            'senha_hash', 'setor', 'cargo', 'departamento', 'privilege_level',
            'is_approved', 'data_criacao', 'data_ultima_atualizacao',
            'trabalha_producao', 'obs_reprovacao', 'id_setor', 'id_departamento',
            'primeiro_login'
        ],
        'apontamentos_detalhados': [
            'id', 'id_os', 'id_usuario', 'id_setor', 'data_hora_inicio',
            'data_hora_fim', 'status_apontamento', 'foi_retrabalho',
            'causa_retrabalho', 'observacao_os', 'servico_de_campo',
            'observacoes_gerais', 'aprovado_supervisor', 'data_aprovacao_supervisor',
            'supervisor_aprovacao', 'criado_por', 'criado_por_email',
            'data_processo_finalizado', 'setor', 'horas_orcadas',
            'etapa_inicial', 'etapa_parcial', 'etapa_final',
            'horas_etapa_inicial', 'horas_etapa_parcial', 'horas_etapa_final',
            'observacoes_etapa_inicial', 'observacoes_etapa_parcial',
            'observacoes_etapa_final', 'data_etapa_inicial', 'data_etapa_parcial',
            'data_etapa_final', 'supervisor_etapa_inicial', 'supervisor_etapa_parcial',
            'supervisor_etapa_final', 'tipo_maquina', 'tipo_atividade',
            'descricao_atividade', 'categoria_maquina', 'subcategorias_maquina',
            'subcategorias_finalizadas', 'data_finalizacao_subcategorias',
            'emprestimo_setor', 'pendencia', 'pendencia_data'
        ]
    }
    
    # Verificar cada tabela
    for nome_tabela, colunas_esperadas in tabelas_para_verificar.items():
        colunas_reais = mostrar_estrutura_detalhada(cursor, nome_tabela)
        comparar_com_esquema(nome_tabela, colunas_reais, colunas_esperadas)
    
    # Mostrar todas as tabelas existentes
    print(f"\n📋 TODAS AS TABELAS NO BANCO:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas_existentes = [row[0] for row in cursor.fetchall()]
    
    for i, tabela in enumerate(tabelas_existentes, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor.fetchone()[0]
        print(f"  {i:2d}. {tabela:<35} ({count} registros)")
    
    conn.close()
    
    print(f"\n🎯 Verificação detalhada concluída!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
