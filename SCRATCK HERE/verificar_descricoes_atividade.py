#!/usr/bin/env python3
"""
Script para verificar a tabela tipo_descricao_atividade
"""

import sqlite3

def verificar_tabela():
    """Verifica a estrutura e dados da tabela tipo_descricao_atividade"""
    
    print("🔍 VERIFICANDO TABELA tipo_descricao_atividade")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tipo_descricao_atividade'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("❌ TABELA tipo_descricao_atividade NÃO EXISTE!")
            
            # Verificar tabelas similares
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%descricao%'")
            tabelas_similares = cursor.fetchall()
            
            print("🔍 TABELAS SIMILARES ENCONTRADAS:")
            for tabela in tabelas_similares:
                print(f"   - {tabela[0]}")
            
            return
        
        # Verificar estrutura da tabela
        print("📋 ESTRUTURA DA TABELA:")
        cursor.execute("PRAGMA table_info(tipo_descricao_atividade)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - PK: {col[5]} - NotNull: {col[3]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM tipo_descricao_atividade")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        # Contar registros ativos
        cursor.execute("SELECT COUNT(*) FROM tipo_descricao_atividade WHERE ativo = 1")
        ativos = cursor.fetchone()[0]
        print(f"📊 REGISTROS ATIVOS: {ativos}")
        
        # Mostrar alguns registros
        print(f"\n📄 PRIMEIROS 10 REGISTROS:")
        cursor.execute("SELECT * FROM tipo_descricao_atividade LIMIT 10")
        registros = cursor.fetchall()
        
        for i, reg in enumerate(registros, 1):
            print(f"   {i}. ID: {reg[0]}")
            if len(reg) > 1:
                print(f"      nome: {reg[1] if len(reg) > 1 else 'N/A'}")
            if len(reg) > 2:
                print(f"      descricao: {reg[2] if len(reg) > 2 else 'N/A'}")
            if len(reg) > 3:
                print(f"      ativo: {reg[3] if len(reg) > 3 else 'N/A'}")
            print()
        
        # Testar consulta específica
        print(f"🧪 TESTANDO CONSULTA ESPECÍFICA:")
        try:
            cursor.execute("SELECT id, nome, descricao FROM tipo_descricao_atividade WHERE ativo = 1 ORDER BY nome")
            resultados = cursor.fetchall()
            print(f"   ✅ Consulta executada com sucesso!")
            print(f"   📊 Resultados encontrados: {len(resultados)}")
            
            if resultados:
                print(f"   📄 Primeiros 5 resultados:")
                for i, res in enumerate(resultados[:5], 1):
                    print(f"      {i}. ID: {res[0]}, Nome: {res[1]}, Desc: {res[2]}")
            else:
                print(f"   ⚠️ Nenhum resultado encontrado!")
                
        except Exception as e:
            print(f"   ❌ Erro na consulta: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    verificar_tabela()
