#!/usr/bin/env python3
"""
DEBUG PROGRAMAÇÕES CRIADAS
==========================

Verificar por que as programações criadas não têm id_ordem_servico.
"""

import sqlite3

def debug_programacoes():
    """Debug das programações criadas"""
    print("🔍 Debugando programações criadas...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar programações do usuário ID 8
        cursor.execute("""
            SELECT id, id_ordem_servico, responsavel_id, status, observacoes, created_at
            FROM programacoes 
            WHERE responsavel_id = 8
            ORDER BY id DESC
        """)
        programacoes = cursor.fetchall()
        
        print(f"📋 Programações do usuário ID 8:")
        for prog in programacoes:
            print(f"   ID {prog[0]}: OS={prog[1]}, Responsável={prog[2]}, Status={prog[3]}")
            print(f"      Observações: {prog[4][:50]}...")
            print(f"      Criado em: {prog[5]}")
            print()
        
        # Verificar todas as programações recentes
        cursor.execute("""
            SELECT id, id_ordem_servico, responsavel_id, status, observacoes, created_at
            FROM programacoes 
            ORDER BY id DESC
            LIMIT 10
        """)
        todas_programacoes = cursor.fetchall()
        
        print(f"📋 Últimas 10 programações criadas:")
        for prog in todas_programacoes:
            print(f"   ID {prog[0]}: OS={prog[1]}, Responsável={prog[2]}, Status={prog[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔧 DEBUG PROGRAMAÇÕES CRIADAS")
    print("=" * 35)
    
    debug_programacoes()

if __name__ == "__main__":
    main()
