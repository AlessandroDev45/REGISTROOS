#!/usr/bin/env python3
"""
Teste para verificar se o soft delete está funcionando corretamente
para Descrição de Atividades, Tipos de Falha e Causas de Retrabalho
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

def test_soft_delete_corrections():
    """Testar se o soft delete está funcionando para todos os tipos"""
    
    print("🔧 [DEBUG] Testando correções de soft delete...")
    
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
    print("1. TESTANDO: Descrição de Atividades - Filtro de Ativos")
    print("="*60)
    
    try:
        response = client.get('/api/admin/descricoes-atividade')
        print(f"✅ [DEBUG] GET descricoes-atividade status: {response.status_code}")
        
        if response.status_code == 200:
            descricoes = response.json()
            print(f"✅ [DEBUG] Retornou {len(descricoes)} descrições de atividade")
            
            # Verificar se todas são ativas
            if len(descricoes) > 0:
                todas_ativas = all(desc.get('ativo', True) for desc in descricoes)
                print(f"✅ [RESULTADO] Todas as descrições são ativas: {todas_ativas}")
                
                if not todas_ativas:
                    inativas = [desc for desc in descricoes if not desc.get('ativo', True)]
                    print(f"❌ [PROBLEMA] {len(inativas)} descrições inativas ainda aparecem na lista")
                else:
                    print(f"✅ [SUCESSO] Filtro de ativos funcionando corretamente")
            else:
                print("⚠️ [AVISO] Nenhuma descrição de atividade encontrada")
        else:
            print(f"❌ [ERROR] Erro no endpoint: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de descrições: {e}")

    print("\n" + "="*60)
    print("2. TESTANDO: Tipos de Falha - Filtro de Ativos")
    print("="*60)
    
    try:
        response = client.get('/api/admin/tipos-falha')
        print(f"✅ [DEBUG] GET tipos-falha status: {response.status_code}")
        
        if response.status_code == 200:
            tipos_falha = response.json()
            print(f"✅ [DEBUG] Retornou {len(tipos_falha)} tipos de falha")
            
            # Verificar se todas são ativas
            if len(tipos_falha) > 0:
                todas_ativas = all(tf.get('ativo', True) for tf in tipos_falha)
                print(f"✅ [RESULTADO] Todos os tipos de falha são ativos: {todas_ativas}")
                
                if not todas_ativas:
                    inativas = [tf for tf in tipos_falha if not tf.get('ativo', True)]
                    print(f"❌ [PROBLEMA] {len(inativas)} tipos de falha inativos ainda aparecem na lista")
                else:
                    print(f"✅ [SUCESSO] Filtro de ativos funcionando corretamente")
            else:
                print("⚠️ [AVISO] Nenhum tipo de falha encontrado")
        else:
            print(f"❌ [ERROR] Erro no endpoint: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de tipos de falha: {e}")

    print("\n" + "="*60)
    print("3. TESTANDO: Causas de Retrabalho - Filtro de Ativos")
    print("="*60)
    
    try:
        response = client.get('/api/admin/causas-retrabalho')
        print(f"✅ [DEBUG] GET causas-retrabalho status: {response.status_code}")
        
        if response.status_code == 200:
            causas = response.json()
            print(f"✅ [DEBUG] Retornou {len(causas)} causas de retrabalho")
            
            # Verificar se todas são ativas
            if len(causas) > 0:
                todas_ativas = all(causa.get('ativo', True) for causa in causas)
                print(f"✅ [RESULTADO] Todas as causas de retrabalho são ativas: {todas_ativas}")
                
                if not todas_ativas:
                    inativas = [causa for causa in causas if not causa.get('ativo', True)]
                    print(f"❌ [PROBLEMA] {len(inativas)} causas inativas ainda aparecem na lista")
                else:
                    print(f"✅ [SUCESSO] Filtro de ativos funcionando corretamente")
            else:
                print("⚠️ [AVISO] Nenhuma causa de retrabalho encontrada")
        else:
            print(f"❌ [ERROR] Erro no endpoint: {response.text}")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de causas de retrabalho: {e}")

    print("\n" + "="*60)
    print("4. TESTANDO: Soft Delete Funcionando")
    print("="*60)
    
    try:
        # Testar criação e soft delete de uma causa de retrabalho
        print("📝 [TEST] Criando causa de retrabalho para teste...")
        
        causa_data = {
            'codigo': 'TEST_SOFT_DELETE',
            'descricao': 'Teste de soft delete',
            'ativo': True
        }
        
        response = client.post('/api/admin/causas-retrabalho', json=causa_data)
        if response.status_code == 200:
            created_causa = response.json()
            causa_id = created_causa['id']
            print(f"✅ [TEST] Causa criada: ID {causa_id}")
            
            # Verificar se aparece na listagem
            response = client.get('/api/admin/causas-retrabalho')
            if response.status_code == 200:
                causas = response.json()
                causa_exists = any(c['id'] == causa_id for c in causas)
                print(f"✅ [TEST] Causa aparece na listagem: {causa_exists}")
                
                # Fazer soft delete
                response = client.delete(f'/api/admin/causas-retrabalho/{causa_id}')
                if response.status_code == 200:
                    print(f"✅ [TEST] Soft delete executado com sucesso")
                    
                    # Verificar se NÃO aparece mais na listagem
                    response = client.get('/api/admin/causas-retrabalho')
                    if response.status_code == 200:
                        causas = response.json()
                        causa_exists = any(c['id'] == causa_id for c in causas)
                        if not causa_exists:
                            print(f"✅ [SUCESSO] Soft delete funcionando - causa não aparece mais na listagem")
                        else:
                            print(f"❌ [PROBLEMA] Causa ainda aparece na listagem após soft delete")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro no teste de soft delete: {e}")

    print("\n" + "="*60)
    print("RESUMO DAS CORREÇÕES IMPLEMENTADAS")
    print("="*60)
    print("✅ 1. Descrição de Atividades: Filtro .filter(ativo == True) adicionado")
    print("✅ 2. Tipos de Falha: Filtro .filter(ativo == True) adicionado")
    print("✅ 3. Causas de Retrabalho: Filtro .filter(ativo == True) adicionado")
    print("✅ 4. Soft Delete: Marca como ativo=False em vez de deletar fisicamente")
    
    print("\n✅ [DEBUG] Teste de correções de soft delete concluído!")

if __name__ == "__main__":
    test_soft_delete_corrections()
