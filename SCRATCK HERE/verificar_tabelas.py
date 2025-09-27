#!/usr/bin/env python3
"""
Verificar tabelas do banco
"""

import sqlite3
import os

def main():
    print("🔍 VERIFICANDO TABELAS DO BANCO")
    print("=" * 60)
    
    # Conectar ao banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Listar todas as tabelas
        print("1. 📋 Todas as tabelas:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tabelas = cursor.fetchall()
        
        for i, (tabela,) in enumerate(tabelas, 1):
            print(f"   {i:2d}. {tabela}")
        
        # 2. Procurar tabelas relacionadas a setor
        print("\n2. 🔍 Tabelas relacionadas a 'setor':")
        setor_tables = [t[0] for t in tabelas if 'setor' in t[0].lower()]
        
        if setor_tables:
            for tabela in setor_tables:
                print(f"   ✅ {tabela}")
                
                # Mostrar estrutura
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = cursor.fetchall()
                print(f"      Colunas: {[col[1] for col in colunas]}")
                
                # Mostrar alguns dados
                cursor.execute(f"SELECT * FROM {tabela} LIMIT 3")
                dados = cursor.fetchall()
                print(f"      Registros: {len(dados)}")
                for dado in dados:
                    print(f"         {dado}")
        else:
            print("   ❌ Nenhuma tabela com 'setor' encontrada")
        
        # 3. Verificar estrutura da tabela tipo_usuarios
        print("\n3. 👤 Estrutura da tabela tipo_usuarios:")
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        colunas = cursor.fetchall()
        
        for col in colunas:
            print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # 4. Verificar dados de usuários
        print("\n4. 👥 Usuários com id_setor:")
        cursor.execute("""
            SELECT id, nome_completo, id_setor, ativo, privilege_level
            FROM tipo_usuarios 
            WHERE id_setor IS NOT NULL
            ORDER BY id_setor, nome_completo
        """)
        
        usuarios = cursor.fetchall()
        print(f"   📊 Total: {len(usuarios)} usuários com setor")
        
        setores_unicos = set()
        for user in usuarios:
            setores_unicos.add(user[2])
            print(f"      ID: {user[0]} | Nome: {user[1]} | Setor: {user[2]} | Ativo: {user[3]} | Nível: {user[4]}")
        
        print(f"\n   🏢 Setores únicos encontrados: {sorted(setores_unicos)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
