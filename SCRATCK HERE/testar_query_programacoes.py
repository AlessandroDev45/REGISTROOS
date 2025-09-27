#!/usr/bin/env python3
"""
TESTAR QUERY PROGRAMAÇÕES
========================

Testa a query SQL do endpoint de programações diretamente no banco.
"""

import sqlite3

def testar_query_programacoes():
    """Testar a query SQL diretamente"""
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Testando query SQL do endpoint...")
        
        # Query original do endpoint
        query = """
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor, p.historico,
                   os.os_numero, os.status_os, os.prioridade, u.nome_completo as responsavel_nome,
                   c.razao_social as cliente_nome, e.descricao as equipamento_descricao,
                   s.nome as setor_nome
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            WHERE p.responsavel_id = ?
            ORDER BY p.inicio_previsto DESC
            LIMIT 50
        """
        
        user_id = 1  # Admin
        
        print(f"📋 Executando query para user_id = {user_id}...")
        
        try:
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            print(f"✅ Query executada com sucesso!")
            print(f"📊 Resultados encontrados: {len(results)}")
            
            for i, row in enumerate(results):
                print(f"\n📋 Resultado {i+1}:")
                print(f"   ID: {row[0]}")
                print(f"   OS ID: {row[1]}")
                print(f"   Responsável ID: {row[2]}")
                print(f"   Status: {row[5]}")
                print(f"   OS Número: {row[12]}")
                print(f"   Responsável Nome: {row[15]}")
                
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            
            # Testar query simplificada
            print(f"\n🔧 Testando query simplificada...")
            
            query_simples = """
                SELECT p.id, p.responsavel_id, p.status, p.observacoes
                FROM programacoes p
                WHERE p.responsavel_id = ?
            """
            
            try:
                cursor.execute(query_simples, (user_id,))
                results_simples = cursor.fetchall()
                
                print(f"✅ Query simplificada executada!")
                print(f"📊 Resultados: {len(results_simples)}")
                
                for row in results_simples:
                    print(f"   ID {row[0]}: responsável={row[1]}, status={row[2]}")
                    
            except Exception as e2:
                print(f"❌ Erro na query simplificada: {e2}")
        
        # Verificar se as tabelas relacionadas existem
        print(f"\n🔍 Verificando tabelas relacionadas...")
        
        tabelas_para_verificar = [
            "ordens_servico",
            "tipo_usuarios", 
            "clientes",
            "equipamentos",
            "tipo_setores"
        ]
        
        for tabela in tabelas_para_verificar:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {tabela}: {count} registros")
            except Exception as e:
                print(f"   ❌ {tabela}: ERRO - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def verificar_estrutura_tabelas():
    """Verificar estrutura das tabelas relacionadas"""
    
    db_path = "C:/Users/Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificando estrutura das tabelas...")
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print(f"📋 Tabelas no banco:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        # Verificar se as tabelas esperadas existem
        nomes_tabelas = [t[0] for t in tabelas]
        
        tabelas_esperadas = [
            "programacoes",
            "ordens_servico", 
            "tipo_usuarios",
            "clientes",
            "equipamentos",
            "tipo_setores"
        ]
        
        print(f"\n📊 Verificação de tabelas esperadas:")
        for tabela in tabelas_esperadas:
            if tabela in nomes_tabelas:
                print(f"   ✅ {tabela}")
            else:
                print(f"   ❌ {tabela} - NÃO ENCONTRADA")
                
                # Procurar tabelas similares
                similares = [t for t in nomes_tabelas if tabela.lower() in t.lower() or t.lower() in tabela.lower()]
                if similares:
                    print(f"      💡 Similares: {similares}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔧 TESTAR QUERY PROGRAMAÇÕES")
    print("=" * 40)
    
    # 1. Verificar estrutura das tabelas
    verificar_estrutura_tabelas()
    
    # 2. Testar query
    testar_query_programacoes()

if __name__ == "__main__":
    main()
