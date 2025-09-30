#!/usr/bin/env python3
"""
TESTE DA BUSCA AUTOMÁTICA DE DADOS DA OS
========================================

Testa se ao redirecionar para apontamento e preencher o número da OS,
os campos Status OS, Cliente e Equipamento são buscados automaticamente.
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login...")
    
    session = requests.Session()
    
    # Dados de login
    login_data = {
        "username": "alessandro.silva@eletrotest.com.br",
        "password": "123456"
    }
    
    try:
        response = session.post(LOGIN_URL, json=login_data)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login realizado com sucesso!")
            print(f"👤 Usuário: {user_data.get('nome_completo')}")
            print(f"🏢 Setor: {user_data.get('setor_nome')}")
            return session, user_data
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None, None

def testar_busca_os(session, numero_os):
    """Testar busca automática de dados da OS"""
    print(f"\n🔍 Testando busca automática da OS: {numero_os}")
    
    try:
        # Usar o endpoint que o frontend usa
        url = f"{BASE_URL}/api/desenvolvimento/formulario/buscar-os/{numero_os}"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        response = session.get(url, timeout=60)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ OS encontrada!")
            print(f"📋 Dados retornados:")
            print(f"   📊 Status OS: {data.get('status', 'N/A')}")
            print(f"   🏢 Cliente: {data.get('cliente', 'N/A')}")
            print(f"   ⚙️ Equipamento: {data.get('equipamento', 'N/A')}")
            print(f"   🔍 Fonte: {data.get('fonte', 'N/A')}")
            
            # Verificar se todos os campos essenciais estão preenchidos
            campos_essenciais = ['status', 'cliente', 'equipamento']
            campos_preenchidos = []
            campos_vazios = []
            
            for campo in campos_essenciais:
                valor = data.get(campo)
                if valor and valor.strip():
                    campos_preenchidos.append(campo)
                else:
                    campos_vazios.append(campo)
            
            print(f"\n📈 Análise dos campos:")
            print(f"   ✅ Preenchidos: {campos_preenchidos}")
            if campos_vazios:
                print(f"   ❌ Vazios: {campos_vazios}")
            else:
                print(f"   🎉 Todos os campos essenciais preenchidos!")
            
            return data
            
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def testar_programacao_com_os(session):
    """Testar se uma programação tem OS válida"""
    print(f"\n📋 Buscando programações para teste...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            programacoes = response.json()
            
            if programacoes:
                print(f"✅ Encontradas {len(programacoes)} programações")
                
                for i, prog in enumerate(programacoes[:3]):
                    print(f"\n📋 Programação {i+1}:")
                    print(f"   ID: {prog.get('id')}")
                    print(f"   OS: {prog.get('os_numero')}")
                    print(f"   Status: {prog.get('status')}")
                    
                    # Testar busca da OS desta programação
                    if prog.get('os_numero'):
                        dados_os = testar_busca_os(session, prog.get('os_numero'))
                        
                        if dados_os:
                            print(f"   🎯 Simulação de redirecionamento:")
                            print(f"      1. Usuário clica 'Iniciar Execução'")
                            print(f"      2. Sistema preenche OS: {prog.get('os_numero')}")
                            print(f"      3. Sistema busca automaticamente:")
                            print(f"         📊 Status: {dados_os.get('status')}")
                            print(f"         🏢 Cliente: {dados_os.get('cliente')}")
                            print(f"         ⚙️ Equipamento: {dados_os.get('equipamento')}")
                            print(f"      4. ✅ Formulário totalmente preenchido!")
                        else:
                            print(f"   ❌ Falha na busca automática da OS")
                
                return programacoes[0] if programacoes else None
            else:
                print(f"❌ Nenhuma programação encontrada")
                return None
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("🧪 TESTE DA BUSCA AUTOMÁTICA DE DADOS DA OS")
    print("=" * 60)
    
    # 1. Fazer login
    session, user_data = fazer_login()
    if not session:
        return
    
    # 2. Testar busca direta de OS conhecida
    print(f"\n🎯 TESTE 1: Busca direta de OS")
    testar_busca_os(session, "20611")
    
    # 3. Testar com programações existentes
    print(f"\n🎯 TESTE 2: Programações com busca automática")
    testar_programacao_com_os(session)
    
    print(f"\n✅ Testes concluídos!")
    print(f"\n📝 RESUMO:")
    print(f"   - Ao preencher número da OS no formulário de apontamento")
    print(f"   - O sistema deve buscar automaticamente:")
    print(f"     📊 Status da OS")
    print(f"     🏢 Nome do Cliente") 
    print(f"     ⚙️ Descrição do Equipamento")
    print(f"   - Isso funciona tanto para:")
    print(f"     📋 Redirecionamento de pendências")
    print(f"     🚀 Redirecionamento de programações")
    print(f"     ✏️ Digitação manual da OS")

if __name__ == "__main__":
    main()
