#!/usr/bin/env python3
"""
Script de Limpeza de DADOS - RegistroOS
========================================

Este script:
1. Faz backup de todas as tabelas
2. LIMPA OS DADOS das tabelas que NÃO começam com 'tipo_' ou 'tipos_'
3. MANTÉM os dados das tabelas que começam com 'tipo_' ou 'tipos_'
4. Mantém as estruturas das tabelas, apenas remove os dados

REGRA: Se começar com "tipo" ou "tipos" → NÃO limpar dados
       Se NÃO começar com "tipo" ou "tipos" → LIMPAR dados
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Configurações
DB_PATH = "RegistroOS/registrooficial/backend/registroos_new.db"
BACKUP_DIR = "backup_limpeza_dados"
BACKUP_DB_PATH = f"{BACKUP_DIR}/backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

# Tabelas especiais do sistema que devem manter os dados
TABELAS_SISTEMA = {
    'sqlite_sequence',
    'sqlite_stat1', 
    'migration_log'
}

def criar_backup_completo():
    """Cria backup completo do banco antes da limpeza"""
    print("🔄 Criando backup completo do banco de dados...")
    
    # Criar diretório de backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Copiar banco completo
    shutil.copy2(DB_PATH, BACKUP_DB_PATH)
    print(f"✅ Backup criado: {BACKUP_DB_PATH}")

def listar_tabelas_para_limpar():
    """Lista tabelas que terão dados limpos vs mantidos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas_tabelas = [row[0] for row in cursor.fetchall()]
    
    # Filtrar tabelas
    tabelas_para_limpar = []  # NÃO começam com tipo/tipos
    tabelas_para_manter = []  # Começam com tipo/tipos
    
    for tabela in todas_tabelas:
        # Se começar com tipo_ ou tipos_ → MANTER dados
        if tabela.startswith('tipo_') or tabela.startswith('tipos_') or tabela in TABELAS_SISTEMA:
            tabelas_para_manter.append(tabela)
        else:
            # Se NÃO começar com tipo/tipos → LIMPAR dados
            tabelas_para_limpar.append(tabela)
    
    conn.close()
    
    return tabelas_para_limpar, tabelas_para_manter

def contar_registros_tabelas(tabelas):
    """Conta registros nas tabelas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    contadores = {}
    
    for tabela in tabelas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            contadores[tabela] = count
        except Exception as e:
            contadores[tabela] = f"Erro: {e}"
    
    conn.close()
    return contadores

def limpar_dados_tabelas(tabelas_para_limpar):
    """Limpa os dados das tabelas especificadas (mantém estrutura)"""
    if not tabelas_para_limpar:
        print("📝 Nenhuma tabela para limpar dados.")
        return [], []
    
    print(f"🧹 Limpando dados de {len(tabelas_para_limpar)} tabelas...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Desabilitar foreign keys temporariamente
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    tabelas_limpas = []
    tabelas_com_erro = []
    
    for tabela in tabelas_para_limpar:
        try:
            # Contar registros antes
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count_antes = cursor.fetchone()[0]
            
            # Limpar dados (DELETE, não DROP)
            cursor.execute(f"DELETE FROM {tabela}")
            
            # Verificar se foi limpa
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count_depois = cursor.fetchone()[0]
            
            tabelas_limpas.append((tabela, count_antes, count_depois))
            print(f"  ✅ Limpa: {tabela} ({count_antes} → {count_depois} registros)")
            
        except Exception as e:
            tabelas_com_erro.append((tabela, str(e)))
            print(f"  ❌ Erro ao limpar '{tabela}': {e}")
    
    # Reabilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()
    
    return tabelas_limpas, tabelas_com_erro

def main():
    """Função principal"""
    print("🧹 SCRIPT DE LIMPEZA DE DADOS - RegistroOS")
    print("=" * 50)
    print("REGRA: Tabelas que começam com 'tipo' ou 'tipos' → MANTER dados")
    print("       Tabelas que NÃO começam com 'tipo' ou 'tipos' → LIMPAR dados")
    print("=" * 50)
    
    # Verificar se o banco existe
    if not os.path.exists(DB_PATH):
        print(f"❌ Erro: Banco de dados não encontrado: {DB_PATH}")
        return
    
    # Listar tabelas
    tabelas_para_limpar, tabelas_para_manter = listar_tabelas_para_limpar()
    
    # Contar registros antes
    print("🔍 Contando registros atuais...")
    contadores_limpar = contar_registros_tabelas(tabelas_para_limpar)
    contadores_manter = contar_registros_tabelas(tabelas_para_manter)
    
    print(f"\n📊 ANÁLISE DAS TABELAS:")
    print(f"  • Tabelas que MANTERÃO dados (tipo/tipos): {len(tabelas_para_manter)}")
    print(f"  • Tabelas que terão dados LIMPOS: {len(tabelas_para_limpar)}")
    
    if tabelas_para_manter:
        print(f"\n✅ TABELAS QUE MANTERÃO DADOS (começam com tipo/tipos):")
        for tabela in sorted(tabelas_para_manter):
            count = contadores_manter.get(tabela, "N/A")
            print(f"  - {tabela}: {count} registros")
    
    if tabelas_para_limpar:
        print(f"\n🧹 TABELAS QUE TERÃO DADOS LIMPOS (NÃO começam com tipo/tipos):")
        for tabela in sorted(tabelas_para_limpar):
            count = contadores_limpar.get(tabela, "N/A")
            print(f"  - {tabela}: {count} registros")
    
    # Confirmação
    print(f"\n⚠️ ATENÇÃO: Esta operação LIMPA DADOS (não remove tabelas)!")
    print(f"Será feito backup completo antes da limpeza.")
    
    resposta = input("\nDeseja continuar? (digite 'CONFIRMO' para prosseguir): ")
    
    if resposta != 'CONFIRMO':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Executar limpeza
    print(f"\n🚀 INICIANDO LIMPEZA DE DADOS...")
    
    # 1. Backup completo
    criar_backup_completo()
    
    # 2. Limpar dados das tabelas
    tabelas_limpas, tabelas_com_erro = limpar_dados_tabelas(tabelas_para_limpar)
    
    # 3. Resumo final
    print(f"\n🎉 LIMPEZA DE DADOS CONCLUÍDA!")
    print(f"  ✅ Tabelas com dados limpos: {len(tabelas_limpas)}")
    print(f"  ✅ Tabelas com dados mantidos: {len(tabelas_para_manter)}")
    if tabelas_com_erro:
        print(f"  ⚠️ Tabelas com erro: {len(tabelas_com_erro)}")
    
    print(f"\n📁 Backup salvo em: {BACKUP_DB_PATH}")
    print(f"📋 IMPORTANTE: As tabelas foram mantidas, apenas os dados foram limpos!")
    
    # Verificação final
    print(f"\n🔍 VERIFICAÇÃO FINAL:")
    contadores_final_limpar = contar_registros_tabelas(tabelas_para_limpar)
    contadores_final_manter = contar_registros_tabelas(tabelas_para_manter)
    
    print("Tabelas com dados mantidos:")
    for tabela in sorted(tabelas_para_manter):
        count = contadores_final_manter.get(tabela, "N/A")
        print(f"  ✅ {tabela}: {count} registros")
    
    print("Tabelas com dados limpos:")
    for tabela in sorted(tabelas_para_limpar):
        count = contadores_final_limpar.get(tabela, "N/A")
        print(f"  🧹 {tabela}: {count} registros")

if __name__ == "__main__":
    main()
