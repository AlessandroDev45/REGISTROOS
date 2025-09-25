#!/usr/bin/env python3
"""
Script para implementar estrutura hierárquica de máquinas
Adiciona campo descricao_partes na tabela tipos_maquina
"""

import sqlite3
import json
import os

def main():
    # Conectar ao banco
    db_path = 'registroos_new.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar se a coluna já existe
        cursor.execute('PRAGMA table_info(tipos_maquina)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'descricao_partes' not in columns:
            print('Adicionando coluna descricao_partes...')
            cursor.execute('ALTER TABLE tipos_maquina ADD COLUMN descricao_partes TEXT NULL')
            print('✅ Coluna adicionada com sucesso!')
        else:
            print('⚠️ Coluna descricao_partes já existe')
        
        # Estrutura exemplo para Rotativa CC
        estrutura_exemplo = {
            "partes": [
                {"nome": "Campo Shunt", "id_pai": None, "ordem": 1},
                {"nome": "Campo Série", "id_pai": None, "ordem": 2},
                {"nome": "Interpolos", "id_pai": None, "ordem": 3},
                {"nome": "Armadura", "id_pai": None, "ordem": 4},
                {"nome": "Acessórios", "id_pai": None, "ordem": 5,
                 "subpartes": [
                   {"nome": "Sensores", "id_pai": 5, "ordem": 1},
                   {"nome": "Resistores", "id_pai": 5, "ordem": 2},
                   {"nome": "Caixa Ligacao", "id_pai": 5, "ordem": 3}
                 ]
                }
            ]
        }
        
        # Buscar tipos de máquina que contenham 'Rotativa' ou 'CC'
        cursor.execute("SELECT id, nome_tipo FROM tipos_maquina WHERE nome_tipo LIKE '%Rotativa%' OR nome_tipo LIKE '%CC%'")
        maquinas = cursor.fetchall()
        
        # Se não encontrou nenhuma, pegar as primeiras 3 como exemplo
        if not maquinas:
            print("Nenhuma máquina 'Rotativa' ou 'CC' encontrada. Usando primeiras 3 como exemplo...")
            cursor.execute("SELECT id, nome_tipo FROM tipos_maquina LIMIT 3")
            maquinas = cursor.fetchall()
        
        # Atualizar máquinas encontradas
        for maquina_id, nome_tipo in maquinas:
            cursor.execute('UPDATE tipos_maquina SET descricao_partes = ? WHERE id = ?', 
                          (json.dumps(estrutura_exemplo), maquina_id))
            print(f'✅ Estrutura adicionada para: {nome_tipo}')
        
        # Verificar resultado
        cursor.execute('SELECT id, nome_tipo, descricao_partes FROM tipos_maquina WHERE descricao_partes IS NOT NULL')
        resultados = cursor.fetchall()
        
        print(f'\n📊 Tipos de máquina com estrutura hierárquica: {len(resultados)}')
        for resultado in resultados:
            print(f'  - ID {resultado[0]}: {resultado[1]}')
        
        conn.commit()
        print('\n✅ Script executado com sucesso!')
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
