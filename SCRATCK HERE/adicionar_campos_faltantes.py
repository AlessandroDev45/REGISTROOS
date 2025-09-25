#!/usr/bin/env python3
"""
Script para adicionar os campos que estão faltando na estrutura do banco
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def adicionar_campos_faltantes():
    """Adiciona os campos que estão faltando"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Adicionando campos faltantes...")
        
        # Campos para adicionar na ordens_servico
        campos_os = [
            ("status_geral", "VARCHAR(50)"),
            ("testes_exclusivo_os", "TEXT")
        ]
        
        for campo, tipo in campos_os:
            try:
                sql = f"ALTER TABLE ordens_servico ADD COLUMN {campo} {tipo}"
                cursor.execute(sql)
                print(f"✅ Campo {campo} adicionado à ordens_servico")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"ℹ️ Campo {campo} já existe na ordens_servico")
                else:
                    print(f"❌ Erro ao adicionar {campo}: {e}")
        
        # Renomear campo testes_exclusivo para testes_exclusivo_os se necessário
        try:
            # Verificar se o campo antigo existe
            cursor.execute("PRAGMA table_info(ordens_servico)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'testes_exclusivo' in colunas and 'testes_exclusivo_os' not in colunas:
                print("🔄 Renomeando campo testes_exclusivo para testes_exclusivo_os...")
                
                # SQLite não suporta RENAME COLUMN diretamente, então vamos copiar os dados
                cursor.execute("ALTER TABLE ordens_servico ADD COLUMN testes_exclusivo_os TEXT")
                cursor.execute("UPDATE ordens_servico SET testes_exclusivo_os = testes_exclusivo")
                print("✅ Dados copiados para testes_exclusivo_os")
                
                # Nota: Não vamos dropar a coluna antiga para manter compatibilidade
                
        except Exception as e:
            print(f"⚠️ Erro ao renomear campo: {e}")
        
        # Verificar campos do apontamentos_detalhados que podem estar faltando
        campos_ap = [
            ("causa_retrabalho", "VARCHAR(255)"),
            ("observacao_os", "TEXT"),
            ("servico_de_campo", "BOOLEAN"),
            ("categoria_maquina", "VARCHAR(100)"),
            ("subcategorias_maquina", "TEXT"),
            ("subcategorias_finalizadas", "BOOLEAN DEFAULT 0"),
            ("data_finalizacao_subcategorias", "DATETIME")
        ]
        
        for campo, tipo in campos_ap:
            try:
                sql = f"ALTER TABLE apontamentos_detalhados ADD COLUMN {campo} {tipo}"
                cursor.execute(sql)
                print(f"✅ Campo {campo} adicionado à apontamentos_detalhados")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"ℹ️ Campo {campo} já existe na apontamentos_detalhados")
                else:
                    print(f"❌ Erro ao adicionar {campo}: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Campos faltantes adicionados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar campos: {e}")
        return False

def verificar_estrutura_final():
    """Verifica a estrutura final após adicionar os campos"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando estrutura final...")
        
        # Verificar ordens_servico
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        
        campos_esperados = [
            'status_geral', 'testes_exclusivo_os', 'id_usuario_testes_iniciais',
            'id_usuario_testes_parciais', 'id_usuario_testes_finais'
        ]
        
        print("📋 Campos da ordens_servico:")
        for campo in campos_esperados:
            status = "✅" if campo in colunas_os else "❌"
            print(f"  {status} {campo}")
        
        # Verificar apontamentos_detalhados
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas_ap = [col[1] for col in cursor.fetchall()]
        
        campos_ap_esperados = [
            'causa_retrabalho', 'observacao_os', 'servico_de_campo',
            'categoria_maquina', 'subcategorias_maquina'
        ]
        
        print("\n📋 Campos do apontamentos_detalhados:")
        for campo in campos_ap_esperados:
            status = "✅" if campo in colunas_ap else "❌"
            print(f"  {status} {campo}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🔧 Adicionando campos faltantes ao banco de dados...")
    print("=" * 60)
    
    if not adicionar_campos_faltantes():
        return False
    
    if not verificar_estrutura_final():
        return False
    
    print("\n🎉 Estrutura do banco atualizada com sucesso!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
