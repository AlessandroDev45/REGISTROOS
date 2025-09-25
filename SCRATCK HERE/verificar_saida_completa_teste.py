#!/usr/bin/env python3
"""
Verificar a saída completa do endpoint de teste
"""

import requests
import json

def verificar_saida():
    """Verifica a saída completa do endpoint de teste"""
    
    print("🔍 VERIFICANDO SAÍDA COMPLETA DO TESTE")
    print("=" * 60)
    
    try:
        url = "http://localhost:8000/api/formulario/teste-scraping/20203"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 Código de retorno: {data.get('codigo_retorno')}")
            print(f"📊 Sucesso: {data.get('sucesso')}")
            print(f"❌ Stderr: {data.get('stderr', 'Vazio')}")
            
            stdout = data.get('stdout', '')
            print(f"\n📄 STDOUT ({len(stdout)} caracteres):")
            print("=" * 50)
            
            # Procurar pela linha "Resultado:"
            lines = stdout.split('\n')
            resultado_encontrado = False
            
            for i, line in enumerate(lines):
                if 'Resultado:' in line:
                    print(f"📊 LINHA {i}: {line}")
                    resultado_encontrado = True
                    
                    # Tentar extrair e processar o resultado
                    try:
                        resultado_str = line.split('Resultado: ')[1]
                        print(f"📊 Resultado extraído: {resultado_str[:200]}...")
                        
                        import ast
                        dados = ast.literal_eval(resultado_str)
                        
                        if dados and len(dados) > 0:
                            os_data = dados[0]
                            print(f"✅ DADOS PROCESSADOS COM SUCESSO!")
                            print(f"   OS: {os_data.get('OS', 'N/A')}")
                            print(f"   Cliente: {os_data.get('CLIENTE', 'N/A')}")
                            print(f"   Descrição: {os_data.get('DESCRIÇÃO', 'N/A')}")
                            print(f"   Status: {os_data.get('TAREFA', 'N/A')}")
                        else:
                            print(f"❌ Lista de dados vazia")
                            
                    except Exception as parse_error:
                        print(f"❌ Erro ao processar resultado: {parse_error}")
                    
                    break
            
            if not resultado_encontrado:
                print(f"❌ Linha 'Resultado:' não encontrada")
                print(f"📄 Últimas 10 linhas:")
                for line in lines[-10:]:
                    print(f"   {line}")
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_saida()
