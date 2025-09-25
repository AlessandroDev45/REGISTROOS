#!/usr/bin/env python3
"""
Teste para simular exatamente como o backend chama o script de scraping
"""

import subprocess
import os

def testar_subprocess():
    """Testa o subprocess exatamente como o backend faz"""
    
    print("🔍 TESTANDO SUBPROCESS COMO BACKEND")
    print("=" * 50)
    
    try:
        numero_os = "20203"
        
        # Caminho exato como no backend
        scrap_path = os.path.join(
            "C:", "Users", "Alessandro", "OneDrive", "Desktop", "RegistroOS", 
            "RegistroOS", "registrooficial", "backend", "routes", "..", "scripts", "scrape_os_data.py"
        )
        
        print(f"📁 Caminho do script: {scrap_path}")
        print(f"📁 Script existe: {os.path.exists(scrap_path)}")
        
        # Executar exatamente como o backend
        print(f"🚀 Executando comando: python {scrap_path} {numero_os}")
        result_scraping = subprocess.run(
            ["python", scrap_path, numero_os],
            capture_output=True,
            text=False,  # Capturar como bytes
            timeout=60
        )
        
        print(f"📊 Código de retorno: {result_scraping.returncode}")
        print(f"📄 Stdout (bytes): {result_scraping.stdout}")
        print(f"❌ Stderr (bytes): {result_scraping.stderr}")
        
        if result_scraping.returncode == 0:
            # Decodificar como o backend faz
            try:
                stdout_text = result_scraping.stdout.decode('utf-8', errors='replace') if result_scraping.stdout else ""
            except:
                stdout_text = str(result_scraping.stdout) if result_scraping.stdout else ""
            
            print(f"✅ Scraping executado com sucesso")
            print(f"📄 Saída decodificada: {stdout_text}")
            
            # Processar como o backend faz
            output_lines = stdout_text.strip().split('\n')
            resultado_line = None
            
            print(f"🔍 Linhas de saída ({len(output_lines)}):")
            for i, line in enumerate(output_lines):
                print(f"   {i}: {line[:100]}...")  # Primeiros 100 chars
            
            for line in output_lines:
                if line.startswith('Resultado: '):
                    resultado_line = line.replace('Resultado: ', '')
                    print(f"📊 Linha de resultado encontrada: {resultado_line[:100]}...")
                    break
            
            if resultado_line:
                print(f"🔄 Tentando converter resultado...")
                import ast
                scraped_data = ast.literal_eval(resultado_line)
                
                if scraped_data and len(scraped_data) > 0:
                    os_data = scraped_data[0]
                    print(f"📊 Dados coletados com sucesso!")
                    print(f"   OS: {os_data.get('OS', 'N/A')}")
                    print(f"   Cliente: {os_data.get('CLIENTE', 'N/A')}")
                    print(f"   Descrição: {os_data.get('DESCRIÇÃO', 'N/A')}")
                    print(f"   Status: {os_data.get('TAREFA', 'N/A')}")
                else:
                    print(f"❌ Lista de dados vazia")
            else:
                print(f"❌ Linha 'Resultado:' não encontrada")
        else:
            print(f"❌ Scraping falhou com código {result_scraping.returncode}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    testar_subprocess()
