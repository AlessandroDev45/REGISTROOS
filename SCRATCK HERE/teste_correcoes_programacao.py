#!/usr/bin/env python3
"""
Teste das correções implementadas para programação
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Fazer login e retornar sessão autenticada"""
    session = requests.Session()

    login_data = {
        "username": "admin@admin.com",
        "password": "admin123"
    }

    response = session.post(f"{BASE_URL}/api/auth/token", data=login_data)
    if response.status_code == 200:
        print("✅ Login realizado com sucesso")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def test_departamentos_setores(session):
    """Testar busca de departamentos e setores"""

    print("\n" + "="*50)
    print("TESTE: Busca de Departamentos")
    print("="*50)

    response = session.get(f"{BASE_URL}/api/catalogs/departamentos")
    if response.status_code == 200:
        departamentos = response.json()
        print(f"✅ Departamentos encontrados: {len(departamentos)}")
        for dept in departamentos[:3]:
            print(f"  - {dept.get('nome_tipo', 'N/A')}")
    else:
        print(f"❌ Erro ao buscar departamentos: {response.status_code}")

    print("\n" + "="*50)
    print("TESTE: Busca de Setores")
    print("="*50)

    response = session.get(f"{BASE_URL}/api/catalogs/setores")
    if response.status_code == 200:
        setores = response.json()
        print(f"✅ Setores encontrados: {len(setores)}")
        for setor in setores[:3]:
            print(f"  - {setor.get('nome', 'N/A')} (Dept: {setor.get('departamento_nome', 'N/A')})")
    else:
        print(f"❌ Erro ao buscar setores: {response.status_code}")

def test_supervisores_producao(session):
    """Testar busca de supervisores da produção"""

    print("\n" + "="*50)
    print("TESTE: Supervisores da Produção")
    print("="*50)

    response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
    if response.status_code == 200:
        data = response.json()
        usuarios = data.get("usuarios", [])
        print(f"✅ Supervisores da produção encontrados: {len(usuarios)}")
        for user in usuarios[:3]:
            print(f"  - {user.get('nome_completo', 'N/A')} (Setor: {user.get('setor_nome', 'N/A')})")
    else:
        print(f"❌ Erro ao buscar supervisores: {response.status_code}")

def test_programacoes_setor(session):
    """Testar busca de programações do setor"""

    print("\n" + "="*50)
    print("TESTE: Programações do Setor")
    print("="*50)

    # Testar endpoint de desenvolvimento
    response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
    if response.status_code == 200:
        programacoes = response.json()
        print(f"✅ Programações encontradas: {len(programacoes)}")
        for prog in programacoes[:2]:
            print(f"  - OS {prog.get('numero', 'N/A')} - Status: {prog.get('status', 'N/A')}")
    else:
        print(f"❌ Erro ao buscar programações: {response.status_code}")
    
    # Testar filtro por status
    response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao?status=PROGRAMADA")
    if response.status_code == 200:
        programacoes_programadas = response.json()
        print(f"✅ Programações PROGRAMADAS: {len(programacoes_programadas)}")
    else:
        print(f"❌ Erro ao buscar programações programadas: {response.status_code}")

def test_criar_programacao(session):
    """Testar criação de programação"""

    print("\n" + "="*50)
    print("TESTE: Criação de Programação")
    print("="*50)

    # Primeiro buscar uma OS para usar
    response = session.get(f"{BASE_URL}/api/pcp/ordens-servico")
    if response.status_code == 200:
        ordens = response.json()
        if ordens:
            os_id = ordens[0].get("id")
            print(f"✅ OS encontrada para teste: {os_id}")
            
            # Buscar dados do formulário
            response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
            if response.status_code == 200:
                form_data = response.json()
                setores = form_data.get("setores", [])
                usuarios = form_data.get("usuarios", [])
                
                if setores and usuarios:
                    setor_id = setores[0].get("id")
                    responsavel_id = usuarios[0].get("id")
                    
                    programacao_data = {
                        "id_ordem_servico": os_id,
                        "id_setor": setor_id,
                        "responsavel_id": responsavel_id,
                        "inicio_previsto": "2025-09-23T08:00:00",
                        "fim_previsto": "2025-09-23T17:00:00",
                        "observacoes": "Teste de programação automática",
                        "status": "PROGRAMADA"
                    }
                    
                    response = session.post(
                        f"{BASE_URL}/api/pcp/programacoes",
                        json=programacao_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Programação criada com sucesso: ID {result.get('id')}")
                        return result.get('id')
                    else:
                        print(f"❌ Erro ao criar programação: {response.status_code}")
                        print(f"Resposta: {response.text}")
                else:
                    print("❌ Não há setores ou usuários disponíveis")
            else:
                print(f"❌ Erro ao buscar dados do formulário: {response.status_code}")
        else:
            print("❌ Nenhuma OS encontrada")
    else:
        print(f"❌ Erro ao buscar ordens de serviço: {response.status_code}")
    
    return None

def main():
    print("🔧 TESTE DAS CORREÇÕES DE PROGRAMAÇÃO")
    print("="*60)
    
    # 1. Login
    session = test_login()
    if not session:
        return

    # 2. Testar departamentos e setores
    test_departamentos_setores(session)

    # 3. Testar supervisores da produção
    test_supervisores_producao(session)

    # 4. Testar programações do setor
    test_programacoes_setor(session)

    # 5. Testar criação de programação
    programacao_id = test_criar_programacao(session)
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    main()
