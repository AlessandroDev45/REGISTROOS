#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste dos formulários de atribuição de programação e resolução de pendência
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'

def fazer_login():
    """Faz login no sistema"""
    print("🔐 FAZENDO LOGIN...")
    
    try:
        login_data = {
            "username": "admin@registroos.com",
            "password": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/api/token", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            return response.cookies
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return None

def testar_endpoint_atribuicao_programacao(cookies):
    """Testa endpoint de atribuição de programação"""
    print("\n📋 TESTANDO ATRIBUIÇÃO DE PROGRAMAÇÃO...")
    
    try:
        # Primeiro, buscar dados necessários
        usuarios_resp = requests.get(f"{BASE_URL}/api/usuarios", cookies=cookies, timeout=5)
        setores_resp = requests.get(f"{BASE_URL}/api/setores", cookies=cookies, timeout=5)
        departamentos_resp = requests.get(f"{BASE_URL}/api/departamentos", cookies=cookies, timeout=5)
        
        if usuarios_resp.status_code != 200:
            print(f"   ❌ Erro ao buscar usuários: {usuarios_resp.status_code}")
            return False
            
        if setores_resp.status_code != 200:
            print(f"   ❌ Erro ao buscar setores: {setores_resp.status_code}")
            return False
            
        if departamentos_resp.status_code != 200:
            print(f"   ❌ Erro ao buscar departamentos: {departamentos_resp.status_code}")
            return False
        
        usuarios = usuarios_resp.json()
        setores = setores_resp.json()
        departamentos = departamentos_resp.json()
        
        print(f"   📊 Dados carregados: {len(usuarios)} usuários, {len(setores)} setores, {len(departamentos)} departamentos")
        
        # Encontrar um supervisor
        supervisor = None
        for usuario in usuarios:
            if usuario.get('privilege_level') in ['SUPERVISOR', 'GESTAO']:
                supervisor = usuario
                break
        
        if not supervisor:
            print("   ⚠️ Nenhum supervisor encontrado para teste")
            return False
        
        # Encontrar um setor
        if not setores:
            print("   ⚠️ Nenhum setor encontrado para teste")
            return False
            
        setor = setores[0]
        
        # Encontrar departamento do setor
        departamento_nome = setor.get('departamento', 'MOTORES')
        
        # Dados para atribuição
        data_inicio = datetime.now() + timedelta(days=1)
        data_fim = data_inicio + timedelta(hours=8)
        
        dados_atribuicao = {
            "responsavel_id": supervisor['id'],
            "setor_destino": setor['nome'],
            "departamento_destino": departamento_nome,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
            "prioridade": "NORMAL",
            "observacoes": "Teste de atribuição de programação via API"
        }
        
        print(f"   📝 Testando atribuição para: {supervisor['nome_completo']} - {setor['nome']}")
        
        # Testar criação de atribuição
        response = requests.post(
            f"{BASE_URL}/api/pcp/programacoes/atribuir",
            json=dados_atribuicao,
            cookies=cookies,
            timeout=10
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Atribuição criada com sucesso: ID {resultado.get('id')}")
            return True
        else:
            print(f"   ❌ Erro ao criar atribuição: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"      Detalhes: {error_detail}")
            except:
                print(f"      Resposta: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exceção no teste de atribuição: {e}")
        return False

def testar_endpoint_resolucao_pendencia(cookies):
    """Testa endpoint de resolução de pendência"""
    print("\n🔧 TESTANDO RESOLUÇÃO DE PENDÊNCIA...")
    
    try:
        # Buscar pendências existentes
        response = requests.get(f"{BASE_URL}/api/pendencias", cookies=cookies, timeout=5)
        
        if response.status_code != 200:
            print(f"   ❌ Erro ao buscar pendências: {response.status_code}")
            return False
        
        pendencias = response.json()
        print(f"   📊 Encontradas {len(pendencias)} pendências")
        
        # Encontrar uma pendência aberta
        pendencia_aberta = None
        for pendencia in pendencias:
            if pendencia.get('status') == 'ABERTA':
                pendencia_aberta = pendencia
                break
        
        if not pendencia_aberta:
            print("   ⚠️ Nenhuma pendência aberta encontrada para teste")
            print("   💡 Criando uma pendência de teste...")
            
            # Criar uma pendência de teste
            dados_pendencia = {
                "numero_os": "TEST999",
                "cliente": "Cliente Teste",
                "tipo_maquina": "Equipamento Teste",
                "descricao_maquina": "Equipamento para teste de resolução",
                "descricao_pendencia": "Pendência criada para teste de resolução via API",
                "prioridade": "NORMAL",
                "status": "ABERTA"
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/pendencias",
                json=dados_pendencia,
                cookies=cookies,
                timeout=10
            )
            
            if create_response.status_code == 200:
                pendencia_aberta = create_response.json()
                print(f"   ✅ Pendência de teste criada: ID {pendencia_aberta.get('id')}")
            else:
                print(f"   ❌ Erro ao criar pendência de teste: {create_response.status_code}")
                return False
        
        # Dados para resolução
        dados_resolucao = {
            "solucao_aplicada": "Solução aplicada via teste automatizado da API. Problema identificado e corrigido conforme procedimento padrão.",
            "observacoes_fechamento": "Teste de resolução de pendência realizado com sucesso",
            "tempo_resolucao_horas": 2.5,
            "materiais_utilizados": "Componentes de teste, ferramentas padrão",
            "custo_resolucao": 150.00,
            "responsavel_resolucao": "Técnico Teste API",
            "data_resolucao": datetime.now().isoformat(),
            "status": "FECHADA"
        }
        
        print(f"   🔧 Testando resolução da pendência ID: {pendencia_aberta['id']}")
        
        # Testar resolução
        response = requests.patch(
            f"{BASE_URL}/api/pendencias/{pendencia_aberta['id']}/resolver",
            json=dados_resolucao,
            cookies=cookies,
            timeout=10
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Pendência resolvida com sucesso")
            print(f"      Status: {resultado.get('status', 'N/A')}")
            return True
        else:
            print(f"   ❌ Erro ao resolver pendência: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"      Detalhes: {error_detail}")
            except:
                print(f"      Resposta: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exceção no teste de resolução: {e}")
        return False

def testar_endpoints_formularios(cookies):
    """Testa endpoints relacionados aos formulários"""
    print("\n📋 TESTANDO ENDPOINTS DOS FORMULÁRIOS...")
    
    endpoints_teste = [
        ("/api/pcp/programacao-form-data", "Dados do Formulário PCP"),
        ("/api/usuarios", "Lista de Usuários"),
        ("/api/setores", "Lista de Setores"),
        ("/api/departamentos", "Lista de Departamentos"),
        ("/api/pendencias", "Lista de Pendências")
    ]
    
    resultados = {}
    
    for endpoint, nome in endpoints_teste:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {nome}: {len(data)} registros")
                elif isinstance(data, dict):
                    print(f"   ✅ {nome}: Dados carregados")
                else:
                    print(f"   ✅ {nome}: OK")
                resultados[nome] = True
            else:
                print(f"   ❌ {nome}: Erro {response.status_code}")
                resultados[nome] = False
                
        except Exception as e:
            print(f"   ❌ {nome}: Exceção - {str(e)[:30]}...")
            resultados[nome] = False
    
    return resultados

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DOS FORMULÁRIOS")
    print("=" * 50)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        print("❌ Falha no login - abortando testes")
        return False
    
    # Testar endpoints dos formulários
    resultados_endpoints = testar_endpoints_formularios(cookies)
    
    # Testar atribuição de programação
    sucesso_atribuicao = testar_endpoint_atribuicao_programacao(cookies)
    
    # Testar resolução de pendência
    sucesso_resolucao = testar_endpoint_resolucao_pendencia(cookies)
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    total_endpoints = len(resultados_endpoints)
    endpoints_ok = sum(1 for r in resultados_endpoints.values() if r)
    
    print(f"📋 Endpoints dos formulários: {endpoints_ok}/{total_endpoints}")
    print(f"📝 Atribuição de programação: {'✅ OK' if sucesso_atribuicao else '❌ ERRO'}")
    print(f"🔧 Resolução de pendência: {'✅ OK' if sucesso_resolucao else '❌ ERRO'}")
    
    sucesso_geral = (endpoints_ok >= total_endpoints * 0.8) and sucesso_atribuicao and sucesso_resolucao
    
    if sucesso_geral:
        print("\n🎉 TODOS OS FORMULÁRIOS FUNCIONANDO!")
        print("   ✅ Atribuição de programação implementada")
        print("   ✅ Resolução de pendência implementada")
        print("   ✅ APIs de suporte funcionando")
    else:
        print("\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS")
        if not sucesso_atribuicao:
            print("   🔧 Verificar implementação de atribuição de programação")
        if not sucesso_resolucao:
            print("   🔧 Verificar implementação de resolução de pendência")
        if endpoints_ok < total_endpoints * 0.8:
            print("   🔧 Verificar endpoints de suporte aos formulários")
    
    return sucesso_geral

if __name__ == "__main__":
    main()
