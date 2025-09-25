#!/usr/bin/env python3
"""
Script para verificar a estrutura e dados da tabela tipos_maquina
"""

import sqlite3
import json

def verificar_tabela():
    """Verifica a estrutura e dados da tabela tipos_maquina"""
    
    print("🔍 VERIFICANDO TABELA tipos_maquina")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        print("📋 ESTRUTURA DA TABELA:")
        cursor.execute("PRAGMA table_info(tipos_maquina)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - PK: {col[5]} - NotNull: {col[3]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        # Contar registros ativos
        cursor.execute("SELECT COUNT(*) FROM tipos_maquina WHERE ativo = 1")
        ativos = cursor.fetchone()[0]
        print(f"📊 REGISTROS ATIVOS: {ativos}")
        
        # Mostrar alguns registros
        print(f"\n📄 PRIMEIROS 5 REGISTROS:")
        cursor.execute("SELECT * FROM tipos_maquina LIMIT 5")
        registros = cursor.fetchall()
        
        for i, reg in enumerate(registros, 1):
            print(f"   {i}. ID: {reg[0]}")
            if len(reg) > 1:
                print(f"      nome_tipo: {reg[1] if len(reg) > 1 else 'N/A'}")
            if len(reg) > 2:
                print(f"      categoria: {reg[2] if len(reg) > 2 else 'N/A'}")
            if len(reg) > 3:
                print(f"      descricao: {reg[3] if len(reg) > 3 else 'N/A'}")
            if len(reg) > 4:
                print(f"      ativo: {reg[4] if len(reg) > 4 else 'N/A'}")
            print()
        
        # Testar consulta específica
        print(f"🧪 TESTANDO CONSULTA ESPECÍFICA:")
        try:
            cursor.execute("SELECT id, nome_tipo, descricao FROM tipos_maquina WHERE ativo = 1 ORDER BY nome_tipo")
            resultados = cursor.fetchall()
            print(f"   ✅ Consulta executada com sucesso!")
            print(f"   📊 Resultados encontrados: {len(resultados)}")
            
            if resultados:
                print(f"   📄 Primeiros 3 resultados:")
                for i, res in enumerate(resultados[:3], 1):
                    print(f"      {i}. ID: {res[0]}, Nome: {res[1]}, Desc: {res[2]}")
            else:
                print(f"   ⚠️ Nenhum resultado encontrado!")
                
        except Exception as e:
            print(f"   ❌ Erro na consulta: {e}")
        
        # Verificar se há registros com ativo = 1
        print(f"\n🔍 VERIFICANDO REGISTROS ATIVOS:")
        cursor.execute("SELECT id, nome_tipo, ativo FROM tipos_maquina")
        todos_registros = cursor.fetchall()
        
        ativos_encontrados = [r for r in todos_registros if r[2] == 1]
        inativos_encontrados = [r for r in todos_registros if r[2] != 1]
        
        print(f"   ✅ Registros com ativo = 1: {len(ativos_encontrados)}")
        print(f"   ❌ Registros com ativo != 1: {len(inativos_encontrados)}")
        
        if ativos_encontrados:
            print(f"   📄 Registros ativos:")
            for reg in ativos_encontrados[:5]:
                print(f"      ID: {reg[0]}, Nome: {reg[1]}, Ativo: {reg[2]}")
        
        if inativos_encontrados:
            print(f"   📄 Registros inativos (primeiros 5):")
            for reg in inativos_encontrados[:5]:
                print(f"      ID: {reg[0]}, Nome: {reg[1]}, Ativo: {reg[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    verificar_tabela()
