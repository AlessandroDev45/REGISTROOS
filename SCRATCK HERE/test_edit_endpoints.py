#!/usr/bin/env python3
"""
Teste para verificar se os endpoints de busca individual (para edição) estão retornando dados corretos
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

def test_edit_endpoints():
    """Testar se os endpoints de busca individual retornam dados para edição"""
    
    print("🔧 [DEBUG] Testando endpoints de busca individual para edição...")
    
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
    print("1. TESTANDO: Busca individual de Departamento")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/departamentos')
        if response.status_code == 200:
            departamentos = response.json()
            if len(departamentos) > 0:
                dept_id = departamentos[0]['id']
                print(f"✅ [DEBUG] Testando departamento ID: {dept_id}")
                
                # Buscar individual
                response = client.get(f'/api/admin/departamentos/{dept_id}')
                print(f"✅ [DEBUG] GET departamentos/{dept_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    dept_data = response.json()
                    print(f"✅ [SUCESSO] Dados retornados:")
                    print(f"   - ID: {dept_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {dept_data.get('nome', 'VAZIO')}")
                    print(f"   - Nome_tipo: {dept_data.get('nome_tipo', 'VAZIO')}")
                    print(f"   - Descrição: {dept_data.get('descricao', 'VAZIO')}")
                    print(f"   - Ativo: {dept_data.get('ativo', 'VAZIO')}")
                    
                    if not dept_data.get('nome') and not dept_data.get('nome_tipo'):
                        print(f"❌ [PROBLEMA] Nome está vazio!")
                else:
                    print(f"❌ [ERROR] Erro na busca: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum departamento encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar departamentos: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de departamento: {e}")

    print("\n" + "="*60)
    print("2. TESTANDO: Busca individual de Setor")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/setores')
        if response.status_code == 200:
            setores = response.json()
            if len(setores) > 0:
                setor_id = setores[0]['id']
                print(f"✅ [DEBUG] Testando setor ID: {setor_id}")
                
                # Buscar individual
                response = client.get(f'/api/admin/setores/{setor_id}')
                print(f"✅ [DEBUG] GET setores/{setor_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    setor_data = response.json()
                    print(f"✅ [SUCESSO] Dados retornados:")
                    print(f"   - ID: {setor_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {setor_data.get('nome', 'VAZIO')}")
                    print(f"   - Departamento: {setor_data.get('departamento', 'VAZIO')}")
                    print(f"   - Tipo Área: {setor_data.get('tipo_area', 'VAZIO')}")
                    print(f"   - Ativo: {setor_data.get('ativo', 'VAZIO')}")
                    
                    if not setor_data.get('nome'):
                        print(f"❌ [PROBLEMA] Nome está vazio!")
                else:
                    print(f"❌ [ERROR] Erro na busca: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum setor encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar setores: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de setor: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: Busca individual de Tipo de Máquina")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/tipos-maquina')
        if response.status_code == 200:
            tipos = response.json()
            if len(tipos) > 0:
                tipo_id = tipos[0]['id']
                print(f"✅ [DEBUG] Testando tipo máquina ID: {tipo_id}")
                
                # Buscar individual
                response = client.get(f'/api/admin/tipos-maquina/{tipo_id}')
                print(f"✅ [DEBUG] GET tipos-maquina/{tipo_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    tipo_data = response.json()
                    print(f"✅ [SUCESSO] Dados retornados:")
                    print(f"   - ID: {tipo_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {tipo_data.get('nome', 'VAZIO')}")
                    print(f"   - Nome_tipo: {tipo_data.get('nome_tipo', 'VAZIO')}")
                    print(f"   - Categoria: {tipo_data.get('categoria', 'VAZIO')}")
                    print(f"   - Subcategoria: {tipo_data.get('subcategoria', 'VAZIO')}")
                    print(f"   - Setor: {tipo_data.get('setor', 'VAZIO')}")
                    print(f"   - Ativo: {tipo_data.get('ativo', 'VAZIO')}")
                    
                    if not tipo_data.get('nome') and not tipo_data.get('nome_tipo'):
                        print(f"❌ [PROBLEMA] Nome está vazio!")
                else:
                    print(f"❌ [ERROR] Erro na busca: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum tipo de máquina encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar tipos de máquina: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de tipo de máquina: {e}")

    print("\n" + "="*60)
    print("4. TESTANDO: Busca individual de Tipo de Atividade")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/tipos-atividade')
        if response.status_code == 200:
            atividades = response.json()
            if len(atividades) > 0:
                atividade_id = atividades[0]['id']
                print(f"✅ [DEBUG] Testando atividade ID: {atividade_id}")
                
                # Buscar individual
                response = client.get(f'/api/admin/tipos-atividade/{atividade_id}')
                print(f"✅ [DEBUG] GET tipos-atividade/{atividade_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    atividade_data = response.json()
                    print(f"✅ [SUCESSO] Dados retornados:")
                    print(f"   - ID: {atividade_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {atividade_data.get('nome', 'VAZIO')}")
                    print(f"   - Nome_tipo: {atividade_data.get('nome_tipo', 'VAZIO')}")
                    print(f"   - Descrição: {atividade_data.get('descricao', 'VAZIO')}")
                    print(f"   - Departamento: {atividade_data.get('departamento', 'VAZIO')}")
                    print(f"   - Setor: {atividade_data.get('setor', 'VAZIO')}")
                    print(f"   - Categoria: {atividade_data.get('categoria', 'VAZIO')}")
                    print(f"   - Ativo: {atividade_data.get('ativo', 'VAZIO')}")
                    
                    if not atividade_data.get('nome') and not atividade_data.get('nome_tipo'):
                        print(f"❌ [PROBLEMA] Nome está vazio!")
                else:
                    print(f"❌ [ERROR] Erro na busca: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhuma atividade encontrada")
        else:
            print(f"❌ [ERROR] Erro ao listar atividades: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de atividade: {e}")

    print("\n✅ [DEBUG] Teste de endpoints de edição concluído!")

if __name__ == "__main__":
    test_edit_endpoints()
