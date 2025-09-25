#!/usr/bin/env python3
"""
Teste para verificar o tratamento de erros do scraping quando não há OS
"""

import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

def test_scraping_nonexistent_os():
    """Testa o scraping com uma OS que não existe"""
    try:
        # Importar o script de scraping
        scripts_path = os.path.join(backend_path, 'scripts')
        sys.path.append(scripts_path)
        
        from scrape_os_data import execute_scraping
        
        # Testar com uma OS que provavelmente não existe
        test_os_numbers = [
            "99999999",  # Número muito alto
            "INEXISTENTE",  # Texto
            "000000",  # Zeros
            "",  # Vazio
            None  # Nulo
        ]
        
        for os_number in test_os_numbers:
            print(f"\n🧪 Testando OS: {os_number}")
            try:
                result = execute_scraping(os_number)
                print(f"✅ Resultado: {result}")
                
                if not result:
                    print("✅ Tratamento correto: Lista vazia retornada")
                else:
                    print(f"⚠️ Dados inesperados retornados: {len(result)} registros")
                    
            except Exception as e:
                print(f"❌ Erro capturado: {e}")
                
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Verifique se o caminho do backend está correto")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def test_api_endpoint():
    """Testa o endpoint da API com OS inexistente"""
    try:
        import requests
        
        # URL do endpoint (ajuste conforme necessário)
        base_url = "http://localhost:8000"
        
        # Testar endpoint de busca de OS
        test_os = "99999999"
        url = f"{base_url}/api/desenvolvimento/os/{test_os}"
        
        print(f"\n🌐 Testando endpoint: {url}")
        
        # Fazer requisição (você precisará adicionar autenticação se necessário)
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("✅ Tratamento correto: 404 retornado para OS inexistente")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except ImportError:
        print("❌ Biblioteca 'requests' não disponível")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

if __name__ == "__main__":
    print("🔍 TESTE DE TRATAMENTO DE ERROS DO SCRAPING")
    print("=" * 50)
    
    print("\n1. Testando função de scraping diretamente:")
    test_scraping_nonexistent_os()
    
    print("\n2. Testando endpoint da API:")
    test_api_endpoint()
    
    print("\n✅ Testes concluídos!")
