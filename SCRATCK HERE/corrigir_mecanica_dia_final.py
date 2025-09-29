#!/usr/bin/env python3
"""
Corrigir usuário para o setor MECANICA DIA correto
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario, Setor

def corrigir_mecanica_dia_final():
    """Corrigir usuário para setor MECANICA DIA"""
    
    print("🔧 [CORREÇÃO FINAL] Corrigindo para MECANICA DIA...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário
        usuario = db.query(Usuario).filter(Usuario.nome_usuario == 'USERMECANICADIA').first()
        
        # Buscar setor MECANICA DIA (ID 24)
        setor = db.query(Setor).filter(Setor.id == 24).first()
        
        if not usuario or not setor:
            print("❌ [ERROR] Usuário ou setor não encontrado")
            return
            
        print(f"✅ [ANTES]:")
        print(f"   - Usuário: {usuario.nome_completo}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Setor atual: {usuario.setor}")
        print(f"   - ID Setor atual: {usuario.id_setor}")
        
        print(f"\n✅ [SETOR CORRETO]:")
        print(f"   - ID: {setor.id}")
        print(f"   - Nome: '{setor.nome}'")
        print(f"   - Departamento: {setor.departamento}")
        print(f"   - ID Departamento: {setor.id_departamento}")
        
        # CORRIGIR
        usuario.id_setor = setor.id
        usuario.id_departamento = setor.id_departamento
        usuario.setor = setor.nome
        
        # Salvar
        db.commit()
        db.refresh(usuario)
        
        print(f"\n🎯 [SUCESSO] Usuário corrigido:")
        print(f"   - ID Setor: {usuario.id_setor}")
        print(f"   - ID Departamento: {usuario.id_departamento}")
        print(f"   - Setor: '{usuario.setor}'")
        
        print(f"\n✅ [RESULTADO] Agora vai aparecer:")
        print(f"   'USUARIO MECANICA DIA | Setor: {setor.nome.strip()}'")
        
    except Exception as e:
        print(f"❌ [ERROR] Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_mecanica_dia_final()
