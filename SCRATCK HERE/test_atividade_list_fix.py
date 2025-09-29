#!/usr/bin/env python3
"""
Teste para verificar se a listagem de tipos de atividade está retornando o campo nome corretamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.admin_config_routes import router
from app.dependencies import get_current_user
from app.database_models import Usuario
from config.database_config import get_db

def test_atividade_list_fix():
    """Testar se a listagem de tipos de atividade retorna o campo nome"""
    
    print("🔧 [DEBUG] Testando listagem de tipos de atividade...")
    
    # Criar app de teste
    app = FastAPI()
    app.include_router(router, prefix='/api/admin')

    # Mock do usuário admin
    def mock_get_current_user():
        db = next(get_db())
        admin_user = db.query(Usuario).filter(Usuario.privilege_level == 'ADMIN').first()
        db.close()
        return admin_user

    app.dependency_overrides[get_current_user] = mock_get_current_user

    client = TestClient(app)

    print("\n" + "="*60)
    print("TESTANDO: Listagem de Tipos de Atividade")
    print("="*60)
    
    try:
        response = client.get('/api/admin/tipos-atividade')
        print(f"✅ [DEBUG] GET tipos-atividade status: {response.status_code}")
        
        if response.status_code == 200:
            atividades = response.json()
            print(f"✅ [DEBUG] Retornou {len(atividades)} tipos de atividade")
            
            if len(atividades) > 0:
                print(f"\n📋 [RESULTADO] Primeiros 3 tipos de atividade:")
                for i, atividade in enumerate(atividades[:3]):
                    print(f"\n   🔹 ATIVIDADE {i+1}:")
                    print(f"      - ID: {atividade.get('id', 'VAZIO')}")
                    print(f"      - Nome: {atividade.get('nome', 'VAZIO')}")
                    print(f"      - Nome_tipo: {atividade.get('nome_tipo', 'VAZIO')}")
                    print(f"      - Descrição: {atividade.get('descricao', 'VAZIO')}")
                    print(f"      - Departamento: {atividade.get('departamento', 'VAZIO')}")
                    print(f"      - Setor: {atividade.get('setor', 'VAZIO')}")
                    print(f"      - Categoria: {atividade.get('categoria', 'VAZIO')}")
                    print(f"      - Ativo: {atividade.get('ativo', 'VAZIO')}")
                    
                    # Verificar se os campos essenciais estão preenchidos
                    if not atividade.get('nome'):
                        print(f"      ❌ [PROBLEMA] Campo 'nome' está vazio!")
                    else:
                        print(f"      ✅ [OK] Campo 'nome' preenchido")
                        
                    if not atividade.get('nome_tipo'):
                        print(f"      ❌ [PROBLEMA] Campo 'nome_tipo' está vazio!")
                    else:
                        print(f"      ✅ [OK] Campo 'nome_tipo' preenchido")
                        
                    if not atividade.get('descricao'):
                        print(f"      ⚠️ [AVISO] Campo 'descricao' está vazio")
                    else:
                        print(f"      ✅ [OK] Campo 'descricao' preenchido")
                
                # Verificar se todos têm o campo nome preenchido
                sem_nome = [a for a in atividades if not a.get('nome')]
                if len(sem_nome) > 0:
                    print(f"\n❌ [PROBLEMA] {len(sem_nome)} atividades sem campo 'nome':")
                    for atividade in sem_nome[:5]:  # Mostrar apenas as primeiras 5
                        print(f"   - ID {atividade.get('id')}: nome_tipo='{atividade.get('nome_tipo')}', nome='{atividade.get('nome')}'")
                else:
                    print(f"\n✅ [SUCESSO] Todas as {len(atividades)} atividades têm campo 'nome' preenchido!")
                    
                # Verificar se todos têm descrição
                sem_descricao = [a for a in atividades if not a.get('descricao')]
                if len(sem_descricao) > 0:
                    print(f"\n⚠️ [AVISO] {len(sem_descricao)} atividades sem descrição")
                else:
                    print(f"\n✅ [INFO] Todas as atividades têm descrição")
                    
            else:
                print("⚠️ [AVISO] Nenhum tipo de atividade encontrado")
        else:
            print(f"❌ [ERROR] Erro na listagem: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste: {e}")

    print("\n" + "="*60)
    print("COMPARANDO: Dados diretos do banco vs API")
    print("="*60)
    
    try:
        # Verificar dados diretos do banco
        from app.database_models import TipoAtividade
        from config.database_config import get_db
        
        db = next(get_db())
        atividades_db = db.query(TipoAtividade).limit(3).all()
        
        print(f"📊 [BANCO] Primeiros 3 registros diretos do banco:")
        for i, atividade in enumerate(atividades_db):
            print(f"\n   🔹 REGISTRO {i+1} (Banco):")
            print(f"      - ID: {atividade.id}")
            print(f"      - nome_tipo: '{atividade.nome_tipo}'")
            print(f"      - descricao: '{atividade.descricao}'")
            print(f"      - departamento: '{atividade.departamento}'")
            print(f"      - setor: '{atividade.setor}'")
            print(f"      - categoria: '{atividade.categoria}'")
            print(f"      - ativo: {atividade.ativo}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ [ERROR] Erro ao acessar banco: {e}")

    print("\n✅ [DEBUG] Teste de listagem de atividades concluído!")

if __name__ == "__main__":
    test_atividade_list_fix()
