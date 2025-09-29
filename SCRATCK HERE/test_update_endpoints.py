#!/usr/bin/env python3
"""
Teste para verificar se os endpoints de UPDATE (PUT) estão funcionando
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

def test_update_endpoints():
    """Testar se os endpoints de UPDATE estão funcionando"""
    
    print("🔧 [DEBUG] Testando endpoints de UPDATE...")
    
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
    print("1. TESTANDO: UPDATE de Departamento")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/departamentos')
        if response.status_code == 200:
            departamentos = response.json()
            if len(departamentos) > 0:
                dept_id = departamentos[0]['id']
                print(f"✅ [DEBUG] Testando update departamento ID: {dept_id}")
                
                # Dados para update
                update_data = {
                    "nome": "MOTORES TESTE UPDATE",
                    "descricao": "Descrição atualizada via teste",
                    "ativo": True
                }
                
                # Fazer UPDATE
                response = client.put(f'/api/admin/departamentos/{dept_id}', json=update_data)
                print(f"✅ [DEBUG] PUT departamentos/{dept_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f"✅ [SUCESSO] Update funcionou:")
                    print(f"   - ID: {updated_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {updated_data.get('nome', 'VAZIO')}")
                    print(f"   - Descrição: {updated_data.get('descricao', 'VAZIO')}")
                else:
                    print(f"❌ [ERROR] Erro no update: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum departamento encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar departamentos: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de departamento: {e}")

    print("\n" + "="*60)
    print("2. TESTANDO: UPDATE de Setor")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/setores')
        if response.status_code == 200:
            setores = response.json()
            if len(setores) > 0:
                setor_id = setores[0]['id']
                print(f"✅ [DEBUG] Testando update setor ID: {setor_id}")
                
                # Dados para update
                update_data = {
                    "nome": "SETOR TESTE UPDATE",
                    "descricao": "Descrição atualizada via teste",
                    "departamento": "MOTORES",
                    "tipo_area": "PRODUCAO",
                    "ativo": True
                }
                
                # Fazer UPDATE
                response = client.put(f'/api/admin/setores/{setor_id}', json=update_data)
                print(f"✅ [DEBUG] PUT setores/{setor_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f"✅ [SUCESSO] Update funcionou:")
                    print(f"   - ID: {updated_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {updated_data.get('nome', 'VAZIO')}")
                    print(f"   - Departamento: {updated_data.get('departamento', 'VAZIO')}")
                else:
                    print(f"❌ [ERROR] Erro no update: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum setor encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar setores: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de setor: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: UPDATE de Tipo de Máquina")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/tipos-maquina')
        if response.status_code == 200:
            tipos = response.json()
            if len(tipos) > 0:
                tipo_id = tipos[0]['id']
                print(f"✅ [DEBUG] Testando update tipo máquina ID: {tipo_id}")
                
                # Dados para update
                update_data = {
                    "nome": "MAQUINA TESTE UPDATE",
                    "categoria": "MOTOR",
                    "subcategoria": "TESTE",
                    "setor": "LABORATORIO",
                    "ativo": True
                }
                
                # Fazer UPDATE
                response = client.put(f'/api/admin/tipos-maquina/{tipo_id}', json=update_data)
                print(f"✅ [DEBUG] PUT tipos-maquina/{tipo_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f"✅ [SUCESSO] Update funcionou:")
                    print(f"   - ID: {updated_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {updated_data.get('nome', 'VAZIO')}")
                    print(f"   - Categoria: {updated_data.get('categoria', 'VAZIO')}")
                else:
                    print(f"❌ [ERROR] Erro no update: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum tipo de máquina encontrado")
        else:
            print(f"❌ [ERROR] Erro ao listar tipos de máquina: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de tipo de máquina: {e}")

    print("\n" + "="*60)
    print("4. TESTANDO: UPDATE de Tipo de Atividade")
    print("="*60)
    
    try:
        # Primeiro listar para pegar um ID
        response = client.get('/api/admin/tipos-atividade')
        if response.status_code == 200:
            atividades = response.json()
            if len(atividades) > 0:
                atividade_id = atividades[0]['id']
                print(f"✅ [DEBUG] Testando update atividade ID: {atividade_id}")
                
                # Dados para update
                update_data = {
                    "nome": "ATIVIDADE TESTE UPDATE",
                    "descricao": "Descrição atualizada",
                    "departamento": "MOTORES",
                    "setor": "LABORATORIO",
                    "categoria": "MOTOR",
                    "ativo": True
                }
                
                # Fazer UPDATE
                response = client.put(f'/api/admin/tipos-atividade/{atividade_id}', json=update_data)
                print(f"✅ [DEBUG] PUT tipos-atividade/{atividade_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f"✅ [SUCESSO] Update funcionou:")
                    print(f"   - ID: {updated_data.get('id', 'VAZIO')}")
                    print(f"   - Nome: {updated_data.get('nome', 'VAZIO')}")
                    print(f"   - Departamento: {updated_data.get('departamento', 'VAZIO')}")
                else:
                    print(f"❌ [ERROR] Erro no update: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhuma atividade encontrada")
        else:
            print(f"❌ [ERROR] Erro ao listar atividades: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de atividade: {e}")

    print("\n" + "="*60)
    print("VERIFICANDO: Endpoints de UPDATE disponíveis")
    print("="*60)
    
    # Verificar quais endpoints PUT existem
    endpoints_put = [
        "/api/admin/departamentos/1",
        "/api/admin/setores/1", 
        "/api/admin/tipos-maquina/1",
        "/api/admin/tipos-atividade/1",
        "/api/admin/tipos-teste/1",
        "/api/admin/tipos-falha/1",
        "/api/admin/causas-retrabalho/1",
        "/api/admin/descricoes-atividade/1"
    ]
    
    for endpoint in endpoints_put:
        try:
            response = client.put(endpoint, json={"teste": "dados"})
            if response.status_code == 404:
                print(f"❌ [MISSING] {endpoint} - Endpoint não encontrado")
            elif response.status_code == 422:
                print(f"✅ [EXISTS] {endpoint} - Endpoint existe (erro de validação esperado)")
            elif response.status_code == 401:
                print(f"⚠️ [AUTH] {endpoint} - Problema de autenticação")
            else:
                print(f"✅ [EXISTS] {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ [ERROR] {endpoint} - Erro: {e}")

    print("\n✅ [DEBUG] Teste de endpoints de UPDATE concluído!")

if __name__ == "__main__":
    test_update_endpoints()
