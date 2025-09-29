#!/usr/bin/env python3
"""
Teste específico para simular exatamente o que o frontend de atividades faz
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

def test_atividade_frontend_simulation():
    """Simular exatamente o que o frontend de atividades faz"""
    
    print("🎯 [DEBUG] Simulando comportamento do frontend de atividades...")
    
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
    print("SIMULANDO: TipoAtividadeForm useEffect")
    print("="*60)
    
    try:
        print("📡 [FRONTEND] Fazendo Promise.all([departamentos, setores, categorias])...")
        
        # 1. Buscar departamentos (como o frontend faz)
        print("📡 [FRONTEND] Chamando departamentoService.getDepartamentos()...")
        dept_response = client.get('/api/admin/departamentos')
        print(f"📡 [FRONTEND] Resposta departamentos: {dept_response.status_code}")
        
        if dept_response.status_code == 200:
            departamentos = dept_response.json()
            print(f"📡 [FRONTEND] Departamentos recebidos: {len(departamentos)}")
            for dept in departamentos:
                print(f"   - ID: {dept['id']}, Nome: {dept['nome_tipo']}")
        else:
            print(f"❌ [FRONTEND] Erro departamentos: {dept_response.text}")
            return

        # 2. Buscar setores (como o frontend faz)
        print("\n📡 [FRONTEND] Chamando setorService.getSetores()...")
        setor_response = client.get('/api/admin/setores')  # CORRIGIDO
        print(f"📡 [FRONTEND] Resposta setores: {setor_response.status_code}")
        
        if setor_response.status_code == 200:
            setores = setor_response.json()
            print(f"📡 [FRONTEND] Setores recebidos: {len(setores)}")
            for setor in setores[:5]:  # Mostrar só os primeiros 5
                print(f"   - ID: {setor['id']}, Nome: {setor['nome']}, Dept: {setor['departamento']}")
        else:
            print(f"❌ [FRONTEND] Erro setores: {setor_response.text}")
            return

        print("\n" + "="*60)
        print("SIMULANDO: Filtro de setores por departamento")
        print("="*60)
        
        # 3. Simular filtro quando usuário seleciona "MOTORES"
        departamento_selecionado = "MOTORES"
        print(f"🎯 [FRONTEND] Usuário selecionou departamento: '{departamento_selecionado}'")
        
        setores_filtrados = []
        for setor in setores:
            setor_dept = setor.get('departamento', '').strip() if setor.get('departamento') else ''
            form_dept = departamento_selecionado.strip()
            
            print(f"🔍 [FRONTEND] Comparando setor '{setor['nome']}': '{setor_dept}' == '{form_dept}' ? {setor_dept == form_dept}")
            
            if setor_dept == form_dept:
                setores_filtrados.append(setor)
        
        print(f"\n🎯 [RESULTADO] Setores filtrados para '{departamento_selecionado}': {len(setores_filtrados)}")
        for setor in setores_filtrados:
            print(f"   ✅ {setor['nome']} (Dept: {setor['departamento']})")

        print("\n" + "="*60)
        print("DIAGNÓSTICO FINAL")
        print("="*60)
        
        if len(departamentos) == 0:
            print("❌ [PROBLEMA] Nenhum departamento encontrado")
        elif len(setores) == 0:
            print("❌ [PROBLEMA] Nenhum setor encontrado")
        elif len(setores_filtrados) == 0:
            print("❌ [PROBLEMA] Filtro não encontrou setores para o departamento selecionado")
            print("🔍 [DICA] Verifique se os nomes dos departamentos nos setores estão corretos")
        else:
            print("✅ [SUCESSO] Tudo funcionando corretamente!")
            print(f"   - {len(departamentos)} departamentos disponíveis")
            print(f"   - {len(setores)} setores disponíveis")
            print(f"   - {len(setores_filtrados)} setores para '{departamento_selecionado}'")
                
    except Exception as e:
        print(f"❌ [ERROR] Erro na simulação: {e}")

    print("\n✅ [DEBUG] Simulação do frontend concluída!")

if __name__ == "__main__":
    test_atividade_frontend_simulation()
