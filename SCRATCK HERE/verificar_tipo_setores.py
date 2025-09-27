#!/usr/bin/env python3
"""
Verificar tabela tipo_setores
"""

import sqlite3
import os

def main():
    print("🔍 VERIFICANDO TABELA tipo_setores")
    print("=" * 60)
    
    # Conectar ao banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Estrutura da tabela tipo_setores
        print("1. 🏢 Estrutura da tabela tipo_setores:")
        cursor.execute("PRAGMA table_info(tipo_setores)")
        colunas = cursor.fetchall()
        
        for col in colunas:
            print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # 2. Todos os dados da tabela tipo_setores
        print("\n2. 📊 Todos os dados da tabela tipo_setores:")
        cursor.execute("SELECT * FROM tipo_setores ORDER BY id")
        setores = cursor.fetchall()
        
        print(f"   Total: {len(setores)} setores")
        for setor in setores:
            print(f"      {setor}")
        
        # 3. Verificar usuários e seus setores
        print("\n3. 👥 Usuários e seus setores:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.id_setor, u.setor, u.departamento, u.privilege_level
            FROM tipo_usuarios u
            ORDER BY u.id_setor, u.nome_completo
        """)
        
        usuarios = cursor.fetchall()
        print(f"   Total: {len(usuarios)} usuários")
        
        for user in usuarios:
            print(f"      ID: {user[0]} | Nome: {user[1]} | ID_Setor: {user[2]} | Setor: {user[3]} | Dept: {user[4]} | Nível: {user[5]}")
        
        # 4. JOIN entre usuários e setores
        print("\n4. 🔗 JOIN usuários x setores:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.id_setor, u.privilege_level,
                   s.nome as setor_nome, s.departamento as setor_departamento
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            ORDER BY u.id_setor, u.nome_completo
        """)
        
        resultado = cursor.fetchall()
        print(f"   Total: {len(resultado)} registros")
        
        for row in resultado:
            print(f"      ID: {row[0]} | Nome: {row[1]} | ID_Setor: {row[2]} | Nível: {row[3]} | Setor_Nome: {row[4]} | Setor_Dept: {row[5]}")
        
        # 5. Usuários do setor 42 especificamente
        print("\n5. 🎯 Usuários do setor 42:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.id_setor, u.privilege_level,
                   s.nome as setor_nome, s.departamento as setor_departamento
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            WHERE u.id_setor = 42
            ORDER BY u.nome_completo
        """)
        
        setor_42 = cursor.fetchall()
        print(f"   Total: {len(setor_42)} usuários no setor 42")
        
        for row in setor_42:
            print(f"      ID: {row[0]} | Nome: {row[1]} | Nível: {row[3]} | Setor: {row[4]} | Dept: {row[5]}")
        
        # 6. Verificar se existe setor com ID 42
        print("\n6. 🔍 Verificar setor ID 42:")
        cursor.execute("SELECT * FROM tipo_setores WHERE id = 42")
        setor_42_info = cursor.fetchone()
        
        if setor_42_info:
            print(f"   ✅ Setor 42 existe: {setor_42_info}")
        else:
            print(f"   ❌ Setor 42 NÃO existe!")
            
            # Mostrar setores disponíveis
            cursor.execute("SELECT id, nome, departamento FROM tipo_setores ORDER BY id")
            setores_disponiveis = cursor.fetchall()
            print(f"   📋 Setores disponíveis:")
            for s in setores_disponiveis:
                print(f"      ID: {s[0]} | Nome: {s[1]} | Departamento: {s[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
