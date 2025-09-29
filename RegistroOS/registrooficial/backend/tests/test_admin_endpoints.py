"""
Testes de integração para endpoints administrativos
"""
# Importação condicional do pytest
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest para quando não estiver instalado
    class MockPytest:
        @staticmethod
        def fixture(*args, **kwargs):
            _ = args, kwargs  # Silenciar warning
            def decorator(func):
                return func
            return decorator

        @staticmethod
        def main(args):
            _ = args  # Silenciar warning
            print("Mock pytest - testes não executados")

    pytest = MockPytest()

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.database_models import Base, Usuario
from config.database_config import get_db
from app.auth import create_access_token

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    """Configurar banco de dados de teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Cliente de teste FastAPI"""
    return TestClient(app)

@pytest.fixture
def admin_token():
    """Token de administrador para testes"""
    # Create a mock database session for token generation
    db = TestingSessionLocal()
    try:
        # Create a test user if it doesn't exist
        test_user = db.query(Usuario).filter(Usuario.email == "admin@test.com").first()
        if not test_user:
            test_user = Usuario(
                id=1,
                nome_completo="Admin Test",
                nome_usuario="admin_test",
                email="admin@test.com",
                senha_hash="test_hash",
                setor="ADMIN",
                departamento="ADMIN",
                privilege_level="ADMIN",
                is_approved=True,
                trabalha_producao=False,
                primeiro_login=False
            )
            db.add(test_user)
            db.commit()

        # Create token with database session
        user_data = {"sub": str(test_user.id)}
        return create_access_token(data=user_data, db=db)
    finally:
        db.close()

@pytest.fixture
def auth_headers(admin_token):
    """Headers de autenticação"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def sample_departamento():
    """Dados de exemplo para departamento"""
    return {
        "nome": "TESTE_DEPARTAMENTO",
        "descricao": "Departamento de teste",
        "ativo": True
    }

class TestDepartamentoEndpoints:
    """Testes para endpoints de departamento"""
    
    def test_create_departamento(self, client, auth_headers, sample_departamento, setup_database):
        """Teste de criação de departamento"""
        _ = setup_database  # Silenciar warning
        response = client.post(
            "/admin/departamentos",
            json=sample_departamento,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == sample_departamento["nome"]
        assert data["descricao"] == sample_departamento["descricao"]
        assert data["ativo"] == sample_departamento["ativo"]
    
    def test_list_departamentos(self, client, auth_headers, setup_database):
        """Teste de listagem de departamentos"""
        _ = setup_database  # Silenciar warning
        response = client.get("/admin/departamentos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_departamento_by_id(self, client, auth_headers, sample_departamento, setup_database):
        """Teste de busca de departamento por ID"""
        _ = setup_database  # Silenciar warning
        # Primeiro criar um departamento
        create_response = client.post(
            "/admin/departamentos",
            json=sample_departamento,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        departamento_id = create_response.json()["id"]
        
        # Buscar por ID
        response = client.get(f"/admin/departamentos/{departamento_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == departamento_id
        assert data["nome"] == sample_departamento["nome"]
    
    def test_update_departamento(self, client, auth_headers, sample_departamento, setup_database):
        """Teste de atualização de departamento"""
        _ = setup_database  # Silenciar warning
        # Criar departamento
        create_response = client.post(
            "/admin/departamentos",
            json=sample_departamento,
            headers=auth_headers
        )
        departamento_id = create_response.json()["id"]
        
        # Atualizar
        updated_data = {
            "nome": "DEPARTAMENTO_ATUALIZADO",
            "descricao": "Descrição atualizada",
            "ativo": True
        }
        response = client.put(
            f"/admin/departamentos/{departamento_id}",
            json=updated_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == updated_data["nome"]
        assert data["descricao"] == updated_data["descricao"]
    
    def test_delete_departamento(self, client, auth_headers, sample_departamento, setup_database):
        """Teste de exclusão (soft delete) de departamento"""
        _ = setup_database  # Silenciar warning
        # Criar departamento
        create_response = client.post(
            "/admin/departamentos",
            json=sample_departamento,
            headers=auth_headers
        )
        departamento_id = create_response.json()["id"]
        
        # Deletar
        response = client.delete(f"/admin/departamentos/{departamento_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verificar se foi soft delete (ativo = False)
        get_response = client.get(f"/admin/departamentos/{departamento_id}", headers=auth_headers)
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["ativo"] == False

class TestSetorEndpoints:
    """Testes para endpoints de setor"""
    
    def test_create_setor_with_departamento(self, client, auth_headers, setup_database):
        """Teste de criação de setor com departamento"""
        _ = setup_database  # Silenciar warning
        # Primeiro criar um departamento
        dept_data = {
            "nome": "DEPARTAMENTO_PARA_SETOR",
            "descricao": "Departamento para teste de setor",
            "ativo": True
        }
        dept_response = client.post("/admin/departamentos", json=dept_data, headers=auth_headers)
        assert dept_response.status_code == 201
        
        # Criar setor
        setor_data = {
            "nome": "SETOR_TESTE",
            "departamento": "DEPARTAMENTO_PARA_SETOR",
            "descricao": "Setor de teste",
            "ativo": True,
            "area_tipo": "PRODUCAO"
        }
        response = client.post("/admin/setores", json=setor_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == setor_data["nome"]
        assert data["departamento"] == setor_data["departamento"]
    
    def test_list_setores(self, client, auth_headers, setup_database):
        """Teste de listagem de setores"""
        _ = setup_database  # Silenciar warning
        response = client.get("/admin/setores", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestCatalogEndpoints:
    """Testes para endpoints de catálogo"""
    
    def test_get_departamentos_catalog(self, client, auth_headers, setup_database):
        """Teste do endpoint de catálogo de departamentos"""
        _ = setup_database  # Silenciar warning
        response = client.get("/api/departamentos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_setores_catalog(self, client, auth_headers, setup_database):
        """Teste do endpoint de catálogo de setores"""
        _ = setup_database  # Silenciar warning
        response = client.get("/api/setores", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestAuthenticationEndpoints:
    """Testes para endpoints de autenticação"""
    
    def test_health_check(self, client):
        """Teste de health check (não requer autenticação)"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_unauthorized_access(self, client):
        """Teste de acesso não autorizado"""
        response = client.get("/admin/departamentos")
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__])
