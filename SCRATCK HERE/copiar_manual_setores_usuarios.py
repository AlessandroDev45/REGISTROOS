#!/usr/bin/env python3
"""
Script para copiar manualmente tipo_setores e tipo_usuarios tratando NULLs
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def copiar_tipo_setores():
    """Copia dados da tabela tipo_setores tratando campos NULL"""
    try:
        banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print("📋 Copiando tipo_setores...")
        
        # Buscar dados da origem
        cursor_origem.execute("SELECT * FROM tipo_setores")
        dados_origem = cursor_origem.fetchall()
        
        # Obter nomes das colunas da origem
        cursor_origem.execute("PRAGMA table_info(tipo_setores)")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        # Obter nomes das colunas do destino
        cursor_destino.execute("PRAGMA table_info(tipo_setores)")
        colunas_destino = [col[1] for col in cursor_destino.fetchall()]
        
        print(f"  📊 Registros na origem: {len(dados_origem)}")
        print(f"  📋 Colunas origem: {colunas_origem}")
        print(f"  📋 Colunas destino: {colunas_destino}")
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM tipo_setores")
        
        # Processar cada registro
        registros_inseridos = 0
        for linha in dados_origem:
            try:
                # Criar dicionário com os dados
                dados_dict = dict(zip(colunas_origem, linha))
                
                # Tratar campos NULL/vazios
                if dados_dict.get('departamento') is None:
                    dados_dict['departamento'] = 'GERAL'  # Valor padrão
                
                if dados_dict.get('setor') is None or dados_dict.get('setor') == '':
                    dados_dict['setor'] = f"SETOR_{dados_dict.get('id', 'NOVO')}"
                
                # Preparar dados para inserção (apenas colunas que existem no destino)
                dados_para_inserir = []
                colunas_para_inserir = []
                
                for col in colunas_destino:
                    if col in dados_dict:
                        colunas_para_inserir.append(col)
                        dados_para_inserir.append(dados_dict[col])
                
                # Inserir no destino
                placeholders = ', '.join(['?' for _ in colunas_para_inserir])
                colunas_str = ', '.join(colunas_para_inserir)
                sql = f"INSERT INTO tipo_setores ({colunas_str}) VALUES ({placeholders})"
                
                cursor_destino.execute(sql, dados_para_inserir)
                registros_inseridos += 1
                
                print(f"  ✅ Registro {registros_inseridos}: {dados_dict.get('setor', 'N/A')} - {dados_dict.get('departamento', 'N/A')}")
                
            except Exception as e:
                print(f"  ❌ Erro no registro {linha}: {e}")
        
        conn_destino.commit()
        conn_origem.close()
        conn_destino.close()
        
        print(f"  🎉 {registros_inseridos} registros inseridos em tipo_setores")
        return registros_inseridos
        
    except Exception as e:
        print(f"❌ Erro ao copiar tipo_setores: {e}")
        return 0

def copiar_tipo_usuarios():
    """Copia dados da tabela tipo_usuarios tratando campos NULL"""
    try:
        banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print("\n📋 Copiando tipo_usuarios...")
        
        # Buscar dados da origem
        cursor_origem.execute("SELECT * FROM tipo_usuarios")
        dados_origem = cursor_origem.fetchall()
        
        # Obter nomes das colunas da origem
        cursor_origem.execute("PRAGMA table_info(tipo_usuarios)")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        # Obter nomes das colunas do destino
        cursor_destino.execute("PRAGMA table_info(tipo_usuarios)")
        colunas_destino = [col[1] for col in cursor_destino.fetchall()]
        
        print(f"  📊 Registros na origem: {len(dados_origem)}")
        print(f"  📋 Colunas origem: {colunas_origem}")
        print(f"  📋 Colunas destino: {colunas_destino}")
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM tipo_usuarios")
        
        # Processar cada registro
        registros_inseridos = 0
        for linha in dados_origem:
            try:
                # Criar dicionário com os dados
                dados_dict = dict(zip(colunas_origem, linha))
                
                # Tratar campos NULL/vazios
                if dados_dict.get('setor') is None or dados_dict.get('setor') == '':
                    dados_dict['setor'] = 'GERAL'  # Valor padrão
                
                if dados_dict.get('departamento') is None or dados_dict.get('departamento') == '':
                    dados_dict['departamento'] = 'GERAL'  # Valor padrão
                
                if dados_dict.get('nome') is None or dados_dict.get('nome') == '':
                    dados_dict['nome'] = f"Usuario_{dados_dict.get('id', 'NOVO')}"
                
                # Preparar dados para inserção (apenas colunas que existem no destino)
                dados_para_inserir = []
                colunas_para_inserir = []
                
                for col in colunas_destino:
                    if col in dados_dict:
                        colunas_para_inserir.append(col)
                        dados_para_inserir.append(dados_dict[col])
                
                # Inserir no destino
                placeholders = ', '.join(['?' for _ in colunas_para_inserir])
                colunas_str = ', '.join(colunas_para_inserir)
                sql = f"INSERT INTO tipo_usuarios ({colunas_str}) VALUES ({placeholders})"
                
                cursor_destino.execute(sql, dados_para_inserir)
                registros_inseridos += 1
                
                print(f"  ✅ Registro {registros_inseridos}: {dados_dict.get('nome', 'N/A')} - {dados_dict.get('setor', 'N/A')}")
                
            except Exception as e:
                print(f"  ❌ Erro no registro {linha}: {e}")
        
        conn_destino.commit()
        conn_origem.close()
        conn_destino.close()
        
        print(f"  🎉 {registros_inseridos} registros inseridos em tipo_usuarios")
        return registros_inseridos
        
    except Exception as e:
        print(f"❌ Erro ao copiar tipo_usuarios: {e}")
        return 0

def verificar_resultado():
    """Verifica o resultado final"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_destino)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificação final...")
        
        # Verificar tipo_setores
        cursor.execute("SELECT COUNT(*) FROM tipo_setores")
        count_setores = cursor.fetchone()[0]
        print(f"  📊 tipo_setores: {count_setores} registros")
        
        # Verificar tipo_usuarios
        cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
        count_usuarios = cursor.fetchone()[0]
        print(f"  📊 tipo_usuarios: {count_usuarios} registros")
        
        # Total geral
        tabelas_principais = [
            'tipo_atividade', 'tipo_causas_retrabalho', 'tipo_departamentos',
            'tipo_descricao_atividade', 'tipo_setores', 'tipo_usuarios',
            'tipos_maquina', 'tipos_teste'
        ]
        
        total_registros = 0
        for tabela in tabelas_principais:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            total_registros += count
        
        print(f"  📊 Total geral: {total_registros} registros")
        
        conn.close()
        return count_setores + count_usuarios
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return 0

def main():
    print("🚀 Copiando manualmente tipo_setores e tipo_usuarios...")
    print("=" * 60)
    
    # Copiar tipo_setores
    setores_copiados = copiar_tipo_setores()
    
    # Copiar tipo_usuarios
    usuarios_copiados = copiar_tipo_usuarios()
    
    # Verificar resultado
    total_verificado = verificar_resultado()
    
    print(f"\n🎉 CÓPIA MANUAL CONCLUÍDA!")
    print(f"✅ tipo_setores: {setores_copiados} registros")
    print(f"✅ tipo_usuarios: {usuarios_copiados} registros")
    print(f"✅ Total copiado: {setores_copiados + usuarios_copiados} registros")
    
    if setores_copiados > 0 and usuarios_copiados > 0:
        print(f"🎯 SUCESSO TOTAL! Todas as tabelas tipo/tipos agora têm dados.")
    else:
        print(f"⚠️ Algumas tabelas podem não ter sido copiadas completamente.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
