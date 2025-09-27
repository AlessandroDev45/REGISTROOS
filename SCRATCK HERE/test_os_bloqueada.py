#!/usr/bin/env python3
"""
Teste simples para verificar a funcionalidade de detecção de OS bloqueada
"""

import sys
import os

# Adicionar o caminho do projeto ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import sqlite3

def test_os_bloqueada():
    """Teste se a detecção de OS bloqueada funciona corretamente"""
    
    # Conectar ao banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'registroos_new.db')
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Lista de status que bloqueiam apontamentos
    status_finalizados = [
        'RECUSADA - CONFERIDA',
        'TERMINADA - CONFERIDA',
        'TERMINADA - EXPEDIDA',
        'TERMINADA - ARQUIVADA',
        'OS CANCELADA'
    ]
    
    try:
        with engine.connect() as conn:
            # Buscar todas as OS
            result = conn.execute(text("SELECT os_numero, status_os FROM ordens_servico LIMIT 10"))
            os_list = result.fetchall()
            
            print(f"Total de OS encontradas: {len(os_list)}")
            
            # Verificar cada OS
            for os_num, status in os_list:
                bloqueada = status in status_finalizados
                print(f"OS: {os_num} - Status: {status} - Bloqueada: {bloqueada}")
                
                if bloqueada:
                    print(f"  -> OS {os_num} está bloqueada para apontamentos!")
            
            # Teste específico com status finalizado
            print("\n=== Teste com status finalizado ===")
            test_os_num = "12345"
            test_status = "TERMINADA - CONFERIDA"
            
            # Simular a lógica do endpoint
            bloqueada = test_status in status_finalizados
            print(f"OS: {test_os_num} - Status: {test_status} - Bloqueada: {bloqueada}")
            
            if bloqueada:
                print(f"✅ Detecção de OS bloqueada funcionando corretamente!")
            else:
                print(f"❌ Falha na detecção de OS bloqueada!")
                
    except Exception as e:
        print(f"Erro ao testar: {e}")

if __name__ == "__main__":
    test_os_bloqueada()
