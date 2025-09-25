#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuários para o setor Mecânica
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

def verificar_setor_mecanica(cookies):
    """Verifica se o setor Mecânica existe"""
    print("\n🏭 VERIFICANDO SETOR MECÂNICA...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/setores", cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            setores = response.json()
            setor_mecanica = None
            
            for setor in setores:
                if 'MECANICA' in setor.get('nome', '').upper() or 'MECÂNICA' in setor.get('nome', '').upper():
                    setor_mecanica = setor
                    break
            
            if setor_mecanica:
                print(f"   ✅ Setor encontrado: {setor_mecanica['nome']} - {setor_mecanica['departamento']}")
                return setor_mecanica
            else:
                print("   ⚠️ Setor Mecânica não encontrado, criando...")
                return criar_setor_mecanica(cookies)
        else:
            print(f"   ❌ Erro ao buscar setores: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar setor: {e}")
        return None

def criar_setor_mecanica(cookies):
    """Cria o setor Mecânica se não existir"""
    print("   🔧 CRIANDO SETOR MECÂNICA...")
    
    try:
        dados_setor = {
            "nome": "MECANICA",
            "departamento": "MOTORES",
            "descricao": "Setor responsável por montagem e manutenção mecânica de motores",
            "ativo": True,
            "area_tipo": "PRODUCAO",
            "permite_apontamento": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/config/setores",
            json=dados_setor,
            cookies=cookies,
            timeout=10
        )
        
        if response.status_code == 200:
            setor = response.json()
            print(f"   ✅ Setor criado: {setor.get('nome')}")
            return setor
        else:
            print(f"   ❌ Erro ao criar setor: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao criar setor: {e}")
        return None

def criar_usuarios_mecanica(cookies):
    """Cria usuários para o setor Mecânica"""
    print("\n👥 CRIANDO USUÁRIOS DA MECÂNICA...")
    
    usuarios_para_criar = [
        {
            "nome_completo": "João Silva Mecânico",
            "email": "joao.mecanica@registroos.com",
            "senha": "123456",
            "matricula": "MEC001",
            "setor": "MECANICA",
            "departamento": "MOTORES",
            "cargo": "Supervisor de Mecânica",
            "privilege_level": "SUPERVISOR",
            "trabalha_producao": True
        },
        {
            "nome_completo": "Maria Santos Montadora",
            "email": "maria.mecanica@registroos.com",
            "senha": "123456",
            "matricula": "MEC002",
            "setor": "MECANICA",
            "departamento": "MOTORES",
            "cargo": "Técnica Mecânica",
            "privilege_level": "USER",
            "trabalha_producao": True
        },
        {
            "nome_completo": "Pedro Costa Mecânico",
            "email": "pedro.mecanica@registroos.com",
            "senha": "123456",
            "matricula": "MEC003",
            "setor": "MECANICA",
            "departamento": "MOTORES",
            "cargo": "Mecânico Montador",
            "privilege_level": "USER",
            "trabalha_producao": True
        },
        {
            "nome_completo": "Ana Oliveira Técnica",
            "email": "ana.mecanica@registroos.com",
            "senha": "123456",
            "matricula": "MEC004",
            "setor": "MECANICA",
            "departamento": "MOTORES",
            "cargo": "Técnica de Montagem",
            "privilege_level": "USER",
            "trabalha_producao": True
        }
    ]
    
    usuarios_criados = []
    
    for dados_usuario in usuarios_para_criar:
        try:
            print(f"   👤 Criando: {dados_usuario['nome_completo']} ({dados_usuario['privilege_level']})")
            
            response = requests.post(
                f"{BASE_URL}/api/users/create-user",
                json=dados_usuario,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                usuario = response.json()
                print(f"      ✅ Usuário criado: ID {usuario.get('id')}")
                
                # Aprovar usuário automaticamente
                if usuario.get('id'):
                    approve_response = requests.patch(
                        f"{BASE_URL}/api/users/{usuario['id']}/approve",
                        cookies=cookies,
                        timeout=10
                    )
                    
                    if approve_response.status_code == 200:
                        print(f"      ✅ Usuário aprovado automaticamente")
                    else:
                        print(f"      ⚠️ Erro ao aprovar usuário: {approve_response.status_code}")
                
                usuarios_criados.append(usuario)
            else:
                print(f"      ❌ Erro ao criar usuário: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"         Detalhes: {error_detail}")
                except:
                    print(f"         Resposta: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"      ❌ Erro ao criar usuário {dados_usuario['nome_completo']}: {e}")
    
    print(f"\n   📊 RESUMO: {len(usuarios_criados)} usuários criados com sucesso")
    return usuarios_criados

def verificar_usuarios_criados(cookies):
    """Verifica os usuários criados"""
    print("\n🔍 VERIFICANDO USUÁRIOS CRIADOS...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/usuarios", cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            usuarios = response.json()
            usuarios_mecanica = [u for u in usuarios if 'MECANICA' in u.get('setor', '').upper()]
            
            print(f"   📊 Usuários da Mecânica no sistema: {len(usuarios_mecanica)}")
            for user in usuarios_mecanica:
                status_aprovacao = "✅ APROVADO" if user.get('is_approved') else "⏳ PENDENTE"
                print(f"      - {user['nome_completo']} ({user['privilege_level']}) - {status_aprovacao}")
                print(f"        Email: {user['email']} | Setor: {user['setor']}")
            
            return usuarios_mecanica
        else:
            print(f"   ❌ Erro ao verificar usuários: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar usuários: {e}")
        return []

def main():
    """Função principal"""
    print("🏭 CRIAÇÃO DE USUÁRIOS PARA SETOR MECÂNICA")
    print("=" * 60)
    
    # Login como admin
    cookies = fazer_login()
    if not cookies:
        print("❌ Falha no login - abortando")
        return False
    
    # Verificar/criar setor Mecânica
    setor_mecanica = verificar_setor_mecanica(cookies)
    if not setor_mecanica:
        print("❌ Falha ao verificar/criar setor Mecânica - abortando")
        return False
    
    # Criar usuários da Mecânica
    usuarios_criados = criar_usuarios_mecanica(cookies)
    if not usuarios_criados:
        print("❌ Nenhum usuário foi criado - abortando")
        return False
    
    # Verificar usuários criados
    usuarios_verificados = verificar_usuarios_criados(cookies)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 RESUMO DA CRIAÇÃO")
    print("=" * 60)
    print(f"✅ Setor Mecânica: {setor_mecanica.get('nome')} - {setor_mecanica.get('departamento')}")
    print(f"✅ Usuários criados: {len(usuarios_criados)}")
    print(f"✅ Usuários verificados: {len(usuarios_verificados)}")
    
    print("\n👥 USUÁRIOS DA MECÂNICA PRONTOS:")
    for user in usuarios_verificados:
        print(f"   - {user['nome_completo']} ({user['privilege_level']})")
        print(f"     📧 {user['email']} | 🏭 {user['setor']}")
    
    print("\n🎉 SETOR MECÂNICA CONFIGURADO COM SUCESSO!")
    print("   📋 Agora é possível executar o fluxo completo")
    print("   🔄 Execute: python fluxo_completo_mecanica.py")
    
    return True

if __name__ == "__main__":
    main()
