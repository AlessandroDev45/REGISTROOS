#!/usr/bin/env python3
"""
Script para verificar a estrutura completa de todas as tabelas
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_estrutura_completa():
    """Verifica a estrutura completa de todas as tabelas"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura completa do banco...")
        print("=" * 80)
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        # Estruturas esperadas conforme o esquema
        estruturas_esperadas = {
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
            ]
        }
        
        for tabela in ['ordens_servico', 'apontamentos_detalhados']:
            if tabela in tabelas:
                print(f"\n📋 TABELA: {tabela.upper()}")
                print("-" * 60)
                
                # Obter estrutura atual
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas_atuais = [col[1] for col in cursor.fetchall()]
                
                # Comparar com estrutura esperada
                esperadas = estruturas_esperadas.get(tabela, [])
                
                print(f"Colunas atuais: {len(colunas_atuais)}")
                print(f"Colunas esperadas: {len(esperadas)}")
                
                # Campos faltando
                faltando = [campo for campo in esperadas if campo not in colunas_atuais]
                if faltando:
                    print(f"\n❌ CAMPOS FALTANDO ({len(faltando)}):")
                    for campo in faltando:
                        print(f"  - {campo}")
                
                # Campos extras (que não deveriam estar)
                extras = [campo for campo in colunas_atuais if campo not in esperadas]
                if extras:
                    print(f"\n⚠️ CAMPOS EXTRAS ({len(extras)}):")
                    for campo in extras:
                        print(f"  - {campo}")
                
                # Status geral
                if not faltando and not extras:
                    print("\n✅ ESTRUTURA CORRETA!")
                else:
                    print(f"\n❌ ESTRUTURA INCORRETA - Faltando: {len(faltando)}, Extras: {len(extras)}")
            else:
                print(f"\n❌ TABELA {tabela} NÃO ENCONTRADA!")
        
        # Verificar outras tabelas importantes
        outras_tabelas = ['pendencias', 'programacoes', 'resultados_teste', 'clientes', 'equipamentos']
        print(f"\n📋 OUTRAS TABELAS:")
        print("-" * 60)
        
        for tabela in outras_tabelas:
            if tabela in tabelas:
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = [col[1] for col in cursor.fetchall()]
                print(f"✅ {tabela}: {len(colunas)} colunas")
            else:
                print(f"❌ {tabela}: NÃO ENCONTRADA")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🔍 Verificando estrutura completa do banco de dados...")
    print("=" * 80)
    
    if not verificar_estrutura_completa():
        return False
    
    print("\n🎯 Verificação concluída!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
