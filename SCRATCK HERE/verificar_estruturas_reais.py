#!/usr/bin/env python3
"""
Verificar estruturas reais das tabelas
"""

import sqlite3
import os

def verificar_estruturas():
    """Verifica estruturas reais das tabelas"""
    db_path = "RegistroOS/registrooficial/backend/app/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 ESTRUTURAS REAIS DAS TABELAS")
        print("=" * 60)
        
        tabelas_importantes = [
            'tipo_departamentos',
            'tipo_setores', 
            'tipo_usuarios',
            'tipo_atividade',
            'tipo_descricao_atividade',
            'tipos_maquina',
            'clientes',
            'equipamentos',
            'ordens_servico',
            'apontamentos_detalhados',
            'pendencias',
            'programacoes'
        ]
        
        for tabela in tabelas_importantes:
            try:
                print(f"\n📋 {tabela.upper()}:")
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = cursor.fetchall()
                
                for coluna in colunas:
                    print(f"   - {coluna[1]} ({coluna[2]})")
                
                # Mostrar alguns dados de exemplo
                cursor.execute(f"SELECT * FROM {tabela} LIMIT 2")
                dados = cursor.fetchall()
                if dados:
                    print(f"   Exemplo: {dados[0]}")
                    
            except Exception as e:
                print(f"❌ {tabela}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estruturas()
