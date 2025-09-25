#!/usr/bin/env python3
"""
Script para verificar os tipos de máquina para o admin
"""

import sqlite3

def verificar_tipos_maquina():
    """Verifica os tipos de máquina"""
    
    print("🔍 VERIFICANDO TIPOS DE MÁQUINA PARA ADMIN")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela tipos_maquina
        print("📋 ESTRUTURA DA TABELA tipos_maquina:")
        cursor.execute("PRAGMA table_info(tipos_maquina)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - PK: {col[5]} - NotNull: {col[3]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        # Verificar valores únicos da coluna ativo
        cursor.execute("SELECT DISTINCT ativo FROM tipos_maquina")
        valores_ativo = cursor.fetchall()
        
        print("\n📊 VALORES ÚNICOS DA COLUNA ATIVO:")
        for valor in valores_ativo:
            print(f"   - '{valor[0]}' (tipo: {type(valor[0])})")
        
        # Contar registros por valor de ativo
        print("\n📊 CONTAGEM POR VALOR DE ATIVO:")
        for valor in valores_ativo:
            cursor.execute("SELECT COUNT(*) FROM tipos_maquina WHERE ativo = ?", (valor[0],))
            count = cursor.fetchone()[0]
            print(f"   - '{valor[0]}': {count} registros")
        
        # Testar diferentes consultas
        print("\n🧪 TESTANDO DIFERENTES CONSULTAS:")
        
        # Consulta 1: ativo = 1
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina WHERE ativo = 1")
        count_1 = cursor.fetchone()[0]
        print(f"   📊 ativo = 1: {count_1} registros")
        
        # Consulta 2: ativo = True
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina WHERE ativo = ?", (True,))
        count_true = cursor.fetchone()[0]
        print(f"   📊 ativo = True: {count_true} registros")
        
        # Consulta 3: ativo IS TRUE
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina WHERE ativo IS 1")
        count_is_1 = cursor.fetchone()[0]
        print(f"   📊 ativo IS 1: {count_is_1} registros")
        
        # Mostrar alguns registros
        print(f"\n📄 PRIMEIROS 5 REGISTROS:")
        cursor.execute("SELECT id, nome_tipo, categoria, ativo FROM tipos_maquina LIMIT 5")
        registros = cursor.fetchall()
        
        for i, reg in enumerate(registros, 1):
            print(f"   {i}. ID: {reg[0]}, Nome: {reg[1]}, Categoria: {reg[2]}, Ativo: {reg[3]} (tipo: {type(reg[3])})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tipos de máquina: {e}")

if __name__ == "__main__":
    verificar_tipos_maquina()
