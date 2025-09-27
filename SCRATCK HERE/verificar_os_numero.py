#!/usr/bin/env python3
"""
VERIFICAR OS NÚMERO
==================

Verificar se a OS tem número no banco.
"""

import sqlite3

def verificar_os():
    """Verificar dados da OS"""
    print("🔍 Verificando dados da OS...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar OS ID 1
        cursor.execute("SELECT id, os_numero, status_os, prioridade FROM ordens_servico WHERE id = 1")
        os_data = cursor.fetchone()
        
        if os_data:
            print(f"📋 OS ID 1 encontrada:")
            print(f"   ID: {os_data[0]}")
            print(f"   Número: {os_data[1]}")
            print(f"   Status: {os_data[2]}")
            print(f"   Prioridade: {os_data[3]}")
        else:
            print(f"❌ OS ID 1 não encontrada")
        
        # Verificar programações que usam OS ID 1
        cursor.execute("SELECT id, id_ordem_servico, responsavel_id FROM programacoes WHERE id_ordem_servico = 1")
        programacoes = cursor.fetchall()
        
        print(f"\n📋 Programações que usam OS ID 1:")
        for prog in programacoes:
            print(f"   Programação ID {prog[0]}: OS {prog[1]}, Responsável {prog[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔧 VERIFICAR OS NÚMERO")
    print("=" * 25)
    
    verificar_os()

if __name__ == "__main__":
    main()
