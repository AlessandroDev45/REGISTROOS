#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text
from app.database_models import ApontamentoDetalhado, Setor, Departamento, Usuario

def testar_correcao():
    try:
        db = next(get_db())
        
        print("🔍 Testando a correção dos setores/departamentos...")
        
        # Buscar alguns apontamentos
        apontamentos = db.query(ApontamentoDetalhado).limit(5).all()
        
        print(f"\n📋 Testando {len(apontamentos)} apontamentos:")
        
        for apt in apontamentos:
            print(f"\n--- Apontamento ID: {apt.id} ---")
            print(f"  id_setor: {apt.id_setor}")
            print(f"  id_usuario: {apt.id_usuario}")
            
            # Buscar setor e departamento
            setor_nome = "Não informado"
            departamento_nome = "Não informado"
            
            if hasattr(apt, 'id_setor') and apt.id_setor:
                setor = db.query(Setor).filter(Setor.id == apt.id_setor).first()
                if setor:
                    setor_nome = setor.nome
                    print(f"  ✅ Setor encontrado: {setor_nome}")

                    # Buscar departamento do setor
                    if setor.id_departamento:
                        departamento = db.query(Departamento).filter(Departamento.id == setor.id_departamento).first()
                        if departamento:
                            departamento_nome = departamento.nome_tipo
                            print(f"  ✅ Departamento encontrado: {departamento_nome}")
                        else:
                            print(f"  ❌ Departamento não encontrado para id: {setor.id_departamento}")
                    else:
                        print(f"  ⚠️ Setor sem id_departamento")
                else:
                    print(f"  ❌ Setor não encontrado para id: {apt.id_setor}")
            else:
                print(f"  ⚠️ Apontamento sem id_setor")
                
                # Fallback: usar setor/departamento do usuário
                usuario = db.query(Usuario).filter(Usuario.id == apt.id_usuario).first()
                if usuario:
                    print(f"  🔄 Tentando fallback com usuário: {usuario.nome_completo}")
                    
                    if hasattr(usuario, 'id_setor') and usuario.id_setor:
                        setor = db.query(Setor).filter(Setor.id == usuario.id_setor).first()
                        if setor:
                            setor_nome = setor.nome
                            print(f"  ✅ Setor do usuário: {setor_nome}")

                    if hasattr(usuario, 'id_departamento') and usuario.id_departamento:
                        departamento = db.query(Departamento).filter(Departamento.id == usuario.id_departamento).first()
                        if departamento:
                            departamento_nome = departamento.nome_tipo
                            print(f"  ✅ Departamento do usuário: {departamento_nome}")
            
            print(f"  📊 Resultado final:")
            print(f"    Setor: {setor_nome}")
            print(f"    Departamento: {departamento_nome}")
        
        # Estatísticas gerais
        print(f"\n📊 Estatísticas gerais:")
        
        # Contar apontamentos com setor preenchido
        apontamentos_com_setor = db.query(ApontamentoDetalhado).filter(ApontamentoDetalhado.id_setor.isnot(None)).count()
        total_apontamentos = db.query(ApontamentoDetalhado).count()
        
        print(f"  Total de apontamentos: {total_apontamentos}")
        print(f"  Com id_setor preenchido: {apontamentos_com_setor}")
        print(f"  Sem id_setor: {total_apontamentos - apontamentos_com_setor}")
        
        # Contar setores disponíveis
        total_setores = db.query(Setor).count()
        total_departamentos = db.query(Departamento).count()
        
        print(f"  Total de setores: {total_setores}")
        print(f"  Total de departamentos: {total_departamentos}")
        
        db.close()
        
        print(f"\n✅ Teste concluído! A correção deve funcionar se:")
        print(f"  1. Apontamentos têm id_setor preenchido")
        print(f"  2. Setores existem na tabela tipo_setores")
        print(f"  3. Departamentos existem na tabela tipo_departamentos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_correcao()
