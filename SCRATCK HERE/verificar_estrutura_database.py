#!/usr/bin/env python3
"""
Script para verificar se a estrutura do database_models.py está conforme o esquema solicitado
"""

import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

# Verificar se o caminho existe
if not os.path.exists(backend_path):
    print(f"❌ Caminho não encontrado: {backend_path}")
    sys.exit(1)

def verificar_estrutura():
    print("🔍 Verificando estrutura do database_models.py...")
    print("=" * 60)
    
    try:
        from app.database_models import (
            # Tabelas principais
            OrdemServico,
            ApontamentoDetalhado, 
            Pendencia,
            Programacao,
            ResultadoTeste,
            OSTesteExclusivoFinalizado,
            
            # Tabelas referenciais
            Cliente,
            Equipamento,
            Usuario,
            Setor,
            Departamento,
            TipoMaquina,
            TipoAtividade,
            TipoDescricaoAtividade,
            TipoCausaRetrabalho,
            TipoTeste,
            
            # Tabelas sistema
            MigrationLog
        )
        
        print("✅ Todas as classes foram importadas com sucesso!")
        
        # Verificar campos específicos da OrdemServico
        print("\n📋 Verificando campos da OrdemServico:")
        os_fields = [
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
        ]
        
        missing_fields = []
        for field in os_fields:
            if not hasattr(OrdemServico, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Campos faltando na OrdemServico: {missing_fields}")
        else:
            print("✅ Todos os campos da OrdemServico estão presentes!")
        
        # Verificar campos específicos do ApontamentoDetalhado
        print("\n📋 Verificando campos do ApontamentoDetalhado:")
        apontamento_fields = [
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
        
        missing_apontamento_fields = []
        for field in apontamento_fields:
            if not hasattr(ApontamentoDetalhado, field):
                missing_apontamento_fields.append(field)
        
        if missing_apontamento_fields:
            print(f"❌ Campos faltando no ApontamentoDetalhado: {missing_apontamento_fields}")
        else:
            print("✅ Todos os campos do ApontamentoDetalhado estão presentes!")
        
        print("\n🎯 Resumo:")
        print(f"✅ OrdemServico: {len(os_fields) - len(missing_fields)}/{len(os_fields)} campos")
        print(f"✅ ApontamentoDetalhado: {len(apontamento_fields) - len(missing_apontamento_fields)}/{len(apontamento_fields)} campos")
        
        if not missing_fields and not missing_apontamento_fields:
            print("\n🎉 ESTRUTURA COMPLETA! Todos os modelos estão conforme o esquema solicitado!")
        else:
            print(f"\n⚠️ Alguns campos estão faltando. Total de problemas: {len(missing_fields) + len(missing_apontamento_fields)}")
        
    except ImportError as e:
        print(f"❌ Erro ao importar modelos: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    verificar_estrutura()
