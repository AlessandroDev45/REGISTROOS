#!/usr/bin/env python3
"""
Script para verificar TODAS as tabelas em detalhes contra o esquema
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_tabela_completa(cursor, nome_tabela, campos_esperados):
    """Verifica uma tabela completa contra o esquema"""
    try:
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        if not cursor.fetchone():
            print(f"\n❌ TABELA {nome_tabela.upper()} NÃO EXISTE")
            return False
        
        # Obter estrutura da tabela
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas_info = cursor.fetchall()
        colunas_reais = [col[1] for col in colunas_info]
        
        print(f"\n📋 TABELA: {nome_tabela.upper()}")
        print(f"  📊 Campos reais: {len(colunas_reais)} | Esperados: {len(campos_esperados)}")
        
        # Mostrar estrutura real
        print(f"  📋 ESTRUTURA REAL:")
        for i, col in enumerate(colunas_info, 1):
            cid, name, type_name, notnull, default_value, pk = col
            print(f"    {i:2d}. {name}")
        
        # Campos faltantes
        faltantes = [campo for campo in campos_esperados if campo not in colunas_reais]
        if faltantes:
            print(f"  ❌ CAMPOS FALTANTES ({len(faltantes)}):")
            for campo in faltantes:
                print(f"    - {campo}")
        
        # Campos extras
        extras = [campo for campo in colunas_reais if campo not in campos_esperados]
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
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar {nome_tabela}: {e}")
        return False

def main():
    print("🔍 Verificação COMPLETA de TODAS as tabelas...")
    print("=" * 80)
    
    # Conectar ao banco
    banco = os.path.join(backend_path, 'registroos.db')
    if not os.path.exists(banco):
        print(f"❌ Banco não encontrado: {banco}")
        return False
    
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    
    # Esquemas esperados COMPLETOS conforme fornecido
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
        'clientes': [
            'id', 'razao_social', 'nome_fantasia', 'cnpj_cpf', 'contato_principal',
            'telefone_contato', 'email_contato', 'endereco', 'data_criacao',
            'data_ultima_atualizacao'
        ],
        'equipamentos': [
            'id', 'descricao', 'tipo', 'fabricante', 'modelo', 'numero_serie',
            'data_criacao', 'data_ultima_atualizacao'
        ]
    }
    
    # Verificar cada tabela
    tabelas_corretas = 0
    total_tabelas = len(esquemas_esperados)
    
    for nome_tabela, campos_esperados in esquemas_esperados.items():
        if verificar_tabela_completa(cursor, nome_tabela, campos_esperados):
            tabelas_corretas += 1
    
    # Mostrar TODAS as tabelas existentes com suas estruturas
    print(f"\n📋 TODAS AS TABELAS EXISTENTES NO BANCO:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas_existentes = [row[0] for row in cursor.fetchall()]
    
    for tabela in tabelas_existentes:
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor.fetchone()[0]
        
        print(f"\n  📋 {tabela} ({count} registros, {len(colunas)} campos):")
        for col in colunas:
            print(f"    - {col[1]} ({col[2]})")
    
    conn.close()
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL:")
    print(f"  📋 Tabelas verificadas: {total_tabelas}")
    print(f"  ✅ Tabelas corretas: {tabelas_corretas}")
    print(f"  ❌ Tabelas divergentes: {total_tabelas - tabelas_corretas}")
    print(f"  📊 Taxa de conformidade: {(tabelas_corretas/total_tabelas)*100:.1f}%")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
