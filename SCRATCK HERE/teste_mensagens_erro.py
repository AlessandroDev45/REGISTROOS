#!/usr/bin/env python3
"""
Teste das mensagens de erro corretas
"""

import requests
import json

def testar_mensagens_erro():
    """Testa se as mensagens de erro estão corretas"""
    
    # Tentar fazer uma requisição sem autenticação para ver a mensagem
    try:
        print("🔍 Testando mensagem de erro para OS inexistente...")
        
        # Usar uma OS que sabemos que não existe
        os_inexistente = "99999999"
        
        response = requests.get(
            f"http://localhost:8000/api/desenvolvimento/formulario/os/{os_inexistente}",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Erro de autenticação - precisa fazer login primeiro")
            return False
        
        try:
            data = response.json()
            detail = data.get('detail', '')
            print(f"Mensagem retornada: {detail}")
            
            # Verificar se contém as mensagens esperadas
            if "⚠️ OS não cadastrada na base de dados" in detail:
                if "Você pode preencher os campos manualmente" in detail:
                    print("✅ Mensagem CORRETA: 'Você pode preencher os campos manualmente'")
                    return True
                elif "AGUARDE CONSULTA VIA WEB" in detail:
                    print("✅ Mensagem CORRETA: 'AGUARDE CONSULTA VIA WEB'")
                    return True
                else:
                    print("⚠️ Mensagem parcialmente correta")
                    return False
            else:
                print("❌ Mensagem INCORRETA")
                return False
                
        except json.JSONDecodeError:
            print(f"❌ Resposta não é JSON: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def verificar_servidor():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status: {response.status_code}")
            return False
    except:
        print("❌ Servidor não está rodando")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DAS MENSAGENS DE ERRO")
    print("=" * 40)
    
    print("\n1️⃣ Verificando servidor...")
    if not verificar_servidor():
        print("❌ Teste interrompido - servidor não disponível")
        return
    
    print("\n2️⃣ Testando mensagens de erro...")
    sucesso = testar_mensagens_erro()
    
    print("\n" + "=" * 40)
    print("📊 RESULTADO:")
    if sucesso:
        print("✅ MENSAGENS DE ERRO CORRETAS!")
        print("   As mensagens estão conforme especificado:")
        print("   - ⚠️ OS não cadastrada na base de dados. Você pode preencher os campos manualmente.")
        print("   - ⚠️ OS não cadastrada na base de dados. AGUARDE CONSULTA VIA WEB.")
    else:
        print("❌ MENSAGENS DE ERRO PRECISAM SER CORRIGIDAS")
        print("   Esperado:")
        print("   - ⚠️ OS não cadastrada na base de dados. Você pode preencher os campos manualmente.")
        print("   - ⚠️ OS não cadastrada na base de dados. AGUARDE CONSULTA VIA WEB.")

if __name__ == "__main__":
    main()
