#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text

def verificar_apontamentos():
    try:
        db = next(get_db())
        
        # Verificar estrutura da tabela apontamentos_detalhados
        result = db.execute(text("PRAGMA table_info(apontamentos_detalhados)"))
        colunas = [dict(row._mapping) for row in result]
        
        print("🔍 Estrutura da tabela apontamentos_detalhados:")
        for col in colunas:
            print(f"  {col['name']} ({col['type']}) - NOT NULL: {col['notnull']}")
        
        # Verificar alguns apontamentos
        result = db.execute(text("SELECT id, id_setor, id_usuario FROM apontamentos_detalhados LIMIT 5"))
        apontamentos = [dict(row._mapping) for row in result]
        
        print(f"\n📋 Primeiros 5 apontamentos:")
        for apt in apontamentos:
            print(f"  ID: {apt['id']}, id_setor: {apt['id_setor']}, id_usuario: {apt['id_usuario']}")
            
        # Verificar usuários e seus setores
        result = db.execute(text("SELECT id, nome_completo, id_setor, id_departamento FROM tipo_usuarios LIMIT 5"))
        usuarios = [dict(row._mapping) for row in result]
        
        print(f"\n👥 Primeiros 5 usuários:")
        for user in usuarios:
            print(f"  ID: {user['id']}, Nome: {user['nome_completo']}, id_setor: {user['id_setor']}, id_departamento: {user['id_departamento']}")
            
        # Verificar setores
        result = db.execute(text("SELECT id, nome, id_departamento FROM tipo_setores LIMIT 5"))
        setores = [dict(row._mapping) for row in result]
        
        print(f"\n🏭 Primeiros 5 setores:")
        for setor in setores:
            print(f"  ID: {setor['id']}, Nome: {setor['nome']}, id_departamento: {setor['id_departamento']}")
            
        # Verificar departamentos
        result = db.execute(text("SELECT id, nome_tipo FROM tipo_departamentos LIMIT 5"))
        departamentos = [dict(row._mapping) for row in result]
        
        print(f"\n🏢 Primeiros 5 departamentos:")
        for dept in departamentos:
            print(f"  ID: {dept['id']}, Nome: {dept['nome_tipo']}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_apontamentos()
