#!/usr/bin/env python3
"""
Script para verificar os valores da coluna ativo na tabela tipo_descricao_atividade
"""

import sqlite3

def verificar_coluna_ativo():
    """Verifica os valores da coluna ativo"""
    
    print("🔍 VERIFICANDO COLUNA ATIVO")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar valores únicos da coluna ativo
        cursor.execute("SELECT DISTINCT ativo FROM tipo_descricao_atividade")
        valores_ativo = cursor.fetchall()
        
        print("📊 VALORES ÚNICOS DA COLUNA ATIVO:")
        for valor in valores_ativo:
            print(f"   - '{valor[0]}'")
        
        # Contar registros por valor de ativo
        print("\n📊 CONTAGEM POR VALOR DE ATIVO:")
        for valor in valores_ativo:
            cursor.execute("SELECT COUNT(*) FROM tipo_descricao_atividade WHERE ativo = ?", (valor[0],))
            count = cursor.fetchone()[0]
            print(f"   - '{valor[0]}': {count} registros")
        
        # Testar consulta com ativo = 1
        print("\n🧪 TESTANDO CONSULTA COM ativo = 1:")
        cursor.execute("SELECT COUNT(*) FROM tipo_descricao_atividade WHERE ativo = 1")
        count_1 = cursor.fetchone()[0]
        print(f"   📊 Registros com ativo = 1: {count_1}")
        
        # Testar consulta com ativo = '1'
        print("\n🧪 TESTANDO CONSULTA COM ativo = '1':")
        cursor.execute("SELECT COUNT(*) FROM tipo_descricao_atividade WHERE ativo = '1'")
        count_str_1 = cursor.fetchone()[0]
        print(f"   📊 Registros com ativo = '1': {count_str_1}")
        
        # Testar consulta sem filtro de ativo
        print("\n🧪 TESTANDO CONSULTA SEM FILTRO DE ATIVO:")
        cursor.execute("SELECT id, codigo, descricao FROM tipo_descricao_atividade ORDER BY codigo LIMIT 5")
        resultados = cursor.fetchall()
        print(f"   📊 Primeiros 5 registros:")
        for i, res in enumerate(resultados, 1):
            print(f"      {i}. ID: {res[0]}, Código: {res[1]}, Desc: {res[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar coluna ativo: {e}")

if __name__ == "__main__":
    verificar_coluna_ativo()
