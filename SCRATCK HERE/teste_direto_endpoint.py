#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto do endpoint programacao-form-data
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
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return None

def test_endpoint_raw(cookies):
    """Testa o endpoint diretamente"""
    print("\n🔍 Testando endpoint /api/pcp/programacao-form-data diretamente...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON válido recebido")
                print(f"   📊 Tamanho da resposta: {len(response.text)} caracteres")
                
                # Mostrar estrutura da resposta
                print(f"   📋 Estrutura da resposta:")
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"      {key}: lista com {len(value)} itens")
                        if value and len(value) > 0:
                            print(f"         Primeiro item: {value[0]}")
                    else:
                        print(f"      {key}: {type(value).__name__} = {value}")
                
                # Salvar resposta completa
                with open("SCRATCK HERE/resposta_endpoint_programacao.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print("   ✅ Resposta salva em 'resposta_endpoint_programacao.json'")
                
                return data
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erro ao decodificar JSON: {e}")
                print(f"   📄 Resposta raw: {response.text[:500]}...")
                return None
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            return None
        
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return None

def test_other_endpoints(cookies):
    """Testa outros endpoints para comparação"""
    print("\n🔍 Testando outros endpoints para comparação...")
    
    endpoints = [
        "/api/pcp/programacoes",
        "/api/departamentos",
        "/api/setores",
        "/api/usuarios"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"   {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"      Lista com {len(data)} itens")
                    elif isinstance(data, dict):
                        print(f"      Objeto com {len(data)} chaves")
                    else:
                        print(f"      Tipo: {type(data).__name__}")
                except:
                    print(f"      Resposta não é JSON válido")
            else:
                print(f"      Erro: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   {endpoint}: Erro - {e}")

def main():
    """Função principal"""
    print("🧪 TESTE DIRETO DO ENDPOINT PROGRAMACAO-FORM-DATA")
    print("=" * 60)
    
    # 1. Login
    cookies = test_login()
    if not cookies:
        print("❌ Não foi possível fazer login. Abortando.")
        return
    
    # 2. Testar endpoint principal
    data = test_endpoint_raw(cookies)
    
    # 3. Testar outros endpoints
    test_other_endpoints(cookies)
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO:")
    
    if data:
        print("   ✅ Endpoint respondeu com dados")
        print(f"   📊 Departamentos: {len(data.get('departamentos', []))}")
        print(f"   📊 Setores: {len(data.get('setores', []))}")
        print(f"   📊 Usuários: {len(data.get('usuarios', []))}")
        print(f"   📊 Ordens de Serviço: {len(data.get('ordens_servico', []))}")
        
        if all(len(data.get(key, [])) == 0 for key in ['departamentos', 'setores', 'usuarios', 'ordens_servico']):
            print("\n❌ PROBLEMA: Todas as listas estão vazias")
            print("   Possíveis causas:")
            print("   1. Erro nas queries SQL")
            print("   2. Problema na conexão com o banco")
            print("   3. Dados não estão sendo retornados corretamente")
        else:
            print("\n✅ Alguns dados foram retornados")
    else:
        print("   ❌ Endpoint não respondeu ou retornou erro")
    
    print("\n🔍 PRÓXIMOS PASSOS:")
    print("   1. Verificar logs do backend")
    print("   2. Testar queries SQL diretamente")
    print("   3. Verificar se o endpoint está sendo executado corretamente")

if __name__ == "__main__":
    main()
