#!/usr/bin/env python3
"""
SCRIPT DE REMOÇÃO DE CAMPOS REDUNDANTES
======================================

Remove campos redundantes da base de dados de forma segura,
mantendo apenas os IDs e usando relacionamentos.
"""

import sqlite3
import shutil
from datetime import datetime

def backup_database():
    """Criar backup antes das alterações"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'registroos_backup_remocao_campos_{timestamp}.db'
    shutil.copy2('registroos_new.db', backup_name)
    print(f'✅ Backup criado: {backup_name}')
    return backup_name

def analyze_redundant_fields():
    """Analisar campos redundantes"""
    conn = sqlite3.connect('registroos_new.db')
    cursor = conn.cursor()
    
    print('🔍 Analisando campos redundantes...')
    
    # Verificar uso dos campos string vs ID
    tables_to_check = [
        ('tipo_usuarios', 'setor', 'id_setor'),
        ('tipo_usuarios', 'departamento', 'id_departamento'),
        ('tipos_maquina', 'departamento', 'id_departamento'),
        ('tipos_maquina', 'setor', None),  # Não tem id_setor
        ('tipo_atividade', 'departamento', 'id_departamento'),
        ('tipo_atividade', 'setor', None),  # Não tem id_setor
    ]
    
    for table, string_field, id_field in tables_to_check:
        print(f'\n📋 Tabela: {table}')
        
        # Contar registros com campo string
        cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE {string_field} IS NOT NULL')
        string_count = cursor.fetchone()[0]
        print(f'  Registros com {string_field}: {string_count}')
        
        if id_field:
            # Contar registros com campo ID
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE {id_field} IS NOT NULL')
            id_count = cursor.fetchone()[0]
            print(f'  Registros com {id_field}: {id_count}')
            
            # Verificar inconsistências
            if string_field == 'departamento':
                cursor.execute(f'''
                    SELECT COUNT(*) FROM {table} t
                    LEFT JOIN tipo_departamentos d ON t.{id_field} = d.id
                    WHERE t.{string_field} != d.nome_tipo AND t.{id_field} IS NOT NULL
                ''')
            elif string_field == 'setor':
                cursor.execute(f'''
                    SELECT COUNT(*) FROM {table} t
                    LEFT JOIN tipo_setores s ON t.{id_field} = s.id
                    WHERE t.{string_field} != s.nome AND t.{id_field} IS NOT NULL
                ''')
            
            inconsistent = cursor.fetchone()[0]
            if inconsistent > 0:
                print(f'  ⚠️ Inconsistências encontradas: {inconsistent}')
            else:
                print(f'  ✅ Dados consistentes')
    
    conn.close()

def remove_redundant_fields_phase1():
    """Fase 1: Remover campos string de tabelas com relacionamentos funcionais"""
    conn = sqlite3.connect('registroos_new.db')
    cursor = conn.cursor()
    
    print('\n🗑️ FASE 1: Removendo campos redundantes...')
    
    try:
        # 1. Remover campo 'departamento' de tipo_usuarios (tem id_departamento)
        print('\n1. Removendo campo departamento de tipo_usuarios...')
        cursor.execute('ALTER TABLE tipo_usuarios RENAME TO tipo_usuarios_temp')
        
        cursor.execute('''
            CREATE TABLE tipo_usuarios (
                id INTEGER PRIMARY KEY,
                nome_completo VARCHAR NOT NULL,
                nome_usuario VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                matricula VARCHAR,
                senha_hash VARCHAR NOT NULL,
                setor VARCHAR NOT NULL,
                cargo VARCHAR,
                privilege_level VARCHAR NOT NULL,
                is_approved BOOLEAN NOT NULL,
                data_criacao DATETIME,
                data_ultima_atualizacao DATETIME,
                trabalha_producao BOOLEAN NOT NULL,
                obs_reprovacao TEXT,
                id_setor INTEGER REFERENCES tipo_setores(id),
                id_departamento INTEGER REFERENCES tipo_departamentos(id),
                primeiro_login BOOLEAN NOT NULL
            )
        ''')
        
        cursor.execute('''
            INSERT INTO tipo_usuarios 
            SELECT id, nome_completo, nome_usuario, email, matricula, senha_hash,
                   setor, cargo, privilege_level, is_approved, data_criacao,
                   data_ultima_atualizacao, trabalha_producao, obs_reprovacao,
                   id_setor, id_departamento, primeiro_login
            FROM tipo_usuarios_temp
        ''')
        
        cursor.execute('DROP TABLE tipo_usuarios_temp')
        print('✅ Campo departamento removido de tipo_usuarios')
        
        # 2. Remover campo 'departamento' de tipo_setores (tem id_departamento)
        print('\n2. Removendo campo departamento de tipo_setores...')
        cursor.execute('ALTER TABLE tipo_setores RENAME TO tipo_setores_temp')
        
        cursor.execute('''
            CREATE TABLE tipo_setores (
                id INTEGER PRIMARY KEY,
                nome VARCHAR NOT NULL,
                descricao TEXT,
                ativo BOOLEAN,
                data_criacao DATETIME,
                data_ultima_atualizacao DATETIME,
                id_departamento INTEGER REFERENCES tipo_departamentos(id),
                area_tipo VARCHAR NOT NULL,
                supervisor_responsavel INTEGER,
                permite_apontamento BOOLEAN
            )
        ''')
        
        cursor.execute('''
            INSERT INTO tipo_setores 
            SELECT id, nome, descricao, ativo, data_criacao, data_ultima_atualizacao,
                   id_departamento, area_tipo, supervisor_responsavel, permite_apontamento
            FROM tipo_setores_temp
        ''')
        
        cursor.execute('DROP TABLE tipo_setores_temp')
        print('✅ Campo departamento removido de tipo_setores')
        
        conn.commit()
        print('\n✅ FASE 1 concluída com sucesso!')
        
    except Exception as e:
        print(f'❌ Erro na Fase 1: {e}')
        conn.rollback()
        raise
    
    finally:
        conn.close()

def remove_redundant_fields_phase2():
    """Fase 2: Remover campos não utilizados"""
    conn = sqlite3.connect('registroos_new.db')
    cursor = conn.cursor()
    
    print('\n🗑️ FASE 2: Removendo campos não utilizados...')
    
    try:
        # Remover campos não utilizados de tipos_maquina
        print('\n1. Removendo campos não utilizados de tipos_maquina...')
        cursor.execute('ALTER TABLE tipos_maquina RENAME TO tipos_maquina_temp')
        
        cursor.execute('''
            CREATE TABLE tipos_maquina (
                id INTEGER PRIMARY KEY,
                nome_tipo VARCHAR NOT NULL,
                categoria VARCHAR,
                subcategoria VARCHAR,
                descricao TEXT,
                ativo BOOLEAN,
                data_criacao DATETIME,
                data_ultima_atualizacao DATETIME,
                id_departamento INTEGER REFERENCES tipo_departamentos(id),
                setor VARCHAR,
                departamento TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO tipos_maquina 
            SELECT id, nome_tipo, categoria, subcategoria, descricao, ativo,
                   data_criacao, data_ultima_atualizacao, id_departamento,
                   setor, departamento
            FROM tipos_maquina_temp
        ''')
        
        cursor.execute('DROP TABLE tipos_maquina_temp')
        print('✅ Campos especificacoes_tecnicas e campos_teste_resultado removidos')
        
        conn.commit()
        print('\n✅ FASE 2 concluída com sucesso!')
        
    except Exception as e:
        print(f'❌ Erro na Fase 2: {e}')
        conn.rollback()
        raise
    
    finally:
        conn.close()

def validate_changes():
    """Validar se as mudanças não quebraram nada"""
    conn = sqlite3.connect('registroos_new.db')
    cursor = conn.cursor()
    
    print('\n✅ Validando mudanças...')
    
    # Verificar se as tabelas ainda existem e têm dados
    tables = ['tipo_usuarios', 'tipo_setores', 'tipos_maquina', 'tipo_departamentos']
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'  {table}: {count} registros')
    
    # Verificar se os relacionamentos ainda funcionam
    cursor.execute('''
        SELECT u.nome_completo, s.nome as setor_nome, d.nome_tipo as dept_nome
        FROM tipo_usuarios u
        LEFT JOIN tipo_setores s ON u.id_setor = s.id
        LEFT JOIN tipo_departamentos d ON u.id_departamento = d.id
        LIMIT 3
    ''')
    
    usuarios = cursor.fetchall()
    print('\n📋 Teste de relacionamentos:')
    for usuario in usuarios:
        print(f'  {usuario[0]} -> {usuario[1]} -> {usuario[2]}')
    
    conn.close()
    print('\n✅ Validação concluída!')

if __name__ == "__main__":
    print('🚀 INICIANDO REMOÇÃO DE CAMPOS REDUNDANTES')
    print('=' * 50)
    
    # 1. Backup
    backup_file = backup_database()
    
    # 2. Análise
    analyze_redundant_fields()
    
    # 3. Confirmação
    print('\n⚠️ ATENÇÃO: Esta operação removerá campos redundantes!')
    print('Backup criado:', backup_file)
    
    response = input('\nDeseja continuar? (s/N): ').lower().strip()
    if response != 's':
        print('❌ Operação cancelada pelo usuário')
        exit(0)
    
    # 4. Execução
    try:
        remove_redundant_fields_phase1()
        remove_redundant_fields_phase2()
        validate_changes()
        
        print('\n🎉 REMOÇÃO DE CAMPOS REDUNDANTES CONCLUÍDA!')
        print('✅ Backup disponível em:', backup_file)
        
    except Exception as e:
        print(f'\n❌ ERRO DURANTE A OPERAÇÃO: {e}')
        print(f'🔄 Restaure o backup se necessário: {backup_file}')
