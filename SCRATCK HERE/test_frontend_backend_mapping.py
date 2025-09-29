#!/usr/bin/env python3
"""
Teste de mapeamento entre frontend e backend para atividades
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

def test_frontend_backend_mapping():
    """Testar mapeamento de campos entre frontend e backend"""
    
    print("🔧 [DEBUG] Testando mapeamento frontend-backend para atividades...")
    
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

    # Dados como o frontend enviaria (usando 'nome' em vez de 'nome_tipo')
    frontend_data = {
        'nome': 'TESTE FRONTEND',  # Frontend usa 'nome'
        'descricao': 'Teste de mapeamento frontend-backend',
        'departamento': 'MOTORES',
        'setor': 'LABORATORIO DE ENSAIOS ELETRICOS',
        'categoria': 'MOTOR',
        'ativo': True
    }
    
    print(f"📤 [DEBUG] Dados enviados pelo frontend: {frontend_data}")
    
    # Testar POST
    print('\n🔧 [DEBUG] Testando POST com dados do frontend...')
    try:
        response = client.post('/api/admin/tipos-atividade', json=frontend_data)
        print(f'✅ [DEBUG] POST Status: {response.status_code}')
        
        if response.status_code == 200:
            created_data = response.json()
            print(f'✅ [DEBUG] POST criou registro: {created_data}')
            
            # Verificar se o campo 'nome' foi mapeado corretamente
            if 'nome' in created_data:
                print(f"✅ [DEBUG] Campo 'nome' retornado corretamente: {created_data['nome']}")
            else:
                print(f"❌ [ERROR] Campo 'nome' não encontrado na resposta")
                
            created_id = created_data.get('id')
            
            if created_id:
                # Testar GET by ID
                print(f'\n🔧 [DEBUG] Testando GET by ID...')
                response = client.get(f'/api/admin/tipos-atividade/{created_id}')
                print(f'✅ [DEBUG] GET by ID Status: {response.status_code}')
                
                if response.status_code == 200:
                    get_data = response.json()
                    print(f'✅ [DEBUG] GET by ID retornou: {get_data}')
                    
                    # Verificar mapeamento de campos
                    if 'nome' in get_data:
                        print(f"✅ [DEBUG] Campo 'nome' mapeado corretamente: {get_data['nome']}")
                    else:
                        print(f"❌ [ERROR] Campo 'nome' não encontrado no GET")
                
                # Testar PUT com dados do frontend
                print(f'\n🔧 [DEBUG] Testando PUT com dados do frontend...')
                update_data = {
                    'nome': 'TESTE FRONTEND ATUALIZADO',
                    'descricao': 'Teste atualizado'
                }
                response = client.put(f'/api/admin/tipos-atividade/{created_id}', json=update_data)
                print(f'✅ [DEBUG] PUT Status: {response.status_code}')
                
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f'✅ [DEBUG] PUT atualizou: {updated_data}')
                    
                    if 'nome' in updated_data and updated_data['nome'] == 'TESTE FRONTEND ATUALIZADO':
                        print(f"✅ [DEBUG] Campo 'nome' atualizado corretamente")
                    else:
                        print(f"❌ [ERROR] Campo 'nome' não foi atualizado corretamente")
                else:
                    print(f'❌ [ERROR] PUT erro: {response.text}')
                
                # Limpar - deletar o registro de teste
                print(f'\n🔧 [DEBUG] Limpando registro de teste...')
                response = client.delete(f'/api/admin/tipos-atividade/{created_id}')
                print(f'✅ [DEBUG] DELETE Status: {response.status_code}')
                
        else:
            print(f'❌ [ERROR] POST erro: {response.text}')
            
    except Exception as e:
        print(f'❌ [ERROR] Exceção durante teste: {e}')
        import traceback
        print(f'❌ [ERROR] Traceback: {traceback.format_exc()}')

    print('\n✅ [DEBUG] Teste de mapeamento concluído')

if __name__ == "__main__":
    test_frontend_backend_mapping()
