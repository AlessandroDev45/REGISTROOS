#!/usr/bin/env python3
"""
Testar scraping com OS 12345 para ver os dados retornados
"""

import sys
import os
from pathlib import Path

# Adicionar o caminho do script de scraping
script_path = Path("C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/scripts")
sys.path.append(str(script_path))

def testar_scraping_12345():
    """Executa scraping da OS 12345 e mostra os dados"""
    try:
        print("🚀 EXECUTANDO SCRAPING DA OS 12345...")
        print("=" * 50)
        
        # Importar a função de scraping
        from scrape_os_data import execute_scraping
        
        # Executar scraping
        os_numero = "12345"
        print(f"🔍 Iniciando scraping para OS: {os_numero}")
        
        scraped_data = execute_scraping(os_numero)
        
        if not scraped_data or len(scraped_data) == 0:
            print("❌ Nenhum dado retornado do scraping")
            return None
        
        print(f"✅ Scraping concluído! {len(scraped_data)} registro(s) encontrado(s)")
        
        # Mostrar todos os dados retornados
        for i, data in enumerate(scraped_data):
            print(f"\n📋 REGISTRO {i+1}:")
            print("-" * 30)
            
            # Mostrar todos os campos
            for key, value in data.items():
                if value and str(value).strip() and str(value) != "0":
                    print(f"   {key}: {value}")
        
        return scraped_data
        
    except ImportError as e:
        print(f"❌ Erro ao importar scraping: {e}")
        print("⚠️ Verifique se o arquivo scrape_os_data.py existe")
        return None
        
    except Exception as e:
        print(f"❌ Erro durante scraping: {e}")
        return None

def verificar_arquivo_env():
    """Verifica se o arquivo .env existe"""
    env_path = Path("C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/scripts/.env")
    
    if env_path.exists():
        print("✅ Arquivo .env encontrado")
        return True
    else:
        print("❌ Arquivo .env NÃO encontrado")
        print(f"   Caminho esperado: {env_path}")
        return False

def main():
    """Função principal"""
    print("🔍 TESTE DE SCRAPING - OS 12345")
    print("=" * 50)
    
    # Verificar arquivo .env
    print("\n1️⃣ VERIFICANDO ARQUIVO .ENV...")
    env_ok = verificar_arquivo_env()
    
    if not env_ok:
        print("\n⚠️ ATENÇÃO: Arquivo .env não encontrado!")
        print("   O scraping pode falhar por falta de credenciais")
        print("   Continuando mesmo assim para ver o erro...")
    
    # Executar scraping
    print("\n2️⃣ EXECUTANDO SCRAPING...")
    dados = testar_scraping_12345()
    
    if dados:
        print("\n🎉 SCRAPING FUNCIONOU!")
        print("   Agora posso implementar a integração correta")
    else:
        print("\n❌ SCRAPING FALHOU!")
        print("   Verifique:")
        print("   - Arquivo .env com credenciais")
        print("   - Conexão com internet")
        print("   - ChromeDriver instalado")

if __name__ == "__main__":
    main()
