#!/usr/bin/env python3
"""
Migração para adicionar campos de setor/departamento e popular campos de auditoria na tabela pendências
"""

import sqlite3
from datetime import datetime

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def executar_migracao():
    """Executar migração completa da tabela pendências"""
    
    print("🔧 MIGRAÇÃO DA TABELA PENDÊNCIAS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. ADICIONAR NOVOS CAMPOS DE SETOR E DEPARTAMENTO
        print("\n1. 📋 Adicionando campos de setor e departamento...")
        
        try:
            cursor.execute("ALTER TABLE pendencias ADD COLUMN setor_origem VARCHAR(100)")
            print("   ✅ Campo 'setor_origem' adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️ Campo 'setor_origem' já existe")
            else:
                raise e
        
        try:
            cursor.execute("ALTER TABLE pendencias ADD COLUMN departamento_origem VARCHAR(100)")
            print("   ✅ Campo 'departamento_origem' adicionado")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️ Campo 'departamento_origem' já existe")
            else:
                raise e
        
        # 2. POPULAR CAMPOS DE SETOR E DEPARTAMENTO
        print("\n2. 🏢 Populando campos de setor e departamento...")
        
        # Query para buscar pendências e dados dos usuários responsáveis
        query_populate = """
            UPDATE pendencias 
            SET setor_origem = (
                SELECT s.nome 
                FROM tipo_usuarios u 
                JOIN tipo_setores s ON u.id_setor = s.id 
                WHERE u.id = pendencias.id_responsavel_inicio
            ),
            departamento_origem = (
                SELECT d.nome_tipo 
                FROM tipo_usuarios u 
                JOIN tipo_departamentos d ON u.id_departamento = d.id 
                WHERE u.id = pendencias.id_responsavel_inicio
            )
            WHERE setor_origem IS NULL OR departamento_origem IS NULL
        """
        
        cursor.execute(query_populate)
        rows_updated = cursor.rowcount
        print(f"   ✅ {rows_updated} registros atualizados com setor/departamento")
        
        # 3. POPULAR CAMPOS DE AUDITORIA VAZIOS
        print("\n3. 📅 Populando campos de auditoria vazios...")
        
        # Popular data_criacao com data_inicio onde estiver NULL
        cursor.execute("""
            UPDATE pendencias 
            SET data_criacao = data_inicio 
            WHERE data_criacao IS NULL
        """)
        criacao_updated = cursor.rowcount
        print(f"   ✅ {criacao_updated} registros atualizados com data_criacao")
        
        # Popular data_ultima_atualizacao
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE pendencias 
            SET data_ultima_atualizacao = ? 
            WHERE data_ultima_atualizacao IS NULL
        """, (now,))
        atualizacao_updated = cursor.rowcount
        print(f"   ✅ {atualizacao_updated} registros atualizados com data_ultima_atualizacao")
        
        # 4. CALCULAR E POPULAR TEMPO_ABERTO_HORAS
        print("\n4. ⏱️ Calculando tempo em aberto...")
        
        # Para pendências fechadas
        cursor.execute("""
            UPDATE pendencias 
            SET tempo_aberto_horas = (
                CASE 
                    WHEN data_fechamento IS NOT NULL THEN
                        (julianday(data_fechamento) - julianday(data_inicio)) * 24
                    ELSE
                        (julianday('now') - julianday(data_inicio)) * 24
                END
            )
            WHERE tempo_aberto_horas IS NULL
        """)
        tempo_updated = cursor.rowcount
        print(f"   ✅ {tempo_updated} registros atualizados com tempo_aberto_horas")
        
        # 5. VERIFICAR RESULTADOS
        print("\n5. 📊 Verificando resultados da migração...")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(setor_origem) as com_setor,
                COUNT(departamento_origem) as com_departamento,
                COUNT(data_criacao) as com_data_criacao,
                COUNT(data_ultima_atualizacao) as com_data_atualizacao,
                COUNT(tempo_aberto_horas) as com_tempo_calculado
            FROM pendencias
        """)
        
        stats = cursor.fetchone()
        print(f"   📋 Total de pendências: {stats[0]}")
        print(f"   🏢 Com setor_origem: {stats[1]}")
        print(f"   🏭 Com departamento_origem: {stats[2]}")
        print(f"   📅 Com data_criacao: {stats[3]}")
        print(f"   🔄 Com data_ultima_atualizacao: {stats[4]}")
        print(f"   ⏱️ Com tempo_aberto_horas: {stats[5]}")
        
        # 6. MOSTRAR EXEMPLO DE DADOS
        print("\n6. 📋 Exemplo de dados após migração:")
        cursor.execute("""
            SELECT id, numero_os, status, setor_origem, departamento_origem, 
                   data_criacao, tempo_aberto_horas
            FROM pendencias 
            LIMIT 3
        """)
        
        examples = cursor.fetchall()
        for ex in examples:
            print(f"   ID: {ex[0]} | OS: {ex[1]} | Status: {ex[2]}")
            print(f"      Setor: {ex[3]} | Dept: {ex[4]}")
            print(f"      Criação: {ex[5]} | Tempo: {ex[6]:.1f}h")
            print()
        
        # Commit das mudanças
        conn.commit()
        conn.close()
        
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    executar_migracao()
