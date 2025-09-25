#!/usr/bin/env python3
"""
Teste sem autenticação para verificar se o endpoint responde
"""

import requests

def testar_sem_autenticacao():
    """Testa o endpoint sem autenticação"""
    
    print("🔍 TESTE SEM AUTENTICAÇÃO")
    print("=" * 40)
    
    try:
        # URL correta baseada na documentação OpenAPI
        url = "http://localhost:8000/api/formulario/os/12345"
        print(f"🔍 URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ ENDPOINT EXISTE!")
            print("   Status 401 = Unauthorized (esperado sem login)")
            try:
                data = response.json()
                print(f"   Mensagem: {data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:100]}")
            return True
            
        elif response.status_code == 404:
            print("❌ ENDPOINT NÃO ENCONTRADO")
            try:
                data = response.json()
                print(f"   Mensagem: {data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:100]}")
            return False
            
        else:
            print(f"⚠️ STATUS INESPERADO: {response.status_code}")
            try:
                data = response.json()
                print(f"   Dados: {data}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return True
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE SEM AUTENTICAÇÃO")
    print("=" * 50)
    
    endpoint_existe = testar_sem_autenticacao()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO:")
    if endpoint_existe:
        print("✅ ENDPOINT FUNCIONANDO!")
        print("   O endpoint está registrado e respondendo")
        print("   Problema anterior era na URL incorreta")
        print("   URL correta: /api/formulario/os/{numero_os}")
    else:
        print("❌ ENDPOINT NÃO ENCONTRADO")
        print("   Verifique se o servidor foi reiniciado")

if __name__ == "__main__":
    main()
