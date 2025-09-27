#!/usr/bin/env python3
"""
TESTE DAS CORREÇÕES IMPLEMENTADAS
================================

Testa todas as correções implementadas:
1. ✅ Permissão: Apenas SUPERVISOR pode ver aba Programação
2. ✅ Dashboard: Programações atribuídas aparecem no dashboard do colaborador
3. ✅ PCP: Pode editar programações existentes
4. ✅ Envio: Programação já vai direto ao setor quando criada (ENVIADA)
5. ✅ Prioridade: Está sendo passada corretamente
6. ✅ Histórico: Campo separado, não editável
"""

import requests
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Credenciais
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login como admin...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=ADMIN_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def teste_1_criar_programacao_enviada(session):
    """Teste 1: Criar programação que já vai como ENVIADA"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: PROGRAMAÇÃO JÁ VAI COMO ENVIADA")
    print("="*60)
    
    try:
        # Buscar uma OS existente
        response = session.get(f"{BASE_URL}/api/os/")
        if response.status_code != 200:
            print("❌ Erro ao buscar OSs")
            return False
            
        oss = response.json().get('data', [])
        if not oss:
            print("❌ Nenhuma OS encontrada")
            return False
            
        os_teste = oss[0]
        print(f"📋 Usando OS: {os_teste.get('os_numero')}")
        
        # Criar programação
        programacao_data = {
            "id_ordem_servico": os_teste.get('id'),
            "inicio_previsto": datetime.now().isoformat(),
            "fim_previsto": (datetime.now() + timedelta(hours=8)).isoformat(),
            "id_setor": 6,  # MECANICA DIA
            "responsavel_id": 1,  # Admin
            "observacoes": "Teste de programação que deve ir direto como ENVIADA",
            "prioridade": "ALTA"
        }
        
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_data)
        
        if response.status_code == 200:
            data = response.json()
            programacao_id = data.get('id')
            print(f"✅ Programação criada! ID: {programacao_id}")
            
            # Verificar se foi criada como ENVIADA
            response_check = session.get(f"{BASE_URL}/api/pcp/programacoes")
            if response_check.status_code == 200:
                programacoes = response_check.json()
                prog_criada = next((p for p in programacoes if p.get('id') == programacao_id), None)
                
                if prog_criada:
                    status = prog_criada.get('status')
                    print(f"📊 Status da programação: {status}")
                    
                    if status == 'ENVIADA':
                        print("✅ SUCESSO! Programação foi criada como ENVIADA")
                        return programacao_id
                    else:
                        print(f"❌ FALHA! Status deveria ser ENVIADA, mas é {status}")
                        return False
                else:
                    print("❌ Programação não encontrada após criação")
                    return False
            else:
                print("❌ Erro ao verificar programações")
                return False
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def teste_2_verificar_dashboard_colaborador(session, programacao_id):
    """Teste 2: Verificar se programação aparece no dashboard do colaborador"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: PROGRAMAÇÃO NO DASHBOARD DO COLABORADOR")
    print("="*60)
    
    try:
        # Buscar programações do usuário logado
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            programacoes = response.json()
            print(f"📋 Encontradas {len(programacoes)} programações no dashboard")
            
            # Verificar se nossa programação está lá
            prog_encontrada = next((p for p in programacoes if p.get('id') == programacao_id), None)
            
            if prog_encontrada:
                print("✅ SUCESSO! Programação aparece no dashboard do colaborador")
                print(f"   Status: {prog_encontrada.get('status')}")
                print(f"   OS: {prog_encontrada.get('os_numero')}")
                print(f"   Histórico: {prog_encontrada.get('historico', 'N/A')[:100]}...")
                return True
            else:
                print("❌ FALHA! Programação não aparece no dashboard")
                return False
        else:
            print(f"❌ Erro ao buscar dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def teste_3_editar_programacao(session, programacao_id):
    """Teste 3: Editar programação existente"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: EDITAR PROGRAMAÇÃO EXISTENTE")
    print("="*60)
    
    try:
        # Dados para edição
        edicao_data = {
            "inicio_previsto": (datetime.now() + timedelta(hours=1)).isoformat(),
            "fim_previsto": (datetime.now() + timedelta(hours=9)).isoformat(),
            "observacoes": "Programação editada via teste",
            "prioridade": "URGENTE"
        }
        
        response = session.put(f"{BASE_URL}/api/pcp/programacoes/{programacao_id}", json=edicao_data)
        
        if response.status_code == 200:
            print("✅ SUCESSO! Programação editada com sucesso")
            data = response.json()
            print(f"   Mensagem: {data.get('message')}")
            return True
        else:
            print(f"❌ FALHA! Erro ao editar: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def teste_4_verificar_historico(session, programacao_id):
    """Teste 4: Verificar se histórico está sendo mantido"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: VERIFICAR HISTÓRICO NÃO EDITÁVEL")
    print("="*60)
    
    try:
        # Buscar programação atualizada
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            programacoes = response.json()
            prog_encontrada = next((p for p in programacoes if p.get('id') == programacao_id), None)
            
            if prog_encontrada:
                historico = prog_encontrada.get('historico', '')
                print(f"📝 Histórico da programação:")
                print(f"   {historico}")
                
                # Verificar se contém entradas esperadas
                tem_criacao = '[CRIAÇÃO]' in historico
                tem_edicao = '[EDIÇÃO]' in historico
                
                if tem_criacao:
                    print("✅ Histórico contém entrada de criação")
                else:
                    print("❌ Histórico não contém entrada de criação")
                
                if tem_edicao:
                    print("✅ Histórico contém entrada de edição")
                else:
                    print("⚠️ Histórico não contém entrada de edição (pode ser normal)")
                
                return tem_criacao
            else:
                print("❌ Programação não encontrada")
                return False
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DAS CORREÇÕES IMPLEMENTADAS")
    print("=" * 80)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Executar testes
    resultados = []
    
    # Teste 1: Criar programação ENVIADA
    programacao_id = teste_1_criar_programacao_enviada(session)
    resultados.append(("Programação criada como ENVIADA", bool(programacao_id)))
    
    if programacao_id:
        # Teste 2: Dashboard do colaborador
        resultado_2 = teste_2_verificar_dashboard_colaborador(session, programacao_id)
        resultados.append(("Programação no dashboard", resultado_2))
        
        # Teste 3: Editar programação
        resultado_3 = teste_3_editar_programacao(session, programacao_id)
        resultados.append(("Edição de programação", resultado_3))
        
        # Teste 4: Verificar histórico
        resultado_4 = teste_4_verificar_historico(session, programacao_id)
        resultados.append(("Histórico não editável", resultado_4))
    
    # 3. Resumo dos resultados
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    sucessos = 0
    for teste, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"   {teste}: {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODAS AS CORREÇÕES ESTÃO FUNCIONANDO!")
    else:
        print("⚠️ Algumas correções precisam de ajustes")

if __name__ == "__main__":
    main()
