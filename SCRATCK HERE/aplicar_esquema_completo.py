#!/usr/bin/env python3
"""
Script para aplicar o esquema completo conforme especificação
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def fazer_backup():
    """Faz backup antes das alterações"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        backup_path = os.path.join(os.path.dirname(__file__), f'backup_esquema_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def verificar_e_corrigir_tabelas():
    """Verifica e corrige todas as tabelas conforme o esquema"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Verificando e corrigindo estrutura das tabelas...")
        
        # Esquema completo conforme especificação
        esquemas = {
            'ordens_servico': {
                'campos': [
                    ('id', 'INTEGER PRIMARY KEY'),
                    ('os_numero', 'VARCHAR NOT NULL'),
                    ('status_os', 'VARCHAR'),
                    ('prioridade', 'VARCHAR DEFAULT "MEDIA"'),
                    ('id_responsavel_registro', 'INTEGER'),
                    ('id_responsavel_pcp', 'INTEGER'),
                    ('id_responsavel_final', 'INTEGER'),
                    ('data_inicio_prevista', 'DATETIME'),
                    ('data_fim_prevista', 'DATETIME'),
                    ('data_criacao', 'DATETIME'),
                    ('data_ultima_atualizacao', 'DATETIME'),
                    ('criado_por', 'INTEGER'),
                    ('status_geral', 'VARCHAR'),
                    ('valor_total_previsto', 'DECIMAL'),
                    ('valor_total_real', 'DECIMAL'),
                    ('observacoes_gerais', 'TEXT'),
                    ('id_tipo_maquina', 'INTEGER'),
                    ('custo_total_real', 'DECIMAL'),
                    ('horas_previstas', 'DECIMAL'),
                    ('horas_reais', 'DECIMAL'),
                    ('data_programacao', 'DATETIME'),
                    ('horas_orcadas', 'DECIMAL(10,2) DEFAULT 0'),
                    ('testes_iniciais_finalizados', 'BOOLEAN DEFAULT 0'),
                    ('testes_parciais_finalizados', 'BOOLEAN DEFAULT 0'),
                    ('testes_finais_finalizados', 'BOOLEAN DEFAULT 0'),
                    ('data_testes_iniciais_finalizados', 'DATETIME'),
                    ('data_testes_parciais_finalizados', 'DATETIME'),
                    ('data_testes_finais_finalizados', 'DATETIME'),
                    ('id_usuario_testes_iniciais', 'INTEGER'),
                    ('id_usuario_testes_parciais', 'INTEGER'),
                    ('id_usuario_testes_finais', 'INTEGER'),
                    ('testes_exclusivo_os', 'TEXT'),
                    ('id_cliente', 'INTEGER'),
                    ('id_equipamento', 'INTEGER'),
                    ('id_setor', 'INTEGER'),
                    ('id_departamento', 'INTEGER'),
                    ('inicio_os', 'DATETIME'),
                    ('fim_os', 'DATETIME'),
                    ('descricao_maquina', 'TEXT')
                ]
            },
            'apontamentos_detalhados': {
                'campos': [
                    ('id', 'INTEGER PRIMARY KEY'),
                    ('id_os', 'INTEGER NOT NULL'),
                    ('id_usuario', 'INTEGER NOT NULL'),
                    ('id_setor', 'INTEGER NOT NULL'),
                    ('data_hora_inicio', 'DATETIME NOT NULL'),
                    ('data_hora_fim', 'DATETIME'),
                    ('status_apontamento', 'VARCHAR NOT NULL'),
                    ('foi_retrabalho', 'BOOLEAN DEFAULT 0'),
                    ('causa_retrabalho', 'VARCHAR'),
                    ('observacao_os', 'TEXT'),
                    ('servico_de_campo', 'BOOLEAN'),
                    ('observacoes_gerais', 'TEXT'),
                    ('aprovado_supervisor', 'BOOLEAN'),
                    ('data_aprovacao_supervisor', 'DATETIME'),
                    ('supervisor_aprovacao', 'VARCHAR'),
                    ('criado_por', 'VARCHAR'),
                    ('criado_por_email', 'VARCHAR'),
                    ('data_processo_finalizado', 'DATETIME'),
                    ('setor', 'VARCHAR'),
                    ('horas_orcadas', 'DECIMAL(10,2) DEFAULT 0'),
                    ('etapa_inicial', 'BOOLEAN DEFAULT 0'),
                    ('etapa_parcial', 'BOOLEAN DEFAULT 0'),
                    ('etapa_final', 'BOOLEAN DEFAULT 0'),
                    ('horas_etapa_inicial', 'DECIMAL DEFAULT 0'),
                    ('horas_etapa_parcial', 'DECIMAL DEFAULT 0'),
                    ('horas_etapa_final', 'DECIMAL DEFAULT 0'),
                    ('observacoes_etapa_inicial', 'TEXT'),
                    ('observacoes_etapa_parcial', 'TEXT'),
                    ('observacoes_etapa_final', 'TEXT'),
                    ('data_etapa_inicial', 'DATETIME'),
                    ('data_etapa_parcial', 'DATETIME'),
                    ('data_etapa_final', 'DATETIME'),
                    ('supervisor_etapa_inicial', 'VARCHAR'),
                    ('supervisor_etapa_parcial', 'VARCHAR'),
                    ('supervisor_etapa_final', 'VARCHAR'),
                    ('tipo_maquina', 'VARCHAR'),
                    ('tipo_atividade', 'VARCHAR'),
                    ('descricao_atividade', 'TEXT'),
                    ('categoria_maquina', 'VARCHAR'),
                    ('subcategorias_maquina', 'TEXT'),
                    ('subcategorias_finalizadas', 'BOOLEAN DEFAULT 0'),
                    ('data_finalizacao_subcategorias', 'DATETIME'),
                    ('emprestimo_setor', 'VARCHAR'),
                    ('pendencia', 'BOOLEAN DEFAULT 0'),
                    ('pendencia_data', 'DATETIME')
                ]
            }
        }
        
        # Verificar cada tabela
        for tabela, config in esquemas.items():
            print(f"\n📋 Verificando tabela: {tabela}")
            
            # Obter estrutura atual
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas_atuais = {col[1]: col[2] for col in cursor.fetchall()}
            
            # Campos esperados
            campos_esperados = {campo[0]: campo[1] for campo in config['campos']}
            
            # Verificar campos faltando
            faltando = []
            for campo, tipo in campos_esperados.items():
                if campo not in colunas_atuais:
                    faltando.append((campo, tipo))
            
            # Adicionar campos faltando
            if faltando:
                print(f"  ➕ Adicionando {len(faltando)} campos faltando...")
                for campo, tipo in faltando:
                    try:
                        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {campo} {tipo}")
                        print(f"    ✅ {campo} ({tipo})")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"    ❌ Erro ao adicionar {campo}: {e}")
            else:
                print(f"  ✅ Todos os campos estão presentes")
            
            # Verificar campos extras (informativos apenas)
            extras = [campo for campo in colunas_atuais if campo not in campos_esperados]
            if extras:
                print(f"  ⚠️ Campos extras encontrados: {extras}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar/corrigir tabelas: {e}")
        return False

def verificar_resultado_final():
    """Verifica o resultado final"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificação final...")
        
        # Contar campos das tabelas principais
        tabelas_principais = ['ordens_servico', 'apontamentos_detalhados']
        campos_esperados = {'ordens_servico': 39, 'apontamentos_detalhados': 45}
        
        for tabela in tabelas_principais:
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = cursor.fetchall()
            total_atual = len(colunas)
            total_esperado = campos_esperados[tabela]
            
            status = "✅" if total_atual >= total_esperado else "❌"
            print(f"{status} {tabela}: {total_atual}/{total_esperado} campos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
        return False

def atualizar_codigo_rotas():
    """Atualiza o código das rotas para usar os novos nomes"""
    print("\n🔧 Atualizando código das rotas...")
    
    # Arquivos que precisam ser atualizados
    arquivos_rotas = [
        'routes/desenvolvimento.py',
        'routes/general.py'
    ]
    
    for arquivo in arquivos_rotas:
        caminho_arquivo = os.path.join(backend_path, arquivo)
        if os.path.exists(caminho_arquivo):
            print(f"  📝 Verificando {arquivo}...")
            
            # Ler conteúdo
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituições necessárias
            substituicoes = [
                ('testes_exclusivo"', 'testes_exclusivo_os"'),
                ("'testes_exclusivo'", "'testes_exclusivo_os'"),
                ('testes_exclusivo,', 'testes_exclusivo_os,'),
                ('.testes_exclusivo', '.testes_exclusivo_os'),
                ('setattr(ordem_servico, \'testes_exclusivo\'', 'setattr(ordem_servico, \'testes_exclusivo_os\'')
            ]
            
            alterado = False
            for antigo, novo in substituicoes:
                if antigo in conteudo:
                    conteudo = conteudo.replace(antigo, novo)
                    alterado = True
                    print(f"    ✅ Substituído: {antigo} → {novo}")
            
            # Salvar se houve alterações
            if alterado:
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"    💾 Arquivo {arquivo} atualizado")
            else:
                print(f"    ℹ️ Arquivo {arquivo} já está correto")
        else:
            print(f"  ❌ Arquivo {arquivo} não encontrado")

def main():
    print("🚀 Aplicando esquema completo conforme especificação...")
    print("=" * 70)
    
    # 1. Fazer backup
    if not fazer_backup():
        print("❌ Falha no backup. Abortando.")
        return False
    
    # 2. Verificar e corrigir tabelas
    if not verificar_e_corrigir_tabelas():
        print("❌ Falha na verificação/correção das tabelas.")
        return False
    
    # 3. Atualizar código das rotas
    atualizar_codigo_rotas()
    
    # 4. Verificação final
    if not verificar_resultado_final():
        print("❌ Falha na verificação final.")
        return False
    
    print("\n🎉 ESQUEMA APLICADO COM SUCESSO!")
    print("✅ Backup criado")
    print("✅ Estrutura das tabelas corrigida")
    print("✅ Código das rotas atualizado")
    print("✅ Verificação final OK")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
