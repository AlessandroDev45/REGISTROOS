#!/usr/bin/env python3
"""
Corrigir setor do usuário de acordo com o email
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario, Setor

def corrigir_setor_pelo_email():
    """Corrigir setor do usuário baseado no email"""
    
    print("🔧 [CORREÇÃO] Corrigindo setor baseado no email...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário MECANICA DIA
        usuario = db.query(Usuario).filter(Usuario.nome_usuario == 'USERMECANICADIA').first()
        
        if not usuario:
            print("❌ [ERROR] Usuário não encontrado")
            return
            
        print(f"✅ [USUARIO] Encontrado:")
        print(f"   - Nome: {usuario.nome_completo}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Setor atual (texto): {usuario.setor}")
        print(f"   - ID Setor atual: {usuario.id_setor}")
        
        # Extrair setor do email
        email = usuario.email
        print(f"\n📧 [EMAIL] Analisando: {email}")
        
        # Email: user.mecanica_dia@registroos.com
        # Setor deve ser: MECANICA DIA
        
        if "mecanica_dia" in email.lower():
            setor_nome = "MECANICA DIA"
        else:
            print("❌ [ERROR] Não consegui identificar o setor pelo email")
            return
            
        print(f"🎯 [SETOR] Setor identificado pelo email: {setor_nome}")
        
        # Buscar setor na tabela
        setor = db.query(Setor).filter(Setor.nome == setor_nome).first()
        
        if setor:
            print(f"✅ [SETOR ENCONTRADO]:")
            print(f"   - ID: {setor.id}")
            print(f"   - Nome: {setor.nome}")
            print(f"   - Departamento: {setor.departamento}")
            print(f"   - ID Departamento: {setor.id_departamento}")
            print(f"   - Ativo: {setor.ativo}")
            
            # CORRIGIR o usuário
            print(f"\n🔧 [CORRIGINDO] Atualizando usuário...")
            usuario.id_setor = setor.id
            usuario.id_departamento = setor.id_departamento
            usuario.setor = setor.nome  # Atualizar campo texto também
            
            # Salvar
            db.commit()
            db.refresh(usuario)
            
            print(f"✅ [SUCESSO] Usuário corrigido:")
            print(f"   - ID Setor: {usuario.id_setor}")
            print(f"   - ID Departamento: {usuario.id_departamento}")
            print(f"   - Setor: {usuario.setor}")
            
            print(f"\n🎯 [RESULTADO] Agora vai aparecer:")
            print(f"   'USUARIO MECANICA DIA | Setor: {setor.nome}'")
            
        else:
            print(f"❌ [ERROR] Setor '{setor_nome}' não encontrado na tabela")
            
            # Listar setores disponíveis
            print(f"\n📋 [SETORES DISPONÍVEIS]:")
            setores = db.query(Setor).filter(Setor.ativo == True).all()
            for s in setores:
                if "MECANICA" in s.nome.upper():
                    print(f"   - ID: {s.id}, Nome: {s.nome}, Dept: {s.departamento}")
        
    except Exception as e:
        print(f"❌ [ERROR] Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_setor_pelo_email()
