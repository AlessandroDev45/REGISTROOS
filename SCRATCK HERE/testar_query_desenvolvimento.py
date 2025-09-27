#!/usr/bin/env python3
"""
Testar a query do desenvolvimento diretamente no banco
"""

import sqlite3
import os

def main():
    print("🔍 TESTANDO QUERY DO DESENVOLVIMENTO")
    print("=" * 60)
    
    # Caminho do banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Parâmetros do usuário admin
        user_id = 1
        setor_id = 42
        
        print(f"👤 Usuário: {user_id}")
        print(f"🏢 Setor: {setor_id}")
        
        # 1. Testar query simples
        print(f"\n1. 📊 Query simples - todas as programações:")
        cursor.execute("SELECT p.id, p.responsavel_id, p.id_setor, os.os_numero FROM programacoes p LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id")
        resultados = cursor.fetchall()
        
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | Responsável: {resultado[1]} | Setor: {resultado[2]} | OS: {resultado[3]}")
        
        # 2. Testar filtro por setor
        print(f"\n2. 🔍 Filtro por setor ({setor_id}):")
        cursor.execute("SELECT id, responsavel_id, id_setor FROM programacoes WHERE id_setor = ?", (setor_id,))
        resultados = cursor.fetchall()
        
        print(f"   Encontradas: {len(resultados)} programações")
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | Responsável: {resultado[1]} | Setor: {resultado[2]}")
        
        # 3. Testar filtro por responsável
        print(f"\n3. 👤 Filtro por responsável ({user_id}):")
        cursor.execute("SELECT id, responsavel_id, id_setor FROM programacoes WHERE responsavel_id = ?", (user_id,))
        resultados = cursor.fetchall()
        
        print(f"   Encontradas: {len(resultados)} programações")
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | Responsável: {resultado[1]} | Setor: {resultado[2]}")
        
        # 4. Testar filtro combinado (OR)
        print(f"\n4. 🔗 Filtro combinado (setor {setor_id} OR responsável {user_id}):")
        cursor.execute("SELECT id, responsavel_id, id_setor FROM programacoes WHERE id_setor = ? OR responsavel_id = ?", (setor_id, user_id))
        resultados = cursor.fetchall()
        
        print(f"   Encontradas: {len(resultados)} programações")
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | Responsável: {resultado[1]} | Setor: {resultado[2]}")
        
        # 5. Testar query completa do desenvolvimento
        print(f"\n5. 🔧 Query completa do desenvolvimento:")
        query = """
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor,
                   os.os_numero, os.status_os, os.prioridade, u.nome_completo as responsavel_nome,
                   c.razao_social as cliente_nome, c.cnpj as cliente_cnpj,
                   e.descricao as equipamento_descricao, e.numero_serie as equipamento_serie
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            WHERE (p.id_setor = ? OR p.responsavel_id = ?)
            ORDER BY p.inicio_previsto DESC
            LIMIT 50
        """
        
        cursor.execute(query, (setor_id, user_id))
        resultados = cursor.fetchall()
        
        print(f"   Encontradas: {len(resultados)} programações")
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | OS: {resultado[11]} | Responsável: {resultado[14]} | Setor: {resultado[10]}")
        
        # 6. Verificar se há problema com NULL
        print(f"\n6. ❓ Verificando valores NULL:")
        cursor.execute("SELECT id, id_setor, responsavel_id FROM programacoes WHERE id_setor IS NULL OR responsavel_id IS NULL")
        resultados = cursor.fetchall()
        
        print(f"   Programações com NULL: {len(resultados)}")
        for resultado in resultados:
            print(f"   ID: {resultado[0]} | Setor: {resultado[1]} | Responsável: {resultado[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
