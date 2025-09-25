#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text

def verificar_os_12345():
    try:
        db = next(get_db())
        
        # Verificar se existe OS com número 12345
        result = db.execute(text("SELECT id, os_numero FROM ordens_servico WHERE os_numero = '12345'"))
        os_12345 = [dict(row._mapping) for row in result]
        
        print("🔍 Buscando OS com número 12345:")
        print(f"Resultado: {os_12345}")
        
        # Listar todas as OSs para verificar
        result_all = db.execute(text("SELECT id, os_numero FROM ordens_servico LIMIT 10"))
        todas_os = [dict(row._mapping) for row in result_all]
        
        print("\n📋 Primeiras 10 OSs no banco:")
        for os in todas_os:
            print(f"ID: {os['id']}, Número: {os['os_numero']}")
            
        # Verificar se existe apontamento com numero_os = 12345
        result_apontamento = db.execute(text("SELECT DISTINCT numero_os FROM apontamentos_detalhados WHERE numero_os = '12345' LIMIT 5"))
        apontamentos_12345 = [dict(row._mapping) for row in result_apontamento]
        
        print(f"\n🎯 Apontamentos com numero_os = 12345:")
        print(f"Resultado: {apontamentos_12345}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_os_12345()
