#!/usr/bin/env python3
"""
VERIFICAR CAMPO HISTÓRICO
========================

Verifica se o campo histórico foi adicionado corretamente
e se está sendo usado nos endpoints.
"""

import sqlite3
import os

def verificar_estrutura_tabela():
    """Verificar estrutura da tabela programacoes"""
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura da tabela programacoes...")
        
        # Verificar colunas
        cursor.execute("PRAGMA table_info(programacoes)")
        colunas = cursor.fetchall()
        
        print(f"📋 Colunas da tabela programacoes:")
        for col in colunas:
            print(f"   {col[1]} ({col[2]}) - {col[3]}")
        
        # Verificar se campo histórico existe
        tem_historico = any(col[1] == 'historico' for col in colunas)
        
        if tem_historico:
            print("✅ Campo 'historico' existe na tabela")
        else:
            print("❌ Campo 'historico' NÃO existe na tabela")
            return False
        
        # Verificar dados de algumas programações
        print("\n📋 Verificando dados das últimas programações...")
        
        cursor.execute("""
            SELECT id, observacoes, historico, status, created_at
            FROM programacoes 
            ORDER BY id DESC 
            LIMIT 3
        """)
        
        programacoes = cursor.fetchall()
        
        for prog in programacoes:
            print(f"\n📋 Programação ID {prog[0]}:")
            print(f"   Observações: {prog[1] or 'Vazio'}")
            print(f"   Histórico: {prog[2] or 'Vazio'}")
            print(f"   Status: {prog[3] or 'N/A'}")
            print(f"   Criado em: {prog[4] or 'N/A'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def atualizar_historico_programacoes():
    """Atualizar histórico das programações existentes"""
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Atualizando histórico das programações...")
        
        # Buscar programações sem histórico
        cursor.execute("""
            SELECT id, observacoes, status, created_at
            FROM programacoes 
            WHERE historico IS NULL OR historico = ''
        """)
        
        programacoes_sem_historico = cursor.fetchall()
        
        print(f"📋 Encontradas {len(programacoes_sem_historico)} programações sem histórico")
        
        for prog in programacoes_sem_historico:
            prog_id = prog[0]
            observacoes = prog[1] or ""
            status = prog[2] or "PROGRAMADA"
            created_at = prog[3] or "Data não informada"
            
            # Criar histórico baseado nos dados existentes
            historico = f"[CRIAÇÃO] Programação criada em {created_at}"
            
            if observacoes:
                historico += f"\n[OBSERVAÇÃO INICIAL] {observacoes}"
            
            if status != "PROGRAMADA":
                historico += f"\n[STATUS] Status atual: {status}"
            
            # Atualizar programação
            cursor.execute("""
                UPDATE programacoes 
                SET historico = ?
                WHERE id = ?
            """, (historico, prog_id))
            
            print(f"   ✅ Programação {prog_id} atualizada")
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(programacoes_sem_historico)} programações atualizadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar histórico: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 VERIFICAR CAMPO HISTÓRICO")
    print("=" * 40)
    
    # 1. Verificar estrutura
    estrutura_ok = verificar_estrutura_tabela()
    
    if estrutura_ok:
        # 2. Atualizar histórico se necessário
        atualizar_historico_programacoes()
        
        # 3. Verificar novamente
        print("\n" + "="*40)
        print("🔍 VERIFICAÇÃO FINAL")
        print("="*40)
        verificar_estrutura_tabela()
        
        print("\n🎉 VERIFICAÇÃO CONCLUÍDA!")
        print("💡 Agora reinicie o backend e teste novamente")
    else:
        print("\n❌ VERIFICAÇÃO FALHOU!")
        print("💡 Execute o script de migração novamente")

if __name__ == "__main__":
    main()
