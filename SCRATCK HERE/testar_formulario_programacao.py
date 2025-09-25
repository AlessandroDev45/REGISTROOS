#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do formulário de programação do PCP
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_login():
    """Faz login e retorna cookies"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/token", data=login_data)
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            return response.cookies
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return None

def testar_programacao_form_data(cookies):
    """Testa o endpoint de dados do formulário de programação"""
    print("\n📋 Testando endpoint /api/pcp/programacao-form-data...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("   ✅ Dados do formulário recebidos:")
            print(f"      🏢 Departamentos: {len(data.get('departamentos', []))}")
            print(f"      🏭 Setores: {len(data.get('setores', []))}")
            print(f"      👥 Usuários: {len(data.get('usuarios', []))}")
            print(f"      📋 Ordens de Serviço: {len(data.get('ordens_servico', []))}")
            print(f"      📊 Status Opções: {len(data.get('status_opcoes', []))}")
            
            # Mostrar departamentos disponíveis
            departamentos = data.get('departamentos', [])
            if departamentos:
                print("\n      🏢 Departamentos disponíveis:")
                for dept in departamentos[:5]:  # Mostrar apenas os primeiros 5
                    print(f"         - ID: {dept.get('id')}, Nome: {dept.get('nome')}")
                if len(departamentos) > 5:
                    print(f"         ... e mais {len(departamentos) - 5} departamentos")
            
            # Mostrar setores disponíveis
            setores = data.get('setores', [])
            if setores:
                print("\n      🏭 Setores disponíveis:")
                for setor in setores[:5]:  # Mostrar apenas os primeiros 5
                    print(f"         - ID: {setor.get('id')}, Nome: {setor.get('nome')}, Dept: {setor.get('departamento_nome')}")
                if len(setores) > 5:
                    print(f"         ... e mais {len(setores) - 5} setores")
            
            # Mostrar usuários supervisores
            usuarios = data.get('usuarios', [])
            supervisores = [u for u in usuarios if u.get('privilege_level') == 'SUPERVISOR']
            if supervisores:
                print("\n      👥 Supervisores disponíveis:")
                for sup in supervisores[:5]:  # Mostrar apenas os primeiros 5
                    print(f"         - ID: {sup.get('id')}, Nome: {sup.get('nome_completo')}, Setor: {sup.get('setor')}")
                if len(supervisores) > 5:
                    print(f"         ... e mais {len(supervisores) - 5} supervisores")
            else:
                print("\n      ⚠️ Nenhum supervisor encontrado")
            
            # Verificar se há dados do departamento TESTE
            dept_teste = next((d for d in departamentos if d.get('nome') == 'TESTE'), None)
            if dept_teste:
                print(f"\n      ✅ Departamento TESTE encontrado: ID {dept_teste.get('id')}")
                
                # Buscar setores do departamento TESTE
                setores_teste = [s for s in setores if s.get('departamento_nome') == 'TESTE']
                if setores_teste:
                    print(f"         🏭 Setores do TESTE: {len(setores_teste)}")
                    for setor in setores_teste:
                        print(f"            - {setor.get('nome')} (ID: {setor.get('id')})")
                else:
                    print("         ⚠️ Nenhum setor encontrado para departamento TESTE")
            else:
                print("\n      ❌ Departamento TESTE não encontrado")
            
            return data
            
        else:
            print(f"   ❌ Erro: {response.text}")
            return None
        
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
        return None

def criar_programacao_teste(cookies, form_data):
    """Cria uma programação de teste usando o departamento TESTE"""
    print("\n📅 Criando programação de teste...")
    
    if not form_data:
        print("   ❌ Dados do formulário não disponíveis")
        return None
    
    # Buscar departamento TESTE
    departamentos = form_data.get('departamentos', [])
    dept_teste = next((d for d in departamentos if d.get('nome') == 'TESTE'), None)
    
    if not dept_teste:
        print("   ❌ Departamento TESTE não encontrado")
        return None
    
    # Buscar setor TESTES
    setores = form_data.get('setores', [])
    setor_testes = next((s for s in setores if s.get('nome') == 'TESTES'), None)
    
    if not setor_testes:
        print("   ❌ Setor TESTES não encontrado")
        return None
    
    # Buscar supervisor
    usuarios = form_data.get('usuarios', [])
    supervisor = next((u for u in usuarios if u.get('privilege_level') == 'SUPERVISOR'), None)
    
    # Buscar uma OS disponível
    ordens_servico = form_data.get('ordens_servico', [])
    if not ordens_servico:
        print("   ❌ Nenhuma ordem de serviço disponível")
        return None
    
    os_disponivel = ordens_servico[0]  # Usar a primeira OS disponível
    
    # Dados da programação
    programacao_data = {
        "id_ordem_servico": os_disponivel.get('id'),
        "inicio_previsto": "2025-01-20T08:00:00",
        "fim_previsto": "2025-01-20T17:00:00",
        "id_departamento": dept_teste.get('id'),
        "id_setor": setor_testes.get('id'),
        "responsavel_id": supervisor.get('id') if supervisor else None,
        "prioridade": "ALTA",
        "observacoes": "Programação de teste criada automaticamente para departamento TESTE",
        "status": "PROGRAMADA"
    }
    
    print(f"   📋 Dados da programação:")
    print(f"      OS: {os_disponivel.get('os_numero')} (ID: {os_disponivel.get('id')})")
    print(f"      Departamento: {dept_teste.get('nome')} (ID: {dept_teste.get('id')})")
    print(f"      Setor: {setor_testes.get('nome')} (ID: {setor_testes.get('id')})")
    print(f"      Supervisor: {supervisor.get('nome_completo') if supervisor else 'Nenhum'}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=programacao_data,
            cookies=cookies
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Programação criada com sucesso!")
            print(f"      ID: {result.get('id')}")
            return result
        else:
            print(f"   ❌ Erro ao criar programação: {response.text}")
            return None
        
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return None

def listar_programacoes_pcp(cookies):
    """Lista as programações do PCP"""
    print("\n📋 Listando programações do PCP...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacoes", cookies=cookies)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            programacoes = response.json()
            
            print(f"   ✅ {len(programacoes)} programações encontradas:")
            
            for prog in programacoes:
                print(f"\n      📅 Programação ID: {prog.get('id')}")
                print(f"         OS: {prog.get('os_numero')}")
                print(f"         Status: {prog.get('status')}")
                print(f"         Início: {prog.get('inicio_previsto')}")
                print(f"         Responsável: {prog.get('responsavel_nome')}")
                print(f"         Setor: {prog.get('setor_nome')}")
            
            return programacoes
            
        else:
            print(f"   ❌ Erro: {response.text}")
            return []
        
    except Exception as e:
        print(f"   ❌ Erro ao listar programações: {e}")
        return []

def main():
    """Função principal de teste"""
    print("🧪 TESTANDO FORMULÁRIO DE PROGRAMAÇÃO DO PCP")
    print("=" * 60)
    
    # 1. Login
    cookies = test_login()
    if not cookies:
        print("❌ Não foi possível fazer login. Abortando.")
        return
    
    # 2. Testar dados do formulário
    form_data = testar_programacao_form_data(cookies)
    
    # 3. Criar programação de teste
    if form_data:
        programacao_criada = criar_programacao_teste(cookies, form_data)
    else:
        programacao_criada = None
    
    # 4. Listar programações
    programacoes = listar_programacoes_pcp(cookies)
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO DOS TESTES:")
    print(f"   📋 Dados do formulário: {'✅ OK' if form_data else '❌ Erro'}")
    print(f"   📅 Programação criada: {'✅ OK' if programacao_criada else '❌ Erro'}")
    print(f"   📊 Programações listadas: {len(programacoes)}")
    
    if form_data:
        print("\n🌟 FORMULÁRIO DE PROGRAMAÇÃO:")
        print(f"   🏢 Departamentos disponíveis: {len(form_data.get('departamentos', []))}")
        print(f"   🏭 Setores disponíveis: {len(form_data.get('setores', []))}")
        print(f"   👥 Usuários disponíveis: {len(form_data.get('usuarios', []))}")
        print(f"   📋 Ordens de serviço: {len(form_data.get('ordens_servico', []))}")
        
        # Verificar se departamento TESTE está disponível
        departamentos = form_data.get('departamentos', [])
        dept_teste = next((d for d in departamentos if d.get('nome') == 'TESTE'), None)
        print(f"   ✅ Departamento TESTE: {'Disponível' if dept_teste else 'Não encontrado'}")
        
        if dept_teste:
            setores = form_data.get('setores', [])
            setores_teste = [s for s in setores if s.get('departamento_nome') == 'TESTE']
            print(f"   ✅ Setores do TESTE: {len(setores_teste)} encontrados")
    
    print("\n🎉 TESTE DO FORMULÁRIO DE PROGRAMAÇÃO CONCLUÍDO!")

if __name__ == "__main__":
    main()
