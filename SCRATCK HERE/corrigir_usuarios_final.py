#!/usr/bin/env python3
"""
Corrigir TODOS os usuários
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario, Setor

def corrigir_usuarios():
    """Corrigir usuários"""
    
    print("🔧 Corrigindo usuários...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário MECANICA DIA
        usuario = db.query(Usuario).filter(Usuario.email == 'user.mecanica_dia@registroos.com').first()
        
        if usuario:
            # Buscar setor MECANICA DIA (ID 24)
            setor = db.query(Setor).filter(Setor.id == 24).first()
            
            if setor:
                print(f"Corrigindo {usuario.nome_completo}...")
                usuario.id_setor = setor.id
                usuario.id_departamento = setor.id_departamento
                usuario.setor = setor.nome
                
                db.commit()
                print(f"✅ Corrigido: {usuario.nome_completo} -> Setor: {setor.nome}")
            else:
                print("❌ Setor não encontrado")
        else:
            print("❌ Usuário não encontrado")
            
        # Verificar outros usuários
        usuarios = db.query(Usuario).all()
        for u in usuarios:
            email = u.email.lower()
            setor_nome = None
            
            if "mecanica_dia" in email:
                setor_nome = "MECANICA DIA "
            elif "mecanica_noite" in email:
                setor_nome = "MECANICA NOITE"
            elif "admin" in email:
                setor_nome = "ADMINISTRACAO"
                
            if setor_nome:
                setor = db.query(Setor).filter(Setor.nome.like(f"%{setor_nome.strip()}%")).first()
                if setor and u.id_setor != setor.id:
                    print(f"Corrigindo {u.nome_completo}...")
                    u.id_setor = setor.id
                    u.id_departamento = setor.id_departamento
                    u.setor = setor.nome
                    
        db.commit()
        print("✅ Todos corrigidos!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_usuarios()
