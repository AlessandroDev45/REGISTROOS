#!/usr/bin/env python3
"""
Debug específico para o usuário MECANICA DIA
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from app.database_models import Usuario, Setor, Departamento

def debug_usuario_mecanica():
    """Debug específico do usuário MECANICA DIA"""
    
    print("🔧 [DEBUG] Verificando usuário MECANICA DIA...")
    
    db = next(get_db())
    
    try:
        # Buscar usuário por nome_usuario
        usuario = db.query(Usuario).filter(Usuario.nome_usuario == 'MECANICA DIA').first()
        
        if not usuario:
            # Tentar por nome_completo
            usuario = db.query(Usuario).filter(Usuario.nome_completo.like('%MECANICA DIA%')).first()
            
        if not usuario:
            # Listar todos os usuários para ver os nomes
            print("❌ [ERROR] Usuário MECANICA DIA não encontrado")
            print("📋 [INFO] Usuários disponíveis:")
            usuarios = db.query(Usuario).all()
            for u in usuarios[:10]:  # Mostrar apenas os primeiros 10
                print(f"   - ID: {u.id}, Nome: {u.nome_completo}, Usuario: {u.nome_usuario}")
            return
            
        print(f"✅ [USUARIO] Encontrado:")
        print(f"   - ID: {usuario.id}")
        print(f"   - Nome Completo: {usuario.nome_completo}")
        print(f"   - Nome Usuario: {usuario.nome_usuario}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Privilege: {usuario.privilege_level}")
        print(f"   - ID Setor: {usuario.id_setor}")
        print(f"   - ID Departamento: {usuario.id_departamento}")
        print(f"   - Setor (campo texto): {usuario.setor}")
        print(f"   - Departamento (campo texto): {usuario.departamento}")
        print(f"   - Ativo: {usuario.is_approved}")
        
        # Verificar se o setor existe
        if usuario.id_setor:
            setor = db.query(Setor).filter(Setor.id == usuario.id_setor).first()
            if setor:
                print(f"✅ [SETOR] Setor encontrado:")
                print(f"   - ID: {setor.id}")
                print(f"   - Nome: {setor.nome}")
                print(f"   - Departamento: {setor.departamento}")
                print(f"   - Ativo: {setor.ativo}")
            else:
                print(f"❌ [SETOR] Setor ID {usuario.id_setor} não encontrado na tabela tipo_setores")
        else:
            print(f"⚠️ [SETOR] Usuario não tem id_setor definido")
            
        # Verificar se o departamento existe
        if usuario.id_departamento:
            departamento = db.query(Departamento).filter(Departamento.id == usuario.id_departamento).first()
            if departamento:
                print(f"✅ [DEPARTAMENTO] Departamento encontrado:")
                print(f"   - ID: {departamento.id}")
                print(f"   - Nome: {departamento.nome_tipo}")
                print(f"   - Ativo: {departamento.ativo}")
            else:
                print(f"❌ [DEPARTAMENTO] Departamento ID {usuario.id_departamento} não encontrado")
        else:
            print(f"⚠️ [DEPARTAMENTO] Usuario não tem id_departamento definido")
            
        # Buscar setor por nome (fallback)
        print(f"\n🔍 [FALLBACK] Buscando setor por nome '{usuario.setor}':")
        setor_por_nome = db.query(Setor).filter(Setor.nome == usuario.setor).first()
        if setor_por_nome:
            print(f"✅ [SETOR POR NOME] Encontrado:")
            print(f"   - ID: {setor_por_nome.id}")
            print(f"   - Nome: {setor_por_nome.nome}")
            print(f"   - Departamento: {setor_por_nome.departamento}")
            print(f"   - ID Departamento: {setor_por_nome.id_departamento}")
            print(f"   - Ativo: {setor_por_nome.ativo}")
            
            print(f"\n💡 [SOLUÇÃO] O usuário deveria ter:")
            print(f"   - id_setor: {setor_por_nome.id}")
            print(f"   - id_departamento: {setor_por_nome.id_departamento}")
        else:
            print(f"❌ [SETOR POR NOME] Setor '{usuario.setor}' não encontrado")
            
    except Exception as e:
        print(f"❌ [ERROR] Erro: {e}")
    finally:
        db.close()

    print("\n✅ [DEBUG] Debug concluído!")

if __name__ == "__main__":
    debug_usuario_mecanica()
