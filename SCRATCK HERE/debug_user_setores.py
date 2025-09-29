#!/usr/bin/env python3
"""
Debug para verificar por que o usuário MECANICA DIA não vê setores
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario, Setor

def debug_user_setores():
    """Debug do problema de setores do usuário"""
    
    print("🔧 [DEBUG] Verificando setores para usuário MECANICA DIA...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário MECANICA DIA
        usuario = db.query(Usuario).filter(Usuario.username == 'MECANICA DIA').first()
        
        if usuario:
            print(f"✅ [USUARIO] Encontrado:")
            print(f"   - ID: {usuario.id}")
            print(f"   - Username: {usuario.username}")
            print(f"   - Privilege: {usuario.privilege_level}")
            print(f"   - ID Setor: {usuario.id_setor}")
            print(f"   - ID Departamento: {usuario.id_departamento}")
            print(f"   - Ativo: {usuario.ativo}")
        else:
            print("❌ [ERROR] Usuário MECANICA DIA não encontrado")
            return
            
        # Buscar todos os setores
        print(f"\n📋 [SETORES] Todos os setores:")
        setores = db.query(Setor).all()
        for setor in setores:
            print(f"   - ID: {setor.id}, Nome: {setor.nome}, Dept: {setor.departamento}, Ativo: {setor.ativo}")
            
        # Buscar setores do departamento MOTORES
        print(f"\n🏭 [SETORES MOTORES] Setores do departamento MOTORES:")
        setores_motores = db.query(Setor).filter(Setor.departamento == 'MOTORES').all()
        for setor in setores_motores:
            print(f"   - ID: {setor.id}, Nome: {setor.nome}, Ativo: {setor.ativo}")
            
        # Verificar se existe setor MECANICA DIA
        print(f"\n🔍 [SETOR ESPECIFICO] Procurando setor 'MECANICA DIA':")
        setor_mecanica = db.query(Setor).filter(Setor.nome == 'MECANICA DIA').first()
        if setor_mecanica:
            print(f"   ✅ Encontrado: ID {setor_mecanica.id}, Dept: {setor_mecanica.departamento}, Ativo: {setor_mecanica.ativo}")
        else:
            print(f"   ❌ Setor 'MECANICA DIA' não encontrado")
            
        # Verificar endpoint que o frontend chama
        print(f"\n📡 [API] Simulando chamada do frontend...")
        
        # Simular filtro por departamento (como o frontend faz)
        if usuario.id_departamento:
            setores_dept = db.query(Setor).filter(Setor.id_departamento == usuario.id_departamento).all()
            print(f"   📊 Setores por ID departamento {usuario.id_departamento}: {len(setores_dept)}")
            for setor in setores_dept:
                print(f"      - {setor.nome} (ID: {setor.id}, Ativo: {setor.ativo})")
        else:
            print(f"   ⚠️ Usuário não tem id_departamento definido")
            
    except Exception as e:
        print(f"❌ [ERROR] Erro: {e}")
    finally:
        db.close()

    print("\n✅ [DEBUG] Debug concluído!")

if __name__ == "__main__":
    debug_user_setores()
