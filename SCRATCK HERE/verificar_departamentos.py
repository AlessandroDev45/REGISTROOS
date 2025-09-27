#!/usr/bin/env python3
"""
VERIFICAR DEPARTAMENTOS
======================

Verificar departamentos disponíveis para usar na atribuição.
"""

import sqlite3

def verificar_departamentos():
    """Verificar departamentos e setores"""
    print("🔍 Verificando departamentos e setores...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela tipo_setores
        cursor.execute("PRAGMA table_info(tipo_setores)")
        colunas = cursor.fetchall()
        
        print(f"📋 Estrutura da tabela tipo_setores:")
        for col in colunas:
            print(f"   {col[1]} ({col[2]})")
        
        # Verificar setores com departamentos
        cursor.execute("SELECT id, nome, departamento FROM tipo_setores WHERE nome LIKE '%MECANICA%' ORDER BY nome")
        setores_mecanica = cursor.fetchall()
        
        print(f"\n📋 Setores MECANICA encontrados:")
        for setor in setores_mecanica:
            print(f"   ID {setor[0]}: {setor[1]} - Departamento: {setor[2]}")
        
        # Verificar todos os departamentos únicos
        cursor.execute("SELECT DISTINCT departamento FROM tipo_setores WHERE departamento IS NOT NULL ORDER BY departamento")
        departamentos = cursor.fetchall()
        
        print(f"\n📋 Departamentos únicos encontrados:")
        for dept in departamentos:
            print(f"   {dept[0]}")
        
        # Verificar combinação específica
        cursor.execute("SELECT id, nome, departamento FROM tipo_setores WHERE nome = 'MECANICA DIA'")
        mecanica_dia = cursor.fetchall()
        
        print(f"\n📋 Setor MECANICA DIA específico:")
        for setor in mecanica_dia:
            print(f"   ID {setor[0]}: {setor[1]} - Departamento: {setor[2]}")
        
        conn.close()
        return departamentos
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 VERIFICAR DEPARTAMENTOS")
    print("=" * 30)
    
    departamentos = verificar_departamentos()
    
    print(f"\n💡 RECOMENDAÇÃO:")
    print(f"   Use a combinação exata de setor + departamento")
    print(f"   Exemplo: setor='MECANICA DIA' + departamento correto")

if __name__ == "__main__":
    main()
