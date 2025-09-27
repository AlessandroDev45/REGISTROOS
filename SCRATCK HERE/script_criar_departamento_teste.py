#!/usr/bin/env python3
"""
SCRIPT PARA CRIAR DEPARTAMENTO TESTE COMPLETO
==============================================

Este script cria:
1. Departamento TESTE
2. Setor TESTES 
3. Um de cada tipo de catálogo para o departamento TESTE:
   - 1 Tipo de Máquina
   - 1 Tipo de Teste
   - 1 Atividade
   - 1 Descrição de Atividade
   - 1 Tipo de Falha
   - 1 Causa de Retrabalho

NOMENCLATURA: CAIXA ALTA SEM CARACTERES ESPECIAIS
VALIDAÇÕES: Adiciona validações sem criar nada novo
CORREÇÕES: Corrige inconsistências de nome_tipo vs nome
"""

import sqlite3
import os
import sys
from datetime import datetime

# Configurações
BACKEND_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
DB_PATH = os.path.join(BACKEND_PATH, "registroos_new.db")

def conectar_banco():
    """Conecta ao banco de dados"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_departamento_teste(conn):
    """Verifica se o departamento TESTE já existe"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos WHERE nome_tipo = 'TESTE'")
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Departamento TESTE já existe (ID: {result['id']})")
        return result['id']
    else:
        print("ℹ️ Departamento TESTE não existe - será criado")
        return None

def criar_departamento_teste(conn):
    """Cria o departamento TESTE"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_departamentos (nome_tipo, descricao, ativo, data_criacao, data_ultima_atualizacao)
            VALUES (?, ?, ?, ?, ?)
        """, (
            'TESTE',
            'DEPARTAMENTO DE TESTES E VALIDACAO',
            True,
            datetime.now(),
            datetime.now()
        ))
        
        dept_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Departamento TESTE criado (ID: {dept_id})")
        return dept_id
        
    except Exception as e:
        print(f"❌ Erro ao criar departamento TESTE: {e}")
        conn.rollback()
        return None

def verificar_setor_testes(conn, dept_id):
    """Verifica se o setor TESTES já existe"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome FROM tipo_setores 
        WHERE nome = 'TESTES' AND id_departamento = ?
    """, (dept_id,))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Setor TESTES já existe (ID: {result['id']})")
        return result['id']
    else:
        print("ℹ️ Setor TESTES não existe - será criado")
        return None

def criar_setor_testes(conn, dept_id):
    """Cria o setor TESTES"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_setores (
                nome, departamento, descricao, ativo, data_criacao, data_ultima_atualizacao,
                id_departamento, area_tipo, supervisor_responsavel, permite_apontamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'TESTES',
            'TESTE',  # Campo de compatibilidade
            'SETOR DE TESTES E VALIDACAO',
            True,
            datetime.now(),
            datetime.now(),
            dept_id,
            'TESTE',
            1,  # Admin como supervisor
            True
        ))
        
        setor_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Setor TESTES criado (ID: {setor_id})")
        return setor_id
        
    except Exception as e:
        print(f"❌ Erro ao criar setor TESTES: {e}")
        conn.rollback()
        return None

def criar_tipo_maquina_teste(conn, dept_id):
    """Cria um tipo de máquina para teste"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipos_maquina (
                nome_tipo, categoria, subcategoria, descricao, ativo, 
                data_criacao, data_ultima_atualizacao, id_departamento,
                setor, departamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'EQUIPAMENTO TESTE PADRAO',
            'TESTE',
            'PADRAO',
            'EQUIPAMENTO PADRAO PARA TESTES E VALIDACAO',
            True,
            datetime.now(),
            datetime.now(),
            dept_id,
            'TESTES',  # Campo de compatibilidade
            'TESTE'    # Campo de compatibilidade
        ))
        
        tipo_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Tipo de Máquina TESTE criado (ID: {tipo_id})")
        return tipo_id
        
    except Exception as e:
        print(f"❌ Erro ao criar tipo de máquina: {e}")
        conn.rollback()
        return None

def criar_tipo_teste(conn, dept_id, tipo_maquina_id):
    """Cria um tipo de teste"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipos_teste (
                nome, departamento, setor, tipo_teste, descricao, ativo,
                data_criacao, data_ultima_atualizacao, tipo_maquina,
                categoria, subcategoria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'TESTE FUNCIONAL BASICO',
            'TESTE',
            'TESTES',
            'FUNCIONAL',
            'TESTE FUNCIONAL BASICO PARA VALIDACAO',
            True,
            datetime.now(),
            datetime.now(),
            tipo_maquina_id,
            'FUNCIONAL',
            0  # Padrão
        ))
        
        teste_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Tipo de Teste criado (ID: {teste_id})")
        return teste_id
        
    except Exception as e:
        print(f"❌ Erro ao criar tipo de teste: {e}")
        conn.rollback()
        return None

def criar_tipo_atividade(conn, dept_id, tipo_maquina_id):
    """Cria um tipo de atividade"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_atividade (
                nome_tipo, descricao, categoria, ativo, data_criacao, 
                data_ultima_atualizacao, id_tipo_maquina, id_departamento,
                departamento, setor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'EXECUCAO DE TESTE',
            'EXECUCAO DE TESTES FUNCIONAIS',
            'TESTE',
            True,
            datetime.now(),
            datetime.now(),
            tipo_maquina_id,
            dept_id,
            'TESTE',
            'TESTES'
        ))
        
        atividade_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Tipo de Atividade criado (ID: {atividade_id})")
        return atividade_id
        
    except Exception as e:
        print(f"❌ Erro ao criar tipo de atividade: {e}")
        conn.rollback()
        return None

def criar_descricao_atividade(conn, dept_id, tipo_maquina_id):
    """Cria uma descrição de atividade"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_descricao_atividade (
                codigo, descricao, categoria, ativo, data_criacao,
                data_ultima_atualizacao, setor, id_departamento,
                departamento, tipo_maquina
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'TEST001',
            'PREPARACAO E EXECUCAO DE TESTE BASICO',
            'TESTE',
            True,
            datetime.now(),
            datetime.now(),
            'TESTES',
            dept_id,
            'TESTE',
            tipo_maquina_id
        ))
        
        desc_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Descrição de Atividade criada (ID: {desc_id})")
        return desc_id
        
    except Exception as e:
        print(f"❌ Erro ao criar descrição de atividade: {e}")
        conn.rollback()
        return None

def criar_tipo_falha(conn, dept_id):
    """Cria um tipo de falha"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_falha (
                codigo, descricao, categoria, severidade, ativo,
                data_criacao, data_ultima_atualizacao, id_departamento,
                setor, departamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'FALHA001',
            'FALHA GENERICA DE TESTE',
            'TESTE',
            'MEDIA',
            True,
            datetime.now(),
            datetime.now(),
            dept_id,
            'TESTES',
            'TESTE'
        ))
        
        falha_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Tipo de Falha criado (ID: {falha_id})")
        return falha_id
        
    except Exception as e:
        print(f"❌ Erro ao criar tipo de falha: {e}")
        conn.rollback()
        return None

def criar_causa_retrabalho(conn, dept_id):
    """Cria uma causa de retrabalho"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO tipo_causas_retrabalho (
                codigo, descricao, ativo, data_criacao, data_ultima_atualizacao,
                id_departamento, departamento, setor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'RETR001',
            'ERRO NA PREPARACAO DO TESTE',
            True,
            datetime.now(),
            datetime.now(),
            dept_id,
            'TESTE',
            'TESTES'
        ))
        
        retr_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Causa de Retrabalho criada (ID: {retr_id})")
        return retr_id
        
    except Exception as e:
        print(f"❌ Erro ao criar causa de retrabalho: {e}")
        conn.rollback()
        return None

def main():
    """Função principal"""
    print("🚀 INICIANDO CRIAÇÃO DO DEPARTAMENTO TESTE COMPLETO")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return False
    
    try:
        # 1. Verificar/Criar departamento TESTE
        dept_id = verificar_departamento_teste(conn)
        if not dept_id:
            dept_id = criar_departamento_teste(conn)
            if not dept_id:
                return False
        
        # 2. Verificar/Criar setor TESTES
        setor_id = verificar_setor_testes(conn, dept_id)
        if not setor_id:
            setor_id = criar_setor_testes(conn, dept_id)
            if not setor_id:
                return False
        
        # 3. Criar tipo de máquina
        tipo_maquina_id = criar_tipo_maquina_teste(conn, dept_id)
        if not tipo_maquina_id:
            return False
        
        # 4. Criar tipo de teste
        tipo_teste_id = criar_tipo_teste(conn, dept_id, tipo_maquina_id)
        if not tipo_teste_id:
            return False
        
        # 5. Criar tipo de atividade
        atividade_id = criar_tipo_atividade(conn, dept_id, tipo_maquina_id)
        if not atividade_id:
            return False
        
        # 6. Criar descrição de atividade
        desc_id = criar_descricao_atividade(conn, dept_id, tipo_maquina_id)
        if not desc_id:
            return False
        
        # 7. Criar tipo de falha
        falha_id = criar_tipo_falha(conn, dept_id)
        if not falha_id:
            return False
        
        # 8. Criar causa de retrabalho
        retr_id = criar_causa_retrabalho(conn, dept_id)
        if not retr_id:
            return False
        
        print("=" * 60)
        print("✅ DEPARTAMENTO TESTE CRIADO COM SUCESSO!")
        print(f"📊 Departamento ID: {dept_id}")
        print(f"🏭 Setor ID: {setor_id}")
        print(f"🔧 Tipo Máquina ID: {tipo_maquina_id}")
        print(f"🧪 Tipo Teste ID: {tipo_teste_id}")
        print(f"📋 Atividade ID: {atividade_id}")
        print(f"📄 Descrição ID: {desc_id}")
        print(f"⚠️ Falha ID: {falha_id}")
        print(f"🔄 Retrabalho ID: {retr_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SCRIPT EXECUTADO COM SUCESSO!")
    else:
        print("\n💥 SCRIPT FALHOU!")
        sys.exit(1)
