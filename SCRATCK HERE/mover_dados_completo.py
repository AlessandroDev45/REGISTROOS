#!/usr/bin/env python3
"""
Script para mover TODOS os dados de registroos.db para registroos_new.db
"""

import sys
import os
import sqlite3
import shutil

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def mover_todos_dados():
    """Move todos os dados de registroos.db para registroos_new.db"""
    try:
        print("🔄 Movendo TODOS os dados de registroos.db para registroos_new.db...")
        
        # Caminhos dos bancos
        banco_origem = os.path.join(backend_path, 'registroos.db')
        banco_destino = os.path.join(backend_path, 'registroos_new.db')
        
        print(f"  📂 Banco origem: {banco_origem}")
        print(f"  📂 Banco destino: {banco_destino}")
        
        # Verificar se o banco origem existe
        if not os.path.exists(banco_origem):
            print(f"  ❌ Banco origem não existe")
            return False
        
        # Fazer backup do banco destino se existir
        if os.path.exists(banco_destino):
            backup_destino = banco_destino + '.backup_antes_mover'
            shutil.copy2(banco_destino, backup_destino)
            print(f"  💾 Backup criado: {os.path.basename(backup_destino)}")
        
        # Conectar aos bancos
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        # Obter lista de todas as tabelas do banco origem
        cursor_origem.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor_origem.fetchall()]
        
        print(f"  📋 Tabelas encontradas: {len(tabelas)}")
        
        total_registros_movidos = 0
        
        for tabela in tabelas:
            print(f"\n  📋 Processando tabela: {tabela}")
            
            # Contar registros na origem
            cursor_origem.execute(f"SELECT COUNT(*) FROM {tabela}")
            count_origem = cursor_origem.fetchone()[0]
            print(f"    📊 Registros na origem: {count_origem}")
            
            if count_origem == 0:
                print(f"    ⚠️ Tabela vazia - pulando")
                continue
            
            # Obter estrutura da tabela
            cursor_origem.execute(f"PRAGMA table_info({tabela})")
            colunas_info = cursor_origem.fetchall()
            colunas = [col[1] for col in colunas_info]
            
            # Limpar tabela no destino
            try:
                cursor_destino.execute(f"DELETE FROM {tabela}")
                print(f"    🗑️ Tabela limpa no destino")
            except:
                print(f"    ⚠️ Erro ao limpar tabela - pode não existir")
            
            # Buscar todos os dados
            colunas_str = ', '.join(colunas)
            cursor_origem.execute(f"SELECT {colunas_str} FROM {tabela}")
            dados = cursor_origem.fetchall()
            
            if dados:
                # Inserir dados no destino
                placeholders = ', '.join(['?' for _ in colunas])
                insert_sql = f"INSERT OR REPLACE INTO {tabela} ({colunas_str}) VALUES ({placeholders})"
                
                cursor_destino.executemany(insert_sql, dados)
                conn_destino.commit()
                
                # Verificar resultado
                cursor_destino.execute(f"SELECT COUNT(*) FROM {tabela}")
                count_destino = cursor_destino.fetchone()[0]
                
                print(f"    ✅ {count_destino} registros movidos")
                total_registros_movidos += count_destino
            else:
                print(f"    ⚠️ Nenhum dado encontrado")
        
        conn_origem.close()
        conn_destino.close()
        
        print(f"\n📊 RESUMO:")
        print(f"  📋 Tabelas processadas: {len(tabelas)}")
        print(f"  📊 Total de registros movidos: {total_registros_movidos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao mover dados: {e}")
        return False

def verificar_resultado():
    """Verifica se a movimentação funcionou"""
    try:
        print(f"\n🔍 Verificando resultado...")
        
        banco_origem = os.path.join(backend_path, 'registroos.db')
        banco_destino = os.path.join(backend_path, 'registroos_new.db')
        
        # Verificar banco destino
        if not os.path.exists(banco_destino):
            print(f"  ❌ Banco destino não existe")
            return False
        
        conn_destino = sqlite3.connect(banco_destino)
        cursor_destino = conn_destino.cursor()
        
        # Verificar algumas tabelas importantes
        tabelas_importantes = ['tipo_usuarios', 'tipo_setores', 'tipo_departamentos', 'tipos_maquina']
        
        for tabela in tabelas_importantes:
            try:
                cursor_destino.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor_destino.fetchone()[0]
                print(f"  📊 {tabela}: {count} registros")
            except:
                print(f"  ❌ {tabela}: erro ao verificar")
        
        # Verificar usuário específico
        cursor_destino.execute("SELECT COUNT(*) FROM tipo_usuarios WHERE email = ?", ('admin@registroos.com',))
        admin_count = cursor_destino.fetchone()[0]
        
        if admin_count > 0:
            print(f"  ✅ Usuário admin encontrado no destino")
        else:
            print(f"  ❌ Usuário admin NÃO encontrado no destino")
        
        conn_destino.close()
        
        return admin_count > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar resultado: {e}")
        return False

def apagar_banco_origem():
    """Apaga o banco origem após confirmação"""
    try:
        print(f"\n🗑️ Apagando banco origem...")
        
        banco_origem = os.path.join(backend_path, 'registroos.db')
        
        if not os.path.exists(banco_origem):
            print(f"  ⚠️ Banco origem já não existe")
            return True
        
        # Fazer backup final antes de apagar
        backup_final = banco_origem + '.backup_final_antes_apagar'
        shutil.copy2(banco_origem, backup_final)
        print(f"  💾 Backup final criado: {os.path.basename(backup_final)}")
        
        # Apagar arquivo
        os.remove(banco_origem)
        print(f"  ✅ Banco origem apagado: {os.path.basename(banco_origem)}")
        
        # Verificar se foi apagado
        if not os.path.exists(banco_origem):
            print(f"  ✅ Confirmado: arquivo não existe mais")
            return True
        else:
            print(f"  ❌ Erro: arquivo ainda existe")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao apagar banco origem: {e}")
        return False

def main():
    print("🔄 Movendo TODOS os dados entre bancos...")
    print("=" * 60)
    
    # 1. Mover todos os dados
    sucesso_mover = mover_todos_dados()
    
    if not sucesso_mover:
        print(f"\n❌ Falha ao mover dados - ABORTANDO")
        return False
    
    # 2. Verificar resultado
    sucesso_verificar = verificar_resultado()
    
    if not sucesso_verificar:
        print(f"\n❌ Falha na verificação - ABORTANDO")
        return False
    
    # 3. Apagar banco origem
    sucesso_apagar = apagar_banco_origem()
    
    print(f"\n🎯 Processo concluído!")
    
    if sucesso_mover and sucesso_verificar and sucesso_apagar:
        print(f"✅ TODOS os dados movidos com sucesso!")
        print(f"✅ Banco origem apagado!")
        print(f"📂 Agora o servidor deve usar registroos_new.db")
        print(f"💾 Backups criados para segurança")
    else:
        print(f"❌ Processo incompleto - verifique os logs")
    
    return sucesso_mover and sucesso_verificar and sucesso_apagar

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
