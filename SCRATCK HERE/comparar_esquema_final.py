#!/usr/bin/env python3
"""
Script para comparar estrutura atual com o esquema CORRETO fornecido
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def comparar_tabela_detalhada(cursor, nome_tabela, campos_corretos):
    """Compara uma tabela com o esquema correto"""
    try:
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        if not cursor.fetchone():
            print(f"\n❌ TABELA {nome_tabela.upper()} NÃO EXISTE")
            return False
        
        # Obter estrutura atual
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas_info = cursor.fetchall()
        campos_atuais = [col[1] for col in colunas_info]
        
        print(f"\n📋 TABELA: {nome_tabela.upper()}")
        print(f"  📊 Campos atuais: {len(campos_atuais)} | Corretos: {len(campos_corretos)}")
        
        # Campos faltantes
        faltantes = [campo for campo in campos_corretos if campo not in campos_atuais]
        
        # Campos extras
        extras = [campo for campo in campos_atuais if campo not in campos_corretos]
        
        if faltantes:
            print(f"  ❌ CAMPOS FALTANTES ({len(faltantes)}):")
            for campo in faltantes:
                print(f"    - {campo}")
        
        if extras:
            print(f"  ⚠️ CAMPOS EXTRAS ({len(extras)}):")
            for campo in extras:
                print(f"    + {campo}")
        
        if not faltantes and not extras:
            print(f"  ✅ ESTRUTURA CORRETA!")
            return True
        else:
            print(f"  ❌ ESTRUTURA DIVERGENTE")
            
            # Mostrar comparação lado a lado
            print(f"\n  📋 COMPARAÇÃO DETALHADA:")
            print(f"    ATUAL vs CORRETO:")
            
            max_len = max(len(campos_atuais), len(campos_corretos))
            for i in range(max_len):
                atual = campos_atuais[i] if i < len(campos_atuais) else "---"
                correto = campos_corretos[i] if i < len(campos_corretos) else "---"
                
                if atual == correto:
                    status = "✅"
                elif atual == "---":
                    status = "❌ FALTA"
                elif correto == "---":
                    status = "⚠️ EXTRA"
                else:
                    status = "🔄 DIFERENTE"
                
                print(f"    {i+1:2d}. {atual:<35} | {correto:<35} {status}")
            
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar {nome_tabela}: {e}")
        return False

def main():
    print("🔍 Comparação com o esquema CORRETO fornecido...")
    print("=" * 80)
    
    # Conectar ao banco
    banco = os.path.join(backend_path, 'registroos.db')
    if not os.path.exists(banco):
        print(f"❌ Banco não encontrado: {banco}")
        return False
    
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    
    # Esquemas CORRETOS conforme fornecido pelo usuário
    esquemas_corretos = {
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
        ]
    }
    
    # Verificar cada tabela
    tabelas_corretas = 0
    total_tabelas = len(esquemas_corretos)
    
    for nome_tabela, campos_corretos in esquemas_corretos.items():
        if comparar_tabela_detalhada(cursor, nome_tabela, campos_corretos):
            tabelas_corretas += 1
    
    conn.close()
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL:")
    print(f"  📋 Tabelas verificadas: {total_tabelas}")
    print(f"  ✅ Tabelas corretas: {tabelas_corretas}")
    print(f"  ❌ Tabelas divergentes: {total_tabelas - tabelas_corretas}")
    print(f"  📊 Taxa de conformidade: {(tabelas_corretas/total_tabelas)*100:.1f}%")
    
    if tabelas_corretas == total_tabelas:
        print(f"\n🎉 ESTRUTURA 100% CONFORME O ESQUEMA CORRETO!")
    else:
        print(f"\n⚠️ ESTRUTURA DIVERGENTE - NECESSÁRIO AJUSTAR")
    
    return tabelas_corretas == total_tabelas

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
