#!/usr/bin/env python3
"""
VERIFICAR SETORES EXISTENTES
===========================

Verificar quais setores existem no banco para usar na atribuição.
"""

import sqlite3

def verificar_setores():
    """Verificar setores disponíveis"""
    print("🔍 Verificando setores disponíveis...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabela tipo_setores
        cursor.execute("SELECT id, nome FROM tipo_setores ORDER BY nome")
        setores = cursor.fetchall()
        
        print(f"📋 Setores encontrados na tabela tipo_setores:")
        for setor in setores:
            print(f"   ID {setor[0]}: {setor[1]}")
        
        # Verificar se há outros nomes de setores
        cursor.execute("SELECT DISTINCT id_setor FROM programacoes WHERE id_setor IS NOT NULL")
        setores_usados = cursor.fetchall()
        
        print(f"\n📋 IDs de setores usados em programações:")
        for setor_id in setores_usados:
            print(f"   Setor ID: {setor_id[0]}")
        
        # Verificar usuários do setor MECANICA
        cursor.execute("""
            SELECT id, nome_completo, email 
            FROM tipo_usuarios 
            WHERE email LIKE '%mecanica%' 
            ORDER BY privilege_level, id
        """)
        usuarios_mecanica = cursor.fetchall()
        
        print(f"\n👥 Usuários relacionados à MECANICA:")
        for user in usuarios_mecanica:
            print(f"   ID {user[0]}: {user[1]} ({user[2]})")
        
        conn.close()
        return setores
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 VERIFICAR SETORES EXISTENTES")
    print("=" * 35)
    
    setores = verificar_setores()
    
    if setores:
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"   Use um dos setores listados acima na atribuição")
        print(f"   Exemplo: se existe 'MECANICA', use exatamente esse nome")
    else:
        print(f"\n⚠️ Nenhum setor encontrado")
        print(f"   Pode ser necessário criar setores primeiro")

if __name__ == "__main__":
    main()
