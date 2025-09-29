#!/usr/bin/env python3
"""
Teste dos endpoints de admin config
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database_models import Usuario
from config.database_config import get_db
from sqlalchemy.orm import Session

def test_admin_config_endpoints():
    """Testar endpoints de admin config"""
    
    print("🔧 [DEBUG] Iniciando teste dos endpoints de admin config...")
    
    client = TestClient(app)
    
    # Simular usuário admin
    db = next(get_db())
    admin_user = db.query(Usuario).filter(Usuario.privilege_level == 'ADMIN').first()
    
    if not admin_user:
        print("❌ [ERROR] Nenhum usuário admin encontrado no banco")
        return
    
    print(f"✅ [DEBUG] Usuário admin encontrado: {admin_user.nome}")
    
    # Headers de autenticação simulada
    headers = {
        "Authorization": f"Bearer test-token-{admin_user.id}",
        "Content-Type": "application/json"
    }
    
    # Testar endpoints
    endpoints = [
        "/api/admin/tipos-atividade",
        "/api/admin/tipos-falha", 
        "/api/admin/descricoes-atividade",
        "/api/admin/causas-retrabalho"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔧 [DEBUG] Testando {endpoint}...")
            
            # Fazer requisição direta ao endpoint sem autenticação (para teste)
            from routes.admin_config_routes import router
            from app.dependencies import get_current_user
            
            # Simular dependência de usuário
            def mock_get_current_user():
                return admin_user
            
            app.dependency_overrides[get_current_user] = mock_get_current_user
            
            response = client.get(endpoint)
            
            print(f"✅ [DEBUG] {endpoint} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ [DEBUG] {endpoint} - Retornou {len(data)} registros")
                if data:
                    print(f"✅ [DEBUG] {endpoint} - Primeiro registro: {data[0]}")
            else:
                print(f"❌ [ERROR] {endpoint} - Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ [ERROR] Erro ao testar {endpoint}: {e}")
            import traceback
            print(f"❌ [ERROR] Traceback: {traceback.format_exc()}")
    
    # Limpar override
    app.dependency_overrides.clear()
    db.close()
    
    print("✅ [DEBUG] Teste dos endpoints concluído")

if __name__ == "__main__":
    test_admin_config_endpoints()
