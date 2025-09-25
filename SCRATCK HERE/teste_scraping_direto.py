#!/usr/bin/env python3
"""
Teste direto do scraping sem passar pelo endpoint
"""

import sys
import os
from pathlib import Path

# Adicionar o caminho do backend ao sys.path
backend_path = Path(__file__).parent.parent / "RegistroOS" / "registrooficial" / "backend"
sys.path.append(str(backend_path))

def testar_scraping_direto():
    """Testa o scraping diretamente"""
    
    print("🚀 TESTE DIRETO DO SCRAPING")
    print("=" * 50)
    
    try:
        # Importar o módulo de scraping
        script_path = backend_path / "scripts" / "scrape_os_data.py"
        print(f"📁 Caminho do script: {script_path}")
        print(f"📁 Script existe: {script_path.exists()}")
        
        if not script_path.exists():
            print("❌ Script não encontrado!")
            return False
        
        # Adicionar o diretório scripts ao path
        scripts_dir = str(script_path.parent)
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        
        print("📦 Importando módulo de scraping...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("scrape_os_data", script_path)
        scrape_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scrape_module)
        print("✅ Módulo importado com sucesso!")
        
        # Testar com OS 12345
        numero_os = "12345"
        print(f"\n🚀 Executando scraping para OS: {numero_os}")
        print("⏳ AGUARDE... O scraping pode demorar alguns minutos...")
        print("📋 Monitore o Chrome que será aberto...")
        
        # Executar scraping
        scraped_data = scrape_module.execute_scraping(numero_os)
        
        print(f"\n📊 RESULTADO DO SCRAPING:")
        print(f"   - Dados retornados: {len(scraped_data) if scraped_data else 0} registros")
        
        if scraped_data and len(scraped_data) > 0:
            print("🎉 SCRAPING FUNCIONOU!")
            
            # Mostrar dados principais
            for i, os_data in enumerate(scraped_data):
                print(f"\n📋 OS {i+1}:")
                print(f"   - Número: {os_data.get('NUMERO_OS', 'N/A')}")
                print(f"   - Cliente: {os_data.get('CLIENTE', 'N/A')}")
                print(f"   - Equipamento: {os_data.get('EQUIPAMENTO', 'N/A')}")
                print(f"   - Status: {os_data.get('STATUS', 'N/A')}")
                print(f"   - Potência: {os_data.get('POTENCIA', 'N/A')}")
                print(f"   - Tensão: {os_data.get('TENSAO', 'N/A')}")
                print(f"   - Classificação: {os_data.get('CLASSIFICACAO DO EQUIPAMENTO', 'N/A')}")
                
                # Mostrar todos os campos disponíveis
                print(f"   - Total de campos: {len(os_data)}")
                print(f"   - Campos: {list(os_data.keys())}")
            
            return True
        else:
            print("❌ SCRAPING NÃO RETORNOU DADOS")
            print("   Possíveis causas:")
            print("   - OS não existe no sistema")
            print("   - Problema de conexão")
            print("   - Mudança na estrutura do site")
            return False
            
    except Exception as e:
        print(f"❌ ERRO NO SCRAPING: {e}")
        print(f"🔍 Tipo do erro: {type(e)}")
        
        # Stack trace completo
        import traceback
        print(f"\n📋 Stack trace completo:")
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DIRETO DO SCRAPING")
    print("=" * 60)
    
    print("📋 ESTE TESTE VAI:")
    print("   1. Importar o módulo de scraping diretamente")
    print("   2. Executar o scraping da OS 12345")
    print("   3. Mostrar os dados retornados")
    print("   4. Confirmar se o scraping funciona")
    
    print("\n⚠️ IMPORTANTE:")
    print("   - O Chrome será aberto em modo headless")
    print("   - O processo pode demorar alguns minutos")
    print("   - Certifique-se de que tem conexão com a internet")
    
    input("\n⏸️ Pressione ENTER para continuar...")
    
    sucesso = testar_scraping_direto()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 SCRAPING FUNCIONA PERFEITAMENTE!")
        print("   O problema não é o scraping em si")
        print("   O problema pode ser:")
        print("   - Timeout do endpoint")
        print("   - Reinicialização do servidor")
        print("   - Configuração do frontend")
    else:
        print("❌ SCRAPING TEM PROBLEMAS!")
        print("   Verifique:")
        print("   - Arquivo .env")
        print("   - Conexão com internet")
        print("   - ChromeDriver")
        print("   - Credenciais de login")

if __name__ == "__main__":
    main()
