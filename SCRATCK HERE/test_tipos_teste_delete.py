#!/usr/bin/env python3
"""
Teste específico para verificar o problema de 401 no delete de tipos de teste
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

def test_tipos_teste_delete():
    """Testar especificamente o delete de tipos de teste"""
    
    print("🔧 [DEBUG] Testando delete de tipos de teste...")
    
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
    print("1. TESTANDO: Listar tipos de teste")
    print("="*60)
    
    try:
        response = client.get('/api/admin/tipos-teste')
        print(f"✅ [DEBUG] GET tipos-teste status: {response.status_code}")
        
        if response.status_code == 200:
            tipos_teste = response.json()
            print(f"✅ [DEBUG] Retornou {len(tipos_teste)} tipos de teste")
            
            if len(tipos_teste) > 0:
                primeiro_tipo = tipos_teste[0]
                tipo_id = primeiro_tipo['id']
                print(f"✅ [DEBUG] Primeiro tipo: ID {tipo_id}, Nome: {primeiro_tipo.get('nome', 'N/A')}")
                
                print("\n" + "="*60)
                print("2. TESTANDO: Delete de tipo de teste")
                print("="*60)
                
                # Testar delete
                response = client.delete(f'/api/admin/tipos-teste/{tipo_id}')
                print(f"✅ [DEBUG] DELETE tipos-teste/{tipo_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ [SUCESSO] Delete funcionou: {result}")
                    
                    # Verificar se não aparece mais na lista
                    response = client.get('/api/admin/tipos-teste')
                    if response.status_code == 200:
                        tipos_teste_after = response.json()
                        tipo_exists = any(t['id'] == tipo_id for t in tipos_teste_after)
                        if not tipo_exists:
                            print(f"✅ [SUCESSO] Tipo não aparece mais na lista após delete")
                        else:
                            print(f"⚠️ [AVISO] Tipo ainda aparece na lista (pode ser normal se não foi soft delete)")
                elif response.status_code == 401:
                    print(f"❌ [ERROR] 401 Unauthorized - Problema de autenticação")
                    print(f"❌ [ERROR] Resposta: {response.text}")
                elif response.status_code == 404:
                    print(f"❌ [ERROR] 404 Not Found - Tipo de teste não encontrado")
                    print(f"❌ [ERROR] Resposta: {response.text}")
                else:
                    print(f"❌ [ERROR] Status {response.status_code}: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum tipo de teste encontrado para testar delete")
        else:
            print(f"❌ [ERROR] Erro ao listar tipos de teste: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: Criar tipo de teste para delete")
    print("="*60)
    
    try:
        # Criar um tipo de teste para testar delete
        tipo_data = {
            'nome': 'TESTE DELETE',
            'descricao': 'Tipo de teste para testar delete',
            'ativo': True
        }
        
        response = client.post('/api/admin/tipos-teste', json=tipo_data)
        print(f"✅ [DEBUG] POST tipos-teste status: {response.status_code}")
        
        if response.status_code == 200:
            created_tipo = response.json()
            tipo_id = created_tipo['id']
            print(f"✅ [DEBUG] Tipo criado: ID {tipo_id}")
            
            # Tentar deletar o tipo criado
            response = client.delete(f'/api/admin/tipos-teste/{tipo_id}')
            print(f"✅ [DEBUG] DELETE tipos-teste/{tipo_id} status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ [SUCESSO] Delete do tipo criado funcionou: {result}")
            elif response.status_code == 401:
                print(f"❌ [ERROR] 401 Unauthorized no delete do tipo criado")
                print(f"❌ [ERROR] Resposta: {response.text}")
            else:
                print(f"❌ [ERROR] Status {response.status_code} no delete: {response.text}")
        else:
            print(f"❌ [ERROR] Erro ao criar tipo de teste: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de criação/delete: {e}")

    print("\n" + "="*60)
    print("4. VERIFICANDO: Função verificar_admin")
    print("="*60)
    
    try:
        # Testar se a função verificar_admin está funcionando
        from app.dependencies import verificar_admin
        print(f"✅ [DEBUG] Função verificar_admin importada com sucesso")
        
        # Testar outros endpoints que usam verificar_admin
        response = client.get('/api/admin/departamentos')
        print(f"✅ [DEBUG] GET departamentos (usa verificar_admin): {response.status_code}")
        
        response = client.get('/api/admin/setores')
        print(f"✅ [DEBUG] GET setores (usa verificar_admin): {response.status_code}")
        
        if response.status_code == 401:
            print(f"❌ [PROBLEMA] verificar_admin está rejeitando todas as requisições")
        else:
            print(f"✅ [INFO] verificar_admin funcionando para outros endpoints")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro ao verificar função verificar_admin: {e}")

    print("\n✅ [DEBUG] Teste de tipos de teste concluído!")

if __name__ == "__main__":
    test_tipos_teste_delete()
