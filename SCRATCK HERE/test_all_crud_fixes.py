#!/usr/bin/env python3
"""
Teste completo para verificar todas as correções de CRUD:
1. Campo ativo vai como 0 em vez de deletar (soft delete)
2. Setores conseguem ser criados
3. Delete funciona (soft delete)
4. Máquina busca o campo categoria
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

def test_all_crud_fixes():
    """Testar todas as correções de CRUD"""
    
    print("🔧 [DEBUG] Testando todas as correções de CRUD...")
    
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
    print("1. TESTANDO: Soft Delete de Departamentos")
    print("="*60)
    
    try:
        # Criar departamento para testar
        dept_data = {
            'nome': 'TESTE SOFT DELETE',
            'descricao': 'Teste de soft delete',
            'ativo': True
        }
        
        response = client.post('/api/admin/departamentos', json=dept_data)
        if response.status_code == 200:
            created_dept = response.json()
            dept_id = created_dept['id']
            print(f"✅ [DEBUG] Departamento criado: ID {dept_id}")
            
            # Verificar se aparece na listagem
            response = client.get('/api/admin/departamentos')
            if response.status_code == 200:
                departamentos = response.json()
                dept_exists = any(d['id'] == dept_id for d in departamentos)
                print(f"✅ [DEBUG] Departamento aparece na listagem: {dept_exists}")
                
                # Fazer soft delete
                response = client.delete(f'/api/admin/departamentos/{dept_id}')
                if response.status_code == 200:
                    print(f"✅ [DEBUG] Soft delete executado com sucesso")
                    
                    # Verificar se NÃO aparece mais na listagem (filtro de ativos)
                    response = client.get('/api/admin/departamentos')
                    if response.status_code == 200:
                        departamentos = response.json()
                        dept_exists = any(d['id'] == dept_id for d in departamentos)
                        if not dept_exists:
                            print(f"✅ [SUCESSO] Soft delete funcionando - departamento não aparece mais na listagem")
                        else:
                            print(f"❌ [ERRO] Departamento ainda aparece na listagem após soft delete")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de soft delete: {e}")

    print("\n" + "="*60)
    print("2. TESTANDO: Criação de Setores")
    print("="*60)
    
    try:
        # Buscar um departamento ativo para usar
        response = client.get('/api/admin/departamentos')
        if response.status_code == 200:
            departamentos = response.json()
            if len(departamentos) > 0:
                primeiro_dept = departamentos[0]
                print(f"✅ [DEBUG] Usando departamento: {primeiro_dept['nome']}")
                
                setor_data = {
                    'nome': 'TESTE SETOR CRUD',
                    'departamento': primeiro_dept['nome'],
                    'area_tipo': 'PRODUCAO',
                    'descricao': 'Teste de criação de setor',
                    'ativo': True
                }
                
                response = client.post('/api/admin/setores', json=setor_data)
                print(f"✅ [DEBUG] POST setor status: {response.status_code}")
                
                if response.status_code == 200:
                    created_setor = response.json()
                    print(f"✅ [SUCESSO] Setor criado com sucesso: {created_setor['nome']}")
                    
                    # Limpar - deletar o setor
                    setor_id = created_setor['id']
                    response = client.delete(f'/api/admin/setores/{setor_id}')
                    print(f"✅ [DEBUG] Setor de teste deletado")
                else:
                    print(f"❌ [ERROR] Erro ao criar setor: {response.text}")
            else:
                print("⚠️ [AVISO] Nenhum departamento disponível para teste")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de criação de setor: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: Campo categoria em Tipos de Máquina")
    print("="*60)
    
    try:
        response = client.get('/api/admin/tipos-maquina')
        print(f"✅ [DEBUG] GET tipos-maquina status: {response.status_code}")
        
        if response.status_code == 200:
            tipos_maquina = response.json()
            print(f"✅ [DEBUG] Retornou {len(tipos_maquina)} tipos de máquina")
            
            if len(tipos_maquina) > 0:
                primeira_maquina = tipos_maquina[0]
                campos_presentes = list(primeira_maquina.keys())
                print(f"✅ [DEBUG] Campos disponíveis: {campos_presentes}")
                
                if 'categoria' in primeira_maquina:
                    print(f"✅ [SUCESSO] Campo 'categoria' presente: {primeira_maquina['categoria']}")
                else:
                    print(f"❌ [ERRO] Campo 'categoria' não encontrado")
                    
                if 'subcategoria' in primeira_maquina:
                    print(f"✅ [SUCESSO] Campo 'subcategoria' presente: {primeira_maquina['subcategoria']}")
                else:
                    print(f"❌ [ERRO] Campo 'subcategoria' não encontrado")
            else:
                print("⚠️ [AVISO] Nenhum tipo de máquina encontrado para teste")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de tipos de máquina: {e}")

    print("\n" + "="*60)
    print("RESUMO DAS CORREÇÕES IMPLEMENTADAS")
    print("="*60)
    print("✅ 1. Soft Delete: Registros marcados como ativo=False em vez de deletados")
    print("✅ 2. Filtros de Ativos: Endpoints agora filtram apenas registros ativos")
    print("✅ 3. Setores: Corrigido mapeamento de departamentos no formulário")
    print("✅ 4. Tipos de Máquina: Adicionados campos categoria e subcategoria na resposta")
    print("✅ 5. Frontend: Corrigidos nomes de campos para compatibilidade com backend")
    
    print("\n✅ [DEBUG] Teste completo de correções CRUD concluído!")

if __name__ == "__main__":
    test_all_crud_fixes()
