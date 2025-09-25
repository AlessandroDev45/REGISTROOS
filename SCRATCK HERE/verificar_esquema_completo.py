#!/usr/bin/env python3
"""
Script para verificar se a estrutura do banco está conforme o esquema fornecido
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_estrutura_tabela(cursor, nome_tabela, campos_esperados):
    """Verifica se uma tabela tem os campos esperados"""
    try:
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        if not cursor.fetchone():
            print(f"  ❌ Tabela {nome_tabela} NÃO EXISTE")
            return False
        
        # Obter estrutura da tabela
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas_atuais = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📋 TABELA: {nome_tabela.upper()}")
        print(f"  📊 Campos atuais: {len(colunas_atuais)}")
        print(f"  📊 Campos esperados: {len(campos_esperados)}")
        
        # Verificar campos faltantes
        campos_faltantes = [campo for campo in campos_esperados if campo not in colunas_atuais]
        campos_extras = [campo for campo in colunas_atuais if campo not in campos_esperados]
        
        if campos_faltantes:
            print(f"  ❌ Campos FALTANTES: {campos_faltantes}")
        
        if campos_extras:
            print(f"  ⚠️ Campos EXTRAS: {campos_extras}")
        
        if not campos_faltantes and not campos_extras:
            print(f"  ✅ ESTRUTURA CORRETA!")
            return True
        else:
            print(f"  ⚠️ ESTRUTURA DIVERGENTE")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar {nome_tabela}: {e}")
        return False

def main():
    print("🔍 Verificando estrutura completa do banco conforme esquema...")
    print("=" * 80)
    
    # Conectar ao banco
    banco = os.path.join(backend_path, 'registroos.db')
    if not os.path.exists(banco):
        print(f"❌ Banco não encontrado: {banco}")
        return False
    
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    
    # Definir estruturas esperadas conforme o esquema
    esquemas_esperados = {
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
        ],
        'tipo_usuarios': [
            'id', 'nome_completo', 'nome_usuario', 'email', 'matricula',
            'senha_hash', 'setor', 'cargo', 'departamento', 'privilege_level',
            'is_approved', 'data_criacao', 'data_ultima_atualizacao',
            'trabalha_producao', 'obs_reprovacao', 'id_setor', 'id_departamento',
            'primeiro_login'
        ],
        'tipo_setores': [
            'id', 'nome', 'departamento', 'descricao', 'ativo', 'data_criacao',
            'data_ultima_atualizacao', 'id_departamento', 'area_tipo',
            'supervisor_responsavel', 'permite_apontamento'
        ],
        'tipo_departamentos': [
            'id', 'nome_tipo', 'descricao', 'ativo', 'data_criacao',
            'data_ultima_atualizacao'
        ],
        'tipos_maquina': [
            'id', 'nome_tipo', 'categoria', 'descricao', 'ativo', 'data_criacao',
            'data_ultima_atualizacao', 'id_departamento', 'especificacoes_tecnicas',
            'campos_teste_resultado', 'setor', 'departamento'
        ],
        'tipo_atividade': [
            'id', 'nome_tipo', 'descricao', 'categoria', 'ativo', 'data_criacao',
            'data_ultima_atualizacao', 'id_tipo_maquina'
        ],
        'tipo_descricao_atividade': [
            'id', 'codigo', 'descricao', 'categoria', 'ativo', 'data_criacao',
            'data_ultima_atualizacao', 'setor'
        ],
        'tipo_causas_retrabalho': [
            'id', 'codigo', 'descricao', 'ativo', 'data_criacao',
            'data_ultima_atualizacao', 'id_departamento', 'departamento', 'setor'
        ],
        'tipos_teste': [
            'id', 'nome', 'departamento', 'setor', 'tipo_teste', 'descricao',
            'ativo', 'data_criacao', 'data_ultima_atualizacao', 'tipo_maquina',
            'teste_exclusivo_setor', 'descricao_teste_exclusivo', 'categoria',
            'subcategoria'
        ],
        'clientes': [
            'id', 'razao_social', 'nome_fantasia', 'cnpj_cpf', 'contato_principal',
            'telefone_contato', 'email_contato', 'endereco', 'data_criacao',
            'data_ultima_atualizacao'
        ],
        'equipamentos': [
            'id', 'descricao', 'tipo', 'fabricante', 'modelo', 'numero_serie',
            'data_criacao', 'data_ultima_atualizacao'
        ],
        'pendencias': [
            'id', 'numero_os', 'cliente', 'data_inicio', 'id_responsavel_inicio',
            'tipo_maquina', 'descricao_maquina', 'descricao_pendencia', 'status',
            'prioridade', 'data_fechamento', 'id_responsavel_fechamento',
            'solucao_aplicada', 'observacoes_fechamento', 'id_apontamento_origem',
            'id_apontamento_fechamento', 'tempo_aberto_horas', 'data_criacao',
            'data_ultima_atualizacao'
        ],
        'programacoes': [
            'id', 'id_ordem_servico', 'criado_por_id', 'responsavel_id',
            'observacoes', 'status', 'inicio_previsto', 'fim_previsto',
            'created_at', 'updated_at', 'id_setor'
        ],
        'resultados_teste': [
            'id', 'id_apontamento', 'id_teste', 'resultado', 'observacao',
            'data_registro'
        ],
        'os_testes_exclusivos_finalizados': [
            'id', 'numero_os', 'id_teste_exclusivo', 'nome_teste', 'descricao_teste',
            'usuario_finalizacao', 'departamento', 'setor', 'data_finalizacao',
            'hora_finalizacao', 'descricao_atividade', 'observacoes', 'data_criacao'
        ]
    }
    
    # Verificar cada tabela
    tabelas_corretas = 0
    total_tabelas = len(esquemas_esperados)
    
    for nome_tabela, campos_esperados in esquemas_esperados.items():
        if verificar_estrutura_tabela(cursor, nome_tabela, campos_esperados):
            tabelas_corretas += 1
    
    # Verificar se existem tabelas extras
    print(f"\n🔍 Verificando tabelas extras...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas_existentes = [row[0] for row in cursor.fetchall()]
    
    tabelas_extras = [t for t in tabelas_existentes if t not in esquemas_esperados.keys()]
    if tabelas_extras:
        print(f"  ⚠️ Tabelas EXTRAS encontradas: {tabelas_extras}")
    else:
        print(f"  ✅ Nenhuma tabela extra encontrada")
    
    conn.close()
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL:")
    print(f"  📋 Tabelas corretas: {tabelas_corretas}/{total_tabelas}")
    print(f"  📊 Taxa de conformidade: {(tabelas_corretas/total_tabelas)*100:.1f}%")
    
    if tabelas_corretas == total_tabelas:
        print(f"  🎉 ESTRUTURA 100% CONFORME O ESQUEMA!")
        return True
    else:
        print(f"  ⚠️ ESTRUTURA DIVERGENTE DO ESQUEMA")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
