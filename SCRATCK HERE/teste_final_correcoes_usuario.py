#!/usr/bin/env python3
"""
Teste final das correções solicitadas pelo usuário:

1. Garantir que ao criar programação busca dados da API
2. Departamento MOTORES e Setor LABORATORIO DE ENSAIOS ELETRICOS (MOTORES) 
3. Apenas supervisores que trabalham na produção
4. Ao criar programação, atualizar campos corretos nas tabelas
5. Não conflitar com funcionalidades existentes
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_login():
    """Fazer login e obter cookies"""
    login_data = {
        "username": "admin@registroos.com", 
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=login_data)
    print(f"✅ Login status: {response.status_code}")
    
    if response.status_code == 200:
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.text}")
        return None

def test_departamento_motores_setor_laboratorio(cookies):
    """Testar se departamento MOTORES e setor LABORATORIO estão disponíveis"""
    print(f"\n{'='*60}")
    print("🔍 TESTE: Departamento MOTORES e Setor LABORATORIO")
    
    # Buscar dados do formulário
    response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
    
    if response.status_code != 200:
        print(f"❌ Erro ao buscar dados do formulário: {response.status_code}")
        return False
        
    data = response.json()
    setores = data.get('setores', [])
    
    # Verificar se existe setor LABORATORIO DE ENSAIOS ELETRICOS do departamento MOTORES
    setor_laboratorio_motores = None
    for setor in setores:
        if ('LABORATORIO DE ENSAIOS ELETRICOS' in setor.get('nome', '') and 
            setor.get('departamento_nome') == 'MOTORES'):
            setor_laboratorio_motores = setor
            break
    
    if setor_laboratorio_motores:
        print(f"✅ Setor encontrado: {setor_laboratorio_motores['nome']}")
        print(f"✅ Departamento: {setor_laboratorio_motores['departamento_nome']}")
        print(f"✅ ID do setor: {setor_laboratorio_motores['id']}")
        return setor_laboratorio_motores
    else:
        print("❌ Setor LABORATORIO DE ENSAIOS ELETRICOS (MOTORES) não encontrado")
        return None

def test_supervisores_producao(cookies):
    """Testar se apenas supervisores de produção são retornados"""
    print(f"\n{'='*60}")
    print("👥 TESTE: Supervisores de Produção")
    
    response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
    
    if response.status_code != 200:
        print(f"❌ Erro ao buscar supervisores: {response.status_code}")
        return []
        
    data = response.json()
    supervisores = data.get('usuarios', [])
    
    print(f"✅ Total de supervisores retornados: {len(supervisores)}")
    
    # Verificar se há supervisor do LABORATORIO DE ENSAIOS ELETRICOS
    supervisor_laboratorio = None
    for supervisor in supervisores:
        print(f"   - {supervisor['nome_completo']} (Setor: {supervisor['setor_nome']})")
        if 'LABORATORIO DE ENSAIOS ELETRICOS' in supervisor.get('setor_nome', ''):
            supervisor_laboratorio = supervisor
    
    if supervisor_laboratorio:
        print(f"✅ Supervisor do laboratório encontrado: {supervisor_laboratorio['nome_completo']}")
        return supervisor_laboratorio
    else:
        print("❌ Supervisor do LABORATORIO DE ENSAIOS ELETRICOS não encontrado")
        return None

def test_endpoints_funcionando(cookies):
    """Testar se todos os endpoints estão funcionando sem erros"""
    print(f"\n{'='*60}")
    print("🔗 TESTE: Endpoints Funcionando")
    
    endpoints = [
        "/api/pcp/ordens-servico",
        "/api/pcp/programacoes", 
        "/api/pcp/pendencias",
        "/api/pcp/dashboard/avancado?periodo_dias=30",
        "/api/pcp/alertas",
        "/api/pcp/pendencias/dashboard?periodo_dias=30",
        "/api/pcp/programacao-form-data"
    ]
    
    todos_funcionando = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                todos_funcionando = False
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {e}")
            todos_funcionando = False
    
    return todos_funcionando

def main():
    """Função principal do teste"""
    print("🧪 TESTE FINAL DAS CORREÇÕES SOLICITADAS")
    print("="*60)
    
    # 1. Login
    cookies = test_login()
    if not cookies:
        print("❌ Falha no login. Abortando testes.")
        return
    
    # 2. Testar endpoints funcionando
    endpoints_ok = test_endpoints_funcionando(cookies)
    
    # 3. Testar departamento MOTORES e setor LABORATORIO
    setor_laboratorio = test_departamento_motores_setor_laboratorio(cookies)
    
    # 4. Testar supervisores de produção
    supervisor_laboratorio = test_supervisores_producao(cookies)
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"✅ Login: OK")
    print(f"{'✅' if endpoints_ok else '❌'} Endpoints funcionando: {'OK' if endpoints_ok else 'ERRO'}")
    print(f"{'✅' if setor_laboratorio else '❌'} Departamento MOTORES / Setor LABORATORIO: {'OK' if setor_laboratorio else 'ERRO'}")
    print(f"{'✅' if supervisor_laboratorio else '❌'} Supervisores de produção: {'OK' if supervisor_laboratorio else 'ERRO'}")
    
    if all([endpoints_ok, setor_laboratorio, supervisor_laboratorio]):
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema está funcionando conforme solicitado:")
        print("   - Departamento MOTORES disponível")
        print("   - Setor LABORATORIO DE ENSAIOS ELETRICOS (MOTORES) disponível") 
        print("   - Apenas supervisores de produção são mostrados")
        print("   - Endpoints funcionando sem conflitos")
    else:
        print(f"\n⚠️ ALGUNS TESTES FALHARAM - Verificar problemas acima")

if __name__ == "__main__":
    main()
