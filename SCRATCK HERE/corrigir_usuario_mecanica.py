#!/usr/bin/env python3
"""
Corrigir APENAS os IDs do usuário MECANICA DIA
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario

def corrigir_usuario_mecanica():
    """Corrigir IDs do usuário MECANICA DIA"""
    
    print("🔧 [CORREÇÃO] Corrigindo usuário MECANICA DIA...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário MECANICA DIA
        usuario = db.query(Usuario).filter(Usuario.nome_usuario == 'USERMECANICADIA').first()
        
        if not usuario:
            print("❌ [ERROR] Usuário não encontrado")
            return
            
        print(f"✅ [ANTES] Usuário encontrado:")
        print(f"   - ID: {usuario.id}")
        print(f"   - Nome: {usuario.nome_completo}")
        print(f"   - ID Setor: {usuario.id_setor}")
        print(f"   - ID Departamento: {usuario.id_departamento}")
        
        # CORRIGIR os IDs
        usuario.id_setor = 41  # LABORATORIO DE ENSAIOS ELETRICOS
        usuario.id_departamento = 2  # MOTORES (ID correto)
        
        # Salvar no banco
        db.commit()
        db.refresh(usuario)
        
        print(f"\n✅ [DEPOIS] Usuário corrigido:")
        print(f"   - ID: {usuario.id}")
        print(f"   - Nome: {usuario.nome_completo}")
        print(f"   - ID Setor: {usuario.id_setor}")
        print(f"   - ID Departamento: {usuario.id_departamento}")
        
        print(f"\n🎯 [SUCESSO] Usuário MECANICA DIA corrigido!")
        print(f"   Agora vai aparecer: 'USUARIO MECANICA DIA | Setor: LABORATORIO DE ENSAIOS ELETRICOS'")
        
    except Exception as e:
        print(f"❌ [ERROR] Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_usuario_mecanica()
