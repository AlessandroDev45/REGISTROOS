#!/usr/bin/env python3
"""
Debug da query de colaboradores
"""

import sqlite3
import os

def main():
    print("🔍 DEBUG: QUERY COLABORADORES")
    print("=" * 60)
    
    # Conectar ao banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar usuários do setor 42
        print("1. 👥 Usuários do setor 42:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.email, u.privilege_level, u.ativo,
                   s.nome as setor_nome, s.departamento
            FROM tipo_usuarios u
            LEFT JOIN setores s ON u.id_setor = s.id
            WHERE u.id_setor = 42
            ORDER BY u.nome_completo
        """)
        
        usuarios = cursor.fetchall()
        print(f"   📊 Total: {len(usuarios)} usuários")
        
        for user in usuarios:
            print(f"      ID: {user[0]} | Nome: {user[1]} | Ativo: {user[4]} | Nível: {user[3]} | Setor: {user[5]}")
        
        # 2. Verificar todos os usuários
        print("\n2. 👤 Todos os usuários:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.id_setor, u.ativo, u.privilege_level,
                   s.nome as setor_nome
            FROM tipo_usuarios u
            LEFT JOIN setores s ON u.id_setor = s.id
            ORDER BY u.id_setor, u.nome_completo
        """)
        
        todos_usuarios = cursor.fetchall()
        print(f"   📊 Total: {len(todos_usuarios)} usuários")
        
        setores_com_usuarios = {}
        for user in todos_usuarios:
            setor_id = user[2]
            if setor_id not in setores_com_usuarios:
                setores_com_usuarios[setor_id] = []
            setores_com_usuarios[setor_id].append(user)
        
        print(f"   🏢 Setores com usuários: {list(setores_com_usuarios.keys())}")
        
        for setor_id, users in setores_com_usuarios.items():
            if setor_id:
                print(f"\n   🏢 Setor {setor_id}: {len(users)} usuários")
                for user in users[:3]:  # Primeiros 3
                    print(f"      - {user[1]} (Ativo: {user[3]}, Nível: {user[4]})")
        
        # 3. Verificar setores
        print("\n3. 🏢 Setores disponíveis:")
        cursor.execute("SELECT id, nome, departamento FROM setores ORDER BY id")
        setores = cursor.fetchall()
        
        for setor in setores:
            print(f"   ID: {setor[0]} | Nome: {setor[1]} | Departamento: {setor[2]}")
        
        # 4. Testar query específica
        print("\n4. 🔍 Query específica do endpoint:")
        cursor.execute("""
            SELECT u.id, u.nome_completo, u.email, u.privilege_level,
                   s.nome as setor_nome, s.departamento
            FROM tipo_usuarios u
            LEFT JOIN setores s ON u.id_setor = s.id
            WHERE u.id_setor = 42
            ORDER BY u.nome_completo
        """)
        
        resultado = cursor.fetchall()
        print(f"   📊 Resultado: {len(resultado)} registros")
        
        for row in resultado:
            print(f"      ID: {row[0]} | Nome: {row[1]} | Email: {row[2]} | Nível: {row[3]} | Setor: {row[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
