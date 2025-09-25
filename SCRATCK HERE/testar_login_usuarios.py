#!/usr/bin/env python3
import requests
import json

def testar_login_usuario(email):
    """Testa login automático para um usuário específico"""
    try:
        print(f"\n🔐 Testando login para: {email}")
        
        # Fazer login automático
        response = requests.post(f"http://localhost:8000/api/auth/test-login/{email}")
        
        if response.status_code == 200:
            data = response.json()
            user = data['user']
            print(f"✅ Login bem-sucedido!")
            print(f"  Nome: {user['nome_completo']}")
            print(f"  Privilege: {user['privilege_level']}")
            print(f"  Trabalha Produção: {user['trabalha_producao']}")
            print(f"  Setor: {user.get('setor', 'N/A')}")
            print(f"  Departamento: {user.get('departamento', 'N/A')}")
            
            # Verificar acesso ao desenvolvimento
            cookies = response.cookies
            
            # Testar acesso ao endpoint de desenvolvimento
            dev_response = requests.get(
                "http://localhost:8000/api/desenvolvimento/apontamentos-detalhados",
                cookies=cookies
            )
            
            if dev_response.status_code == 200:
                print(f"✅ Acesso ao desenvolvimento: PERMITIDO")
                return True
            elif dev_response.status_code == 401:
                print(f"❌ Acesso ao desenvolvimento: NEGADO (401 - Não autenticado)")
                return False
            elif dev_response.status_code == 403:
                print(f"❌ Acesso ao desenvolvimento: NEGADO (403 - Sem permissão)")
                return False
            else:
                print(f"⚠️ Acesso ao desenvolvimento: ERRO ({dev_response.status_code})")
                return False
                
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"  Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🧪 TESTE DE AUTENTICAÇÃO E ACESSO AO DESENVOLVIMENTO")
    print("=" * 60)
    
    # Lista de usuários para testar
    usuarios_teste = [
        "admin@registroos.com",  # ADMIN
        "supervisor.mecanica_dia@registroos.com",  # SUPERVISOR com trabalha_producao=True
        "user.mecanica_dia@registroos.com",  # USER com trabalha_producao=True
        "supervisor.pcp@registroos.com",  # PCP (não deveria ter acesso)
        "teste.primeiro.login@registroos.com",  # USER com trabalha_producao=False
    ]
    
    resultados = {}
    
    for email in usuarios_teste:
        resultado = testar_login_usuario(email)
        resultados[email] = resultado
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS:")
    
    for email, tem_acesso in resultados.items():
        status = "✅ ACESSO PERMITIDO" if tem_acesso else "❌ ACESSO NEGADO"
        print(f"  {email}: {status}")
    
    # Verificar se os resultados estão corretos
    print("\n🎯 ANÁLISE:")
    
    esperado_com_acesso = [
        "admin@registroos.com",  # ADMIN
        "supervisor.mecanica_dia@registroos.com",  # SUPERVISOR
        "user.mecanica_dia@registroos.com",  # USER com trabalha_producao=True
    ]
    
    esperado_sem_acesso = [
        "supervisor.pcp@registroos.com",  # PCP
        "teste.primeiro.login@registroos.com",  # USER sem trabalha_producao
    ]
    
    corretos = 0
    total = len(resultados)
    
    for email in esperado_com_acesso:
        if email in resultados and resultados[email]:
            print(f"✅ {email}: Acesso correto (deveria ter acesso)")
            corretos += 1
        else:
            print(f"❌ {email}: Acesso incorreto (deveria ter acesso mas foi negado)")
    
    for email in esperado_sem_acesso:
        if email in resultados and not resultados[email]:
            print(f"✅ {email}: Acesso correto (não deveria ter acesso)")
            corretos += 1
        else:
            print(f"❌ {email}: Acesso incorreto (não deveria ter acesso mas foi permitido)")
    
    print(f"\n🏆 RESULTADO FINAL: {corretos}/{total} testes corretos")
    
    if corretos == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema de autenticação funcionando corretamente!")
    else:
        print("⚠️ Alguns testes falharam. Verificar configurações de permissão.")

if __name__ == "__main__":
    main()
