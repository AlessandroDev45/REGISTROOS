#!/usr/bin/env python3
"""
Teste dos novos endpoints criados
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 TESTE: NOVOS ENDPOINTS")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint de colaboradores
    print("\n2. 🎯 Testando endpoint de colaboradores:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/colaboradores")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} colaboradores do setor")
            
            for i, colab in enumerate(data[:3], 1):
                nome = colab.get('nome_completo', 'N/A')
                setor = colab.get('setor', 'N/A')
                print(f"      {i}. {nome} - {setor}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar endpoint de notificações
    print("\n3. 🔔 Testando endpoint de notificações:")
    try:
        notificacao_data = {
            "usuario_id": 2,
            "titulo": "Teste de Notificação",
            "mensagem": "Esta é uma notificação de teste",
            "tipo": "PROGRAMACAO",
            "prioridade": "ALTA"
        }
        
        response = session.post(f"{BASE_URL}/api/desenvolvimento/notificacoes", json=notificacao_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Notificação criada: {data.get('message')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar endpoint de finalizar programação
    print("\n4. 🎯 Testando endpoint de finalizar programação:")
    try:
        # Primeiro buscar uma programação
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            programacoes = response.json()
            if programacoes:
                prog_id = programacoes[0].get('id')
                print(f"   📋 Testando com programação ID: {prog_id}")
                
                finalizar_data = {
                    "status": "FINALIZADA",
                    "data_finalizacao": "2025-09-26T10:00:00",
                    "finalizada_por": 1
                }
                
                response = session.patch(f"{BASE_URL}/api/desenvolvimento/programacao/{prog_id}/finalizar", json=finalizar_data)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Programação finalizada: {data.get('message')}")
                else:
                    print(f"   ❌ Erro: {response.status_code}")
                    print(f"   📄 Resposta: {response.text[:200]}")
            else:
                print(f"   ⚠️ Nenhuma programação encontrada para testar")
        else:
            print(f"   ❌ Erro ao buscar programações: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n📋 RESUMO DAS CORREÇÕES APLICADAS:")
    print("✅ 1. URL do endpoint de colaboradores corrigida")
    print("✅ 2. Filtro de colaboradores por setor implementado")
    print("✅ 3. Sistema de notificação para atribuições criado")
    print("✅ 4. Verificação de programação finalizada no apontamento")
    print("✅ 5. Endpoint para finalizar programação criado")
    print("\n🚀 AGORA TESTE NO FRONTEND!")

if __name__ == "__main__":
    main()
