#!/usr/bin/env python3
import requests
import json

def testar_login_supervisor():
    """Testa login com usuário SUPERVISOR para verificar se setor e departamento são retornados"""
    try:
        print("🔐 Testando login com SUPERVISOR MECANICA DIA")
        
        # Dados de login
        login_data = {
            "username": "supervisor.mecanica_dia@registroos.com",
            "password": "supervisor123"
        }
        
        # Fazer login usando o endpoint /token
        response = requests.post(
            "http://localhost:8000/api/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            
            print("✅ Login bem-sucedido!")
            print(f"📋 Dados do usuário:")
            print(f"  Nome: {user.get('nome_completo')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Privilege: {user.get('privilege_level')}")
            print(f"  Trabalha Produção: {user.get('trabalha_producao')}")
            print(f"  ID Setor: {user.get('id_setor')}")
            print(f"  ID Departamento: {user.get('id_departamento')}")
            print(f"  🎯 Setor (nome): {user.get('setor')}")
            print(f"  🏢 Departamento (nome): {user.get('departamento')}")
            
            # Verificar se os campos necessários estão presentes
            if user.get('setor') and user.get('departamento'):
                print("\n✅ PROBLEMA RESOLVIDO!")
                print("   Os campos 'setor' e 'departamento' estão sendo retornados corretamente.")
                print("   O frontend agora deve conseguir redirecionar automaticamente.")
            else:
                print("\n❌ PROBLEMA AINDA EXISTE!")
                print("   Os campos 'setor' e/ou 'departamento' ainda não estão sendo retornados.")
            
            # Testar acesso ao endpoint /setores
            print(f"\n🔍 Testando acesso ao endpoint /setores...")
            cookies = response.cookies
            
            setores_response = requests.get(
                "http://localhost:8000/api/setores",
                cookies=cookies
            )
            
            print(f"Status /setores: {setores_response.status_code}")
            
            if setores_response.status_code == 200:
                setores_data = setores_response.json()
                print(f"✅ Setores retornados: {len(setores_data)}")
                
                # Mostrar alguns setores
                for i, setor in enumerate(setores_data[:3]):
                    print(f"  {i+1}. {setor.get('nome')} (ID: {setor.get('id')}, Dept ID: {setor.get('id_departamento')})")
                
                if len(setores_data) > 3:
                    print(f"  ... e mais {len(setores_data) - 3} setores")
            else:
                print(f"❌ Erro ao buscar setores: {setores_response.status_code}")
                print(f"Resposta: {setores_response.text}")
                
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_login_laboratorio():
    """Testa login com usuário SUPERVISOR LABORATORIO"""
    try:
        print("\n" + "="*60)
        print("🔐 Testando login com SUPERVISOR LABORATORIO DE ENSAIOS ELETRICOS")
        
        # Dados de login
        login_data = {
            "username": "supervisor.laboratorio_de_ensaios_eletricos@registroos.com",
            "password": "supervisor123"
        }
        
        # Fazer login usando o endpoint /token
        response = requests.post(
            "http://localhost:8000/api/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            
            print("✅ Login bem-sucedido!")
            print(f"📋 Dados do usuário:")
            print(f"  Nome: {user.get('nome_completo')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Privilege: {user.get('privilege_level')}")
            print(f"  Trabalha Produção: {user.get('trabalha_producao')}")
            print(f"  ID Setor: {user.get('id_setor')}")
            print(f"  ID Departamento: {user.get('id_departamento')}")
            print(f"  🎯 Setor (nome): {user.get('setor')}")
            print(f"  🏢 Departamento (nome): {user.get('departamento')}")
                
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 TESTE DE LOGIN SUPERVISOR - VERIFICAÇÃO DE CAMPOS")
    print("=" * 60)
    
    testar_login_supervisor()
    testar_login_laboratorio()
    
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Se os campos 'setor' e 'departamento' estão sendo retornados:")
    print("   - O frontend deve redirecionar automaticamente")
    print("   - Teste fazendo login no frontend")
    print("2. Se ainda não estão sendo retornados:")
    print("   - Verificar se o backend foi reiniciado")
    print("   - Verificar logs do backend para erros")
