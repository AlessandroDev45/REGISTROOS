#!/usr/bin/env python3
"""
Script para verificar o banco de dados e os dados de TipoMaquina
"""

import sys
import os

# Adicionar o diretório do backend ao path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import Session
from config.database_config import get_db
from app.database_models import TipoMaquina, Departamento, Usuario

def check_database():
    """Verifica o banco de dados"""
    
    print("🔍 Verificando banco de dados...")
    
    try:
        # Obter sessão do banco
        db_gen = get_db()
        db = next(db_gen)
        
        # Verificar usuários
        print("\n👥 Verificando usuários:")
        usuarios = db.query(Usuario).all()
        print(f"Total de usuários: {len(usuarios)}")
        for user in usuarios[:3]:  # Mostrar apenas os primeiros 3
            print(f"  - {user.email} (ID: {user.id}, Aprovado: {user.is_approved})")
        
        # Verificar departamentos
        print("\n🏢 Verificando departamentos:")
        departamentos = db.query(Departamento).all()
        print(f"Total de departamentos: {len(departamentos)}")
        for dept in departamentos:
            print(f"  - {dept.nome_tipo} (ID: {dept.id})")
        
        # Verificar tipos de máquina
        print("\n🔧 Verificando tipos de máquina:")
        tipos_maquina = db.query(TipoMaquina).all()
        print(f"Total de tipos de máquina: {len(tipos_maquina)}")
        
        for tipo in tipos_maquina[:5]:  # Mostrar apenas os primeiros 5
            print(f"  - {tipo.nome_tipo} (Categoria: {tipo.categoria}, Dept ID: {tipo.id_departamento})")
        
        # Verificar categorias únicas
        print("\n📋 Verificando categorias únicas:")
        categorias = db.query(TipoMaquina.categoria).distinct().filter(
            TipoMaquina.categoria.isnot(None),
            TipoMaquina.categoria != ''
        ).all()
        
        categorias_list = [cat[0] for cat in categorias if cat[0]]
        print(f"Total de categorias: {len(categorias_list)}")
        for cat in categorias_list:
            print(f"  - {cat}")
        
        # Testar filtro por departamento
        print("\n🔍 Testando filtro por departamento 'MOTORES':")
        dept_motores = db.query(Departamento).filter(Departamento.nome_tipo == "MOTORES").first()
        if dept_motores:
            print(f"Departamento MOTORES encontrado (ID: {dept_motores.id})")
            
            tipos_motores = db.query(TipoMaquina).filter(
                TipoMaquina.id_departamento == dept_motores.id,
                TipoMaquina.ativo == True
            ).all()
            print(f"Tipos de máquina no departamento MOTORES: {len(tipos_motores)}")
            
            categorias_motores = db.query(TipoMaquina.categoria).distinct().filter(
                TipoMaquina.id_departamento == dept_motores.id,
                TipoMaquina.categoria.isnot(None),
                TipoMaquina.categoria != '',
                TipoMaquina.ativo == True
            ).all()
            
            categorias_motores_list = [cat[0] for cat in categorias_motores if cat[0]]
            print(f"Categorias no departamento MOTORES: {categorias_motores_list}")
        else:
            print("❌ Departamento MOTORES não encontrado")
        
        db.close()
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
