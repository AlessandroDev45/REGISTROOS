"""
Script para adicionar a coluna tipo_maquina à tabela tipo_descricao_atividade
"""

import sqlite3
import os
from datetime import datetime

def adicionar_coluna_tipo_maquina():
    """Adiciona a coluna tipo_maquina à tabela tipo_descricao_atividade"""

    print("🔧 ADICIONANDO COLUNA tipo_maquina À TABELA tipo_descricao_atividade")
    print("=" * 60)

    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "RegistroOS", "registrooficial", "backend", "registroos_new.db")

    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False

    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(tipo_descricao_atividade)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'tipo_maquina' in column_names:
            print("✅ Coluna tipo_maquina já existe na tabela tipo_descricao_atividade")
            conn.close()
            return True

        # Adicionar a coluna tipo_maquina
        print("📝 Adicionando coluna tipo_maquina...")
        cursor.execute("ALTER TABLE tipo_descricao_atividade ADD COLUMN tipo_maquina VARCHAR(255)")

        # Commit das mudanças
        conn.commit()

        # Verificar se foi adicionada com sucesso
        cursor.execute("PRAGMA table_info(tipo_descricao_atividade)")
        columns_after = cursor.fetchall()
        column_names_after = [col[1] for col in columns_after]

        if 'tipo_maquina' in column_names_after:
            print("✅ Coluna tipo_maquina adicionada com sucesso!")
            print(f"📊 Total de colunas agora: {len(column_names_after)}")

            # Log da migração
            cursor.execute("""
                INSERT INTO migration_log (fase, acao, tabela_afetada, registros_afetados, data_execucao, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'ALTER_TABLE',
                'ADD_COLUMN',
                'tipo_descricao_atividade',
                0,
                datetime.now().isoformat(),
                'Adicionada coluna tipo_maquina VARCHAR(255) para associar tipos de máquina às descrições de atividade'
            ))
            conn.commit()

            print("✅ Log de migração registrado")
        else:
            print("❌ Falha ao adicionar coluna tipo_maquina")
            conn.close()
            return False

        conn.close()
        print("🎉 Migração concluída com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    sucesso = adicionar_coluna_tipo_maquina()
    if sucesso:
        print("\n✅ MIGRACÃO CONCLUÍDA: Coluna tipo_maquina adicionada à tabela tipo_descricao_atividade")
    else:
        print("\n❌ MIGRAÇÃO FALHADA: Não foi possível adicionar a coluna tipo_maquina")