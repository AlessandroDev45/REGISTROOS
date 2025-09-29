#!/usr/bin/env python3
"""
Teste para verificar se os endpoints de departamentos e setores estão funcionando
para o formulário de atividades
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

def test_atividade_dropdowns():
    """Testar se os endpoints para dropdowns de atividades estão funcionando"""
    
    print("🔧 [DEBUG] Testando endpoints para dropdowns de atividades...")
    
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
    print("1. TESTANDO: Endpoint de Departamentos")
    print("="*60)
    
    try:
        response = client.get('/api/admin/departamentos')
        print(f"✅ [DEBUG] GET /api/admin/departamentos status: {response.status_code}")
        
        if response.status_code == 200:
            departamentos = response.json()
            print(f"✅ [DEBUG] Retornou {len(departamentos)} departamentos")
            
            if len(departamentos) > 0:
                primeiro_dept = departamentos[0]
                campos_dept = list(primeiro_dept.keys())
                print(f"✅ [DEBUG] Campos do departamento: {campos_dept}")
                print(f"✅ [DEBUG] Primeiro departamento: {primeiro_dept}")
                
                # Verificar se tem o campo nome_tipo
                if 'nome_tipo' in primeiro_dept:
                    print(f"✅ [SUCESSO] Campo 'nome_tipo' presente: {primeiro_dept['nome_tipo']}")
                else:
                    print(f"❌ [ERRO] Campo 'nome_tipo' não encontrado")
                    
                if 'nome' in primeiro_dept:
                    print(f"✅ [INFO] Campo 'nome' também presente: {primeiro_dept['nome']}")
            else:
                print("⚠️ [AVISO] Nenhum departamento encontrado")
        else:
            print(f"❌ [ERROR] Erro no endpoint: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de departamentos: {e}")

    print("\n" + "="*60)
    print("2. TESTANDO: Endpoint de Setores")
    print("="*60)
    
    try:
        response = client.get('/api/admin/setores')
        print(f"✅ [DEBUG] GET /api/admin/setores status: {response.status_code}")
        
        if response.status_code == 200:
            setores = response.json()
            print(f"✅ [DEBUG] Retornou {len(setores)} setores")
            
            if len(setores) > 0:
                primeiro_setor = setores[0]
                campos_setor = list(primeiro_setor.keys())
                print(f"✅ [DEBUG] Campos do setor: {campos_setor}")
                print(f"✅ [DEBUG] Primeiro setor: {primeiro_setor}")
                
                # Verificar se tem os campos necessários
                if 'nome' in primeiro_setor:
                    print(f"✅ [SUCESSO] Campo 'nome' presente: {primeiro_setor['nome']}")
                else:
                    print(f"❌ [ERRO] Campo 'nome' não encontrado")
                    
                if 'departamento' in primeiro_setor:
                    print(f"✅ [SUCESSO] Campo 'departamento' presente: {primeiro_setor['departamento']}")
                else:
                    print(f"❌ [ERRO] Campo 'departamento' não encontrado")
                    
                if 'departamento_nome' in primeiro_setor:
                    print(f"✅ [INFO] Campo 'departamento_nome' presente: {primeiro_setor['departamento_nome']}")
            else:
                print("⚠️ [AVISO] Nenhum setor encontrado")
        else:
            print(f"❌ [ERROR] Erro no endpoint: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de setores: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: Endpoint Público de Setores (usado pelo frontend)")
    print("="*60)
    
    try:
        # Testar endpoint público que o frontend usa
        response = client.get('/setores')  # Sem /api/admin
        print(f"✅ [DEBUG] GET /setores status: {response.status_code}")
        
        if response.status_code == 200:
            setores = response.json()
            print(f"✅ [DEBUG] Endpoint público retornou {len(setores)} setores")
            
            if len(setores) > 0:
                primeiro_setor = setores[0]
                print(f"✅ [DEBUG] Primeiro setor (público): {primeiro_setor}")
        else:
            print(f"❌ [ERROR] Endpoint público com erro: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de endpoint público: {e}")

    print("\n" + "="*60)
    print("DIAGNÓSTICO E SOLUÇÕES")
    print("="*60)
    print("🔍 [INFO] Verificando possíveis problemas:")
    print("1. Se departamentos retornam vazio → Verificar se há dados na database")
    print("2. Se setores retornam vazio → Verificar se há dados na database")
    print("3. Se campos estão errados → Verificar mapeamento no frontend")
    print("4. Se endpoint público falha → Verificar se rota existe")
    
    print("\n✅ [DEBUG] Teste de dropdowns de atividades concluído!")

if __name__ == "__main__":
    test_atividade_dropdowns()
