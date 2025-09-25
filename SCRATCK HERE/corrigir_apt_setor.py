#!/usr/bin/env python3
"""
Script para corrigir todas as referências a apt.setor no sistema
"""

import os
import re
import sqlite3
from datetime import datetime

# Configurações
BACKEND_DIR = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
DB_PATH = os.path.join(BACKEND_DIR, "registroos_new.db")

def criar_backup():
    """Criar backup do banco antes das alterações"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"registroos_backup_apt_setor_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None

def verificar_estrutura_apontamentos():
    """Verificar se a tabela apontamentos_detalhados tem o campo setor"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura da tabela apontamentos_detalhados:")
        tem_setor = False
        tem_id_setor = False
        
        for coluna in colunas:
            nome_coluna = coluna[1]
            tipo_coluna = coluna[2]
            print(f"  - {nome_coluna}: {tipo_coluna}")
            
            if nome_coluna == 'setor':
                tem_setor = True
            elif nome_coluna == 'id_setor':
                tem_id_setor = True
        
        print(f"\n🔍 Análise:")
        print(f"  - Campo 'setor' existe: {tem_setor}")
        print(f"  - Campo 'id_setor' existe: {tem_id_setor}")
        
        conn.close()
        return tem_setor, tem_id_setor
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False, False

def remover_campo_setor_se_existe():
    """Remove o campo setor da tabela apontamentos_detalhados se ele existir"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o campo setor existe
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'setor' in colunas:
            print("🔧 Removendo campo 'setor' da tabela apontamentos_detalhados...")
            
            # Criar nova tabela sem o campo setor
            cursor.execute("""
                CREATE TABLE apontamentos_detalhados_new AS 
                SELECT * FROM apontamentos_detalhados
            """)
            
            # Remover coluna setor da nova tabela
            colunas_sem_setor = [col for col in colunas if col != 'setor']
            colunas_select = ', '.join(colunas_sem_setor)
            
            cursor.execute("DROP TABLE apontamentos_detalhados_new")
            
            # Recriar tabela sem o campo setor
            cursor.execute(f"""
                CREATE TABLE apontamentos_detalhados_new AS 
                SELECT {colunas_select} FROM apontamentos_detalhados
            """)
            
            # Substituir tabela original
            cursor.execute("DROP TABLE apontamentos_detalhados")
            cursor.execute("ALTER TABLE apontamentos_detalhados_new RENAME TO apontamentos_detalhados")
            
            conn.commit()
            print("✅ Campo 'setor' removido com sucesso!")
        else:
            print("ℹ️ Campo 'setor' não existe na tabela")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao remover campo setor: {e}")

def corrigir_arquivos_python():
    """Corrigir referências a apt.setor nos arquivos Python"""
    arquivos_para_corrigir = [
        "routes/desenvolvimento.py",
        "routes/general.py",
        "routes/pcp_routes.py",
        "routes/os_routes_simple.py"
    ]
    
    padroes_correcao = [
        # Padrão: apt.setor em dicionários
        (r'"setor":\s*apt\.setor', '"setor": "Não informado"  # Corrigido: era apt.setor'),
        # Padrão: apt.setor em comparações
        (r'apt\.setor\s*==', 'getattr(apt, "id_setor", None) =='),
        # Padrão: apt.setor em atribuições
        (r'=\s*apt\.setor', '= "Não informado"  # Corrigido: era apt.setor'),
        # Padrão: apt.setor em prints
        (r'apt\.setor', '"Não informado"  # Corrigido: era apt.setor'),
    ]
    
    total_correcoes = 0
    
    for arquivo_rel in arquivos_para_corrigir:
        arquivo_path = os.path.join(BACKEND_DIR, arquivo_rel)
        
        if not os.path.exists(arquivo_path):
            print(f"⚠️ Arquivo não encontrado: {arquivo_path}")
            continue
        
        print(f"\n🔧 Corrigindo: {arquivo_rel}")
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            conteudo_original = conteudo
            correcoes_arquivo = 0
            
            for padrao, substituicao in padroes_correcao:
                matches = re.findall(padrao, conteudo)
                if matches:
                    conteudo = re.sub(padrao, substituicao, conteudo)
                    correcoes_arquivo += len(matches)
                    print(f"  ✅ {len(matches)} correções para padrão: {padrao}")
            
            if conteudo != conteudo_original:
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"  📝 {correcoes_arquivo} correções aplicadas em {arquivo_rel}")
                total_correcoes += correcoes_arquivo
            else:
                print(f"  ℹ️ Nenhuma correção necessária em {arquivo_rel}")
                
        except Exception as e:
            print(f"  ❌ Erro ao processar {arquivo_rel}: {e}")
    
    return total_correcoes

def main():
    print("🚀 Iniciando correção de referências apt.setor...")
    print("=" * 60)
    
    # 1. Criar backup
    backup_path = criar_backup()
    if not backup_path:
        print("❌ Falha ao criar backup. Abortando.")
        return
    
    # 2. Verificar estrutura do banco
    tem_setor, tem_id_setor = verificar_estrutura_apontamentos()
    
    # 3. Remover campo setor se existir
    if tem_setor:
        remover_campo_setor_se_existe()
    
    # 4. Corrigir arquivos Python
    total_correcoes = corrigir_arquivos_python()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA CORREÇÃO:")
    print(f"  - Backup criado: {backup_path}")
    print(f"  - Campo 'setor' removido: {'Sim' if tem_setor else 'Não era necessário'}")
    print(f"  - Total de correções em código: {total_correcoes}")
    print("✅ Correção concluída com sucesso!")

if __name__ == "__main__":
    main()
