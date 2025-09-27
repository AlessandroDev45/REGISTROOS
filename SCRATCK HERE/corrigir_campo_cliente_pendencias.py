#!/usr/bin/env python3
"""
Corrigir campo cliente na tabela pendências para usar o nome real do cliente da OS
"""

import sqlite3

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def corrigir_campo_cliente():
    """Corrigir campo cliente nas pendências"""
    
    print("🔧 CORREÇÃO DO CAMPO CLIENTE NAS PENDÊNCIAS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. VERIFICAR SITUAÇÃO ATUAL
        print("\n1. 📊 SITUAÇÃO ATUAL:")
        print("-" * 40)
        
        cursor.execute("""
            SELECT p.id, p.numero_os, p.cliente as cliente_pendencia,
                   c.nome_fantasia as cliente_real, c.id as cliente_id
            FROM pendencias p
            LEFT JOIN ordens_servico os ON p.numero_os = os.os_numero
            LEFT JOIN clientes c ON os.id_cliente = c.id
        """)
        
        pendencias_antes = cursor.fetchall()
        
        print("📋 Comparação ANTES da correção:")
        for row in pendencias_antes:
            print(f"   Pendência {row[0]} | OS: {row[1]}")
            print(f"      Cliente Atual: '{row[2]}'")
            print(f"      Cliente Real: '{row[3]}' (ID: {row[4]})")
            print(f"      Precisa Correção: {'Sim' if row[2] != row[3] else 'Não'}")
            print()
        
        # 2. EXECUTAR CORREÇÃO
        print("2. 🔄 EXECUTANDO CORREÇÃO:")
        print("-" * 40)
        
        # Query para atualizar o campo cliente
        update_query = """
            UPDATE pendencias 
            SET cliente = (
                SELECT c.nome_fantasia 
                FROM ordens_servico os 
                JOIN clientes c ON os.id_cliente = c.id 
                WHERE os.os_numero = pendencias.numero_os
            )
            WHERE EXISTS (
                SELECT 1 
                FROM ordens_servico os 
                JOIN clientes c ON os.id_cliente = c.id 
                WHERE os.os_numero = pendencias.numero_os
            )
        """
        
        print("📝 Executando query de atualização...")
        cursor.execute(update_query)
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros atualizados")
        
        # 3. VERIFICAR RESULTADO
        print("\n3. ✅ RESULTADO APÓS CORREÇÃO:")
        print("-" * 40)
        
        cursor.execute("""
            SELECT p.id, p.numero_os, p.cliente as cliente_corrigido,
                   c.nome_fantasia as cliente_real, c.id as cliente_id
            FROM pendencias p
            LEFT JOIN ordens_servico os ON p.numero_os = os.os_numero
            LEFT JOIN clientes c ON os.id_cliente = c.id
        """)
        
        pendencias_depois = cursor.fetchall()
        
        print("📋 Comparação DEPOIS da correção:")
        for row in pendencias_depois:
            match = "✅ Correto" if row[2] == row[3] else "❌ Ainda incorreto"
            print(f"   Pendência {row[0]} | OS: {row[1]}")
            print(f"      Cliente Corrigido: '{row[2]}'")
            print(f"      Cliente Real: '{row[3]}' (ID: {row[4]})")
            print(f"      Status: {match}")
            print()
        
        # 4. ESTATÍSTICAS DA CORREÇÃO
        print("4. 📊 ESTATÍSTICAS DA CORREÇÃO:")
        print("-" * 40)
        
        # Contar quantos foram corrigidos
        corretos = sum(1 for row in pendencias_depois if row[2] == row[3])
        total = len(pendencias_depois)
        
        print(f"📈 Resultados:")
        print(f"   Total de Pendências: {total}")
        print(f"   Clientes Corretos: {corretos}")
        print(f"   Taxa de Sucesso: {(corretos/total*100):.1f}%")
        
        # 5. VERIFICAR INTEGRIDADE GERAL
        print("\n5. 🔍 VERIFICAÇÃO DE INTEGRIDADE:")
        print("-" * 40)
        
        # Verificar se todas as pendências têm cliente válido
        cursor.execute("""
            SELECT COUNT(*) as total_pendencias,
                   COUNT(CASE WHEN p.cliente IS NOT NULL AND p.cliente != '' THEN 1 END) as com_cliente_valido
            FROM pendencias p
        """)
        
        integridade = cursor.fetchone()
        print(f"📊 Integridade dos Clientes:")
        print(f"   Total de Pendências: {integridade[0]}")
        print(f"   Com Cliente Válido: {integridade[1]}")
        print(f"   Integridade: {(integridade[1]/integridade[0]*100):.1f}%")
        
        # Verificar se há pendências órfãs (sem OS válida)
        cursor.execute("""
            SELECT COUNT(*) as pendencias_orfas
            FROM pendencias p
            LEFT JOIN ordens_servico os ON p.numero_os = os.os_numero
            WHERE os.id IS NULL
        """)
        
        orfas = cursor.fetchone()[0]
        if orfas > 0:
            print(f"⚠️ Pendências órfãs (sem OS válida): {orfas}")
        else:
            print("✅ Todas as pendências têm OS válida")
        
        # 6. CRIAR TRIGGER PARA MANTER CONSISTÊNCIA
        print("\n6. 🔧 CRIANDO TRIGGER PARA CONSISTÊNCIA AUTOMÁTICA:")
        print("-" * 40)
        
        # Trigger para atualizar cliente automaticamente quando pendência for criada
        trigger_sql = """
            CREATE TRIGGER IF NOT EXISTS update_pendencia_cliente
            AFTER INSERT ON pendencias
            FOR EACH ROW
            BEGIN
                UPDATE pendencias 
                SET cliente = (
                    SELECT c.nome_fantasia 
                    FROM ordens_servico os 
                    JOIN clientes c ON os.id_cliente = c.id 
                    WHERE os.os_numero = NEW.numero_os
                )
                WHERE id = NEW.id;
            END;
        """
        
        cursor.execute(trigger_sql)
        print("✅ Trigger 'update_pendencia_cliente' criado")
        print("   → Novas pendências terão cliente populado automaticamente")
        
        # Commit das mudanças
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("🎯 Benefícios implementados:")
        print("   ✅ Campo cliente corrigido com dados reais")
        print("   ✅ Consistência entre pendências e OS")
        print("   ✅ Trigger automático para novas pendências")
        print("   ✅ Integridade referencial mantida")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    corrigir_campo_cliente()
