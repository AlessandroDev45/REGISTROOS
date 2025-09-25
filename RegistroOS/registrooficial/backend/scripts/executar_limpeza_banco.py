#!/usr/bin/env python3
"""
Script para executar a limpeza do banco de dados
Remove tabelas e colunas desnecessárias conforme especificado
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config.database_config import DATABASE_URL, engine
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_coluna_existe(connection, tabela, coluna):
    """
    Verifica se uma coluna existe em uma tabela
    """
    try:
        result = connection.execute(text(f"PRAGMA table_info({tabela})"))
        colunas = [row[1] for row in result.fetchall()]
        return coluna in colunas
    except:
        return False

def remover_coluna_se_existe(connection, tabela, coluna):
    """
    Remove uma coluna se ela existir
    """
    if verificar_coluna_existe(connection, tabela, coluna):
        try:
            connection.execute(text(f"ALTER TABLE {tabela} DROP COLUMN {coluna}"))
            connection.commit()
            logger.info(f"✅ Coluna '{coluna}' removida da tabela '{tabela}'")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover coluna '{coluna}' da tabela '{tabela}': {str(e)}")
            return False
    else:
        logger.info(f"⏭️  Coluna '{coluna}' não existe na tabela '{tabela}' (já removida)")
        return True

def executar_limpeza_banco():
    """
    Executa o script de limpeza do banco de dados
    """
    try:
        # Usar o engine já configurado
        logger.info(f"🔗 Conectando ao banco: {DATABASE_URL}")

        logger.info("🔄 Iniciando limpeza do banco de dados...")

        with engine.connect() as connection:

            # 1. REMOVER TABELAS DE HISTÓRICO
            logger.info("🗑️  Removendo tabelas de histórico...")
            tabelas_historico = [
                'ordens_servico_historico',
                'apontamentos_historico',
                'pendencias_historico',
                'programacoes_historico',
                'usuarios_historico',
                'backup_apontamentos',
                'temp_apontamentos',
                'old_apontamentos'
            ]

            for tabela in tabelas_historico:
                try:
                    connection.execute(text(f"DROP TABLE IF EXISTS {tabela}"))
                    connection.commit()
                    logger.info(f"✅ Tabela '{tabela}' removida")
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao remover tabela '{tabela}': {str(e)}")

            # 2. REMOVER COLUNAS DESNECESSÁRIAS DE APONTAMENTOS_DETALHADOS
            logger.info("🔧 Removendo colunas desnecessárias de apontamentos_detalhados...")
            colunas_desnecessarias = [
                'sequencia_repeticao',
                'ensaio_carga',
                'diagnose',
                'teste_inicial_finalizado',
                'teste_inicial_liberado_em',
                'os_finalizada',
                'data_processo_finalizado',
                'pend_criada',
                'pend_fim',
                'pend_finaliza',
                'motivo_falha',
                'resultado_os',
                'setor_do_retrabalho',
                'nome_tecnico',
                'cargo_tecnico',
                'setor_tecnico',
                'departamento_tecnico',
                'matricula_tecnico',
                'observacoes'
            ]

            for coluna in colunas_desnecessarias:
                remover_coluna_se_existe(connection, 'apontamentos_detalhados', coluna)

            # 3. REMOVER COLUNAS DUPLICADAS DE OUTRAS TABELAS
            logger.info("🔧 Removendo colunas duplicadas de outras tabelas...")

            # ordens_servico
            remover_coluna_se_existe(connection, 'ordens_servico', 'setor')
            remover_coluna_se_existe(connection, 'ordens_servico', 'departamento')

            # programacoes
            remover_coluna_se_existe(connection, 'programacoes', 'setor')

            # tipos_maquina
            remover_coluna_se_existe(connection, 'tipos_maquina', 'departamento')

            # causas_retrabalho
            remover_coluna_se_existe(connection, 'causas_retrabalho', 'departamento')
            remover_coluna_se_existe(connection, 'causas_retrabalho', 'setor')

            # tipo_atividade
            remover_coluna_se_existe(connection, 'tipo_atividade', 'setor')
            remover_coluna_se_existe(connection, 'tipo_atividade', 'departamento')

            # descricao_atividade
            remover_coluna_se_existe(connection, 'descricao_atividade', 'setor')
            remover_coluna_se_existe(connection, 'descricao_atividade', 'departamento')

            # tipo_falha
            remover_coluna_se_existe(connection, 'tipo_falha', 'setor')
            remover_coluna_se_existe(connection, 'tipo_falha', 'departamento')

            # 4. CRIAR ÍNDICES OTIMIZADOS
            logger.info("📊 Criando índices otimizados...")
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_apontamentos_id_os ON apontamentos_detalhados(id_os)",
                "CREATE INDEX IF NOT EXISTS idx_apontamentos_id_usuario ON apontamentos_detalhados(id_usuario)",
                "CREATE INDEX IF NOT EXISTS idx_apontamentos_data_inicio ON apontamentos_detalhados(data_hora_inicio)",
                "CREATE INDEX IF NOT EXISTS idx_pendencias_numero_os ON pendencias(numero_os)",
                "CREATE INDEX IF NOT EXISTS idx_ordens_servico_numero ON ordens_servico(os_numero)"
            ]

            for indice in indices:
                try:
                    connection.execute(text(indice))
                    connection.commit()
                    logger.info(f"✅ Índice criado")
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao criar índice: {str(e)}")

            # 5. ANALISAR TABELAS
            logger.info("📈 Analisando tabelas...")
            tabelas_analisar = ['apontamentos_detalhados', 'ordens_servico', 'pendencias', 'programacoes']

            for tabela in tabelas_analisar:
                try:
                    connection.execute(text(f"ANALYZE {tabela}"))
                    connection.commit()
                    logger.info(f"✅ Tabela '{tabela}' analisada")
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao analisar tabela '{tabela}': {str(e)}")

            logger.info("✅ Limpeza do banco de dados concluída!")

            # Verificar estrutura final
            verificar_estrutura_final(connection)

        return True

    except Exception as e:
        logger.error(f"❌ Erro durante a limpeza do banco: {str(e)}")
        return False

def verificar_estrutura_final(connection):
    """
    Verifica a estrutura final das tabelas após a limpeza
    """
    logger.info("🔍 Verificando estrutura final das tabelas...")
    
    tabelas_verificar = [
        'apontamentos_detalhados',
        'ordens_servico', 
        'pendencias',
        'programacoes',
        'tipos_maquina',
        'causas_retrabalho',
        'tipo_atividade',
        'descricao_atividade',
        'tipo_falha'
    ]
    
    for tabela in tabelas_verificar:
        try:
            # Verificar se a tabela existe e suas colunas
            result = connection.execute(text(f"PRAGMA table_info({tabela})"))
            colunas = [row[1] for row in result.fetchall()]
            
            logger.info(f"📊 Tabela '{tabela}': {len(colunas)} colunas")
            logger.info(f"   Colunas: {', '.join(colunas)}")
            
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível verificar tabela '{tabela}': {str(e)}")

def verificar_tabelas_removidas(connection):
    """
    Verifica se as tabelas de histórico foram removidas
    """
    logger.info("🗑️  Verificando tabelas removidas...")
    
    tabelas_historico = [
        'ordens_servico_historico',
        'apontamentos_historico',
        'pendencias_historico',
        'programacoes_historico',
        'usuarios_historico'
    ]
    
    for tabela in tabelas_historico:
        try:
            result = connection.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'"))
            if result.fetchone():
                logger.warning(f"⚠️  Tabela '{tabela}' ainda existe!")
            else:
                logger.info(f"✅ Tabela '{tabela}' removida com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao verificar tabela '{tabela}': {str(e)}")

def main():
    """
    Função principal
    """
    print("=" * 60)
    print("🧹 SCRIPT DE LIMPEZA DO BANCO DE DADOS")
    print("=" * 60)
    print()
    print("Este script irá:")
    print("✅ Remover a tabela ordens_servico_historico")
    print("✅ Remover colunas desnecessárias de apontamentos_detalhados")
    print("✅ Remover colunas duplicadas de várias tabelas")
    print("✅ Otimizar índices e estrutura do banco")
    print()
    
    resposta = input("Deseja continuar? (s/N): ").lower().strip()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário")
        return
    
    print("\n🔄 Iniciando limpeza...")
    
    if executar_limpeza_banco():
        print("\n🎉 Limpeza concluída com sucesso!")
        print("\n📋 Resumo das alterações:")
        print("   - Tabelas de histórico removidas")
        print("   - Colunas duplicadas removidas")
        print("   - Colunas desnecessárias removidas")
        print("   - Índices otimizados")
        print("\n✅ Banco de dados limpo e otimizado!")
    else:
        print("\n❌ Erro durante a limpeza do banco de dados")
        print("   Verifique os logs para mais detalhes")

if __name__ == "__main__":
    main()
