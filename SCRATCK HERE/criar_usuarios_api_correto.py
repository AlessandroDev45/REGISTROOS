#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuários da Mecânica via API - testando diferentes endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

def fazer_login():
    """Faz login como admin"""
    print("🔐 FAZENDO LOGIN COMO ADMIN...")
    
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

def buscar_setor_mecanica(cookies):
    """Busca o setor Mecânica"""
    print("\n🏭 BUSCANDO SETOR MECÂNICA...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/setores", cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            setores = response.json()
            for setor in setores:
                if 'MECANICA' in setor.get('nome', '').upper():
                    print(f"   ✅ Setor encontrado: {setor['nome']} (ID: {setor['id']})")
                    return setor
            
            print("   ⚠️ Setor Mecânica não encontrado")
            return None
        else:
            print(f"   ❌ Erro ao buscar setores: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao buscar setores: {e}")
        return None

def testar_endpoints_criacao(cookies, setor_mecanica):
    """Testa diferentes endpoints para criar usuário"""
    print("\n🧪 TESTANDO ENDPOINTS DE CRIAÇÃO...")
    
    # Dados base do usuário de teste
    dados_base = {
        "nome_completo": "Teste Mecânico API",
        "email": "teste.mecanica@registroos.com",
        "senha": "123456",
        "privilege_level": "USER",
        "trabalha_producao": True,
        "id_setor": setor_mecanica['id'] if setor_mecanica else None,
        "id_departamento": 1  # MOTORES
    }
    
    # Lista de endpoints para testar
    endpoints_teste = [
        "/api/users/create-user",
        "/api/users/create",
        "/api/admin/usuarios",
        "/api/register"
    ]
    
    for endpoint in endpoints_teste:
        print(f"\n   🔍 Testando: {endpoint}")
        
        try:
            # Adaptar dados conforme endpoint
            if endpoint == "/api/register":
                dados_adaptados = {
                    "primeiro_nome": "Teste",
                    "sobrenome": "Mecânico API",
                    "email": "teste.mecanica@registroos.com",
                    "password": "123456",
                    "nome_usuario": "teste.mecanica",
                    "matricula": "TEST001",
                    "cargo": "Técnico Teste",
                    "departamento": "MOTORES",
                    "setor_de_trabalho": setor_mecanica['nome'] if setor_mecanica else "MECANICA",
                    "trabalha_producao": True
                }
            elif endpoint == "/api/admin/usuarios":
                dados_adaptados = {
                    "nome_completo": "Teste Mecânico API",
                    "email": "teste.mecanica@registroos.com",
                    "matricula": "TEST001",
                    "setor": setor_mecanica['nome'] if setor_mecanica else "MECANICA",
                    "departamento": "MOTORES",
                    "cargo": "Técnico Teste",
                    "privilege_level": "USER",
                    "trabalha_producao": True
                }
            else:
                dados_adaptados = dados_base
            
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=dados_adaptados,
                cookies=cookies,
                timeout=10
            )
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                resultado = response.json()
                print(f"      ✅ SUCESSO! Endpoint funcional: {endpoint}")
                print(f"      Resposta: {json.dumps(resultado, indent=2)[:200]}...")
                return endpoint, dados_adaptados
            else:
                try:
                    error_detail = response.json()
                    print(f"      ❌ Erro: {error_detail}")
                except:
                    print(f"      ❌ Erro: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"      ❌ Exceção: {e}")
    
    print("\n   ❌ Nenhum endpoint funcionou")
    return None, None

def criar_usuarios_mecanica_api(cookies, endpoint_funcional, modelo_dados, setor_mecanica):
    """Cria usuários da Mecânica usando o endpoint que funciona"""
    print(f"\n👥 CRIANDO USUÁRIOS VIA: {endpoint_funcional}")
    
    usuarios_para_criar = [
        {
            "nome": "João Silva Mecânico",
            "email": "joao.mecanica@registroos.com",
            "matricula": "MEC001",
            "cargo": "Supervisor de Mecânica",
            "privilege_level": "SUPERVISOR"
        },
        {
            "nome": "Maria Santos Montadora",
            "email": "maria.mecanica@registroos.com",
            "matricula": "MEC002",
            "cargo": "Técnica Mecânica",
            "privilege_level": "USER"
        },
        {
            "nome": "Pedro Costa Mecânico",
            "email": "pedro.mecanica@registroos.com",
            "matricula": "MEC003",
            "cargo": "Mecânico Montador",
            "privilege_level": "USER"
        },
        {
            "nome": "Ana Oliveira Técnica",
            "email": "ana.mecanica@registroos.com",
            "matricula": "MEC004",
            "cargo": "Técnica de Montagem",
            "privilege_level": "USER"
        }
    ]
    
    usuarios_criados = []
    
    for usuario_info in usuarios_para_criar:
        try:
            # Adaptar dados conforme o modelo que funcionou
            if endpoint_funcional == "/api/register":
                dados_usuario = {
                    "primeiro_nome": usuario_info["nome"].split()[0],
                    "sobrenome": " ".join(usuario_info["nome"].split()[1:]),
                    "email": usuario_info["email"],
                    "password": "123456",
                    "nome_usuario": usuario_info["email"].split('@')[0],
                    "matricula": usuario_info["matricula"],
                    "cargo": usuario_info["cargo"],
                    "departamento": "MOTORES",
                    "setor_de_trabalho": setor_mecanica['nome'] if setor_mecanica else "MECANICA",
                    "trabalha_producao": True
                }
            elif endpoint_funcional == "/api/admin/usuarios":
                dados_usuario = {
                    "nome_completo": usuario_info["nome"],
                    "email": usuario_info["email"],
                    "matricula": usuario_info["matricula"],
                    "setor": setor_mecanica['nome'] if setor_mecanica else "MECANICA",
                    "departamento": "MOTORES",
                    "cargo": usuario_info["cargo"],
                    "privilege_level": usuario_info["privilege_level"],
                    "trabalha_producao": True
                }
            else:
                dados_usuario = {
                    "nome_completo": usuario_info["nome"],
                    "email": usuario_info["email"],
                    "senha": "123456",
                    "privilege_level": usuario_info["privilege_level"],
                    "trabalha_producao": True,
                    "id_setor": setor_mecanica['id'] if setor_mecanica else None,
                    "id_departamento": 1
                }
            
            print(f"   👤 Criando: {usuario_info['nome']} ({usuario_info['privilege_level']})")
            
            response = requests.post(
                f"{BASE_URL}{endpoint_funcional}",
                json=dados_usuario,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                resultado = response.json()
                print(f"      ✅ Usuário criado com sucesso")
                usuarios_criados.append(resultado)
                
                # Se for registro, tentar aprovar
                if endpoint_funcional == "/api/register" and resultado.get('id'):
                    try:
                        approve_response = requests.patch(
                            f"{BASE_URL}/api/users/{resultado['id']}/approve",
                            cookies=cookies,
                            timeout=10
                        )
                        if approve_response.status_code == 200:
                            print(f"      ✅ Usuário aprovado automaticamente")
                    except:
                        print(f"      ⚠️ Não foi possível aprovar automaticamente")
                        
            else:
                print(f"      ❌ Erro ao criar usuário: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"         Detalhes: {error_detail}")
                except:
                    print(f"         Resposta: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"      ❌ Erro ao criar {usuario_info['nome']}: {e}")
    
    return usuarios_criados

def verificar_usuarios_criados(cookies):
    """Verifica os usuários criados"""
    print("\n🔍 VERIFICANDO USUÁRIOS CRIADOS...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/usuarios", cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            usuarios = response.json()
            usuarios_mecanica = [u for u in usuarios if 'MECANICA' in u.get('setor', '').upper()]
            
            print(f"   📊 Usuários da Mecânica: {len(usuarios_mecanica)}")
            for user in usuarios_mecanica:
                print(f"      - {user['nome_completo']} ({user['privilege_level']})")
                print(f"        📧 {user['email']} | 🏭 {user['setor']}")
            
            return usuarios_mecanica
        else:
            print(f"   ❌ Erro ao verificar usuários: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar usuários: {e}")
        return []

def main():
    """Função principal"""
    print("🏭 CRIAÇÃO DE USUÁRIOS MECÂNICA VIA API")
    print("=" * 60)
    
    # Login
    cookies = fazer_login()
    if not cookies:
        print("❌ Falha no login - abortando")
        return False
    
    # Buscar setor Mecânica
    setor_mecanica = buscar_setor_mecanica(cookies)
    
    # Testar endpoints
    endpoint_funcional, modelo_dados = testar_endpoints_criacao(cookies, setor_mecanica)
    
    if not endpoint_funcional:
        print("❌ Nenhum endpoint de criação funcionou - abortando")
        return False
    
    # Criar usuários
    usuarios_criados = criar_usuarios_mecanica_api(cookies, endpoint_funcional, modelo_dados, setor_mecanica)
    
    # Verificar resultado
    usuarios_verificados = verificar_usuarios_criados(cookies)
    
    # Resumo
    print("\n" + "=" * 60)
    print("🎯 RESUMO DA CRIAÇÃO VIA API")
    print("=" * 60)
    print(f"✅ Endpoint usado: {endpoint_funcional}")
    print(f"✅ Usuários criados: {len(usuarios_criados)}")
    print(f"✅ Usuários verificados: {len(usuarios_verificados)}")
    
    if usuarios_verificados:
        print("\n🎉 USUÁRIOS DA MECÂNICA CRIADOS COM SUCESSO!")
        print("   🔑 Senha padrão: 123456")
        print("   🚀 Execute: python fluxo_completo_mecanica.py")
    else:
        print("\n❌ FALHA NA CRIAÇÃO DOS USUÁRIOS")
    
    return len(usuarios_verificados) > 0

if __name__ == "__main__":
    main()
