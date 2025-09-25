#!/usr/bin/env python3
"""
Verificar se o endpoint está na documentação OpenAPI
"""

import requests
import json

def verificar_openapi():
    """Verifica se o endpoint está na documentação OpenAPI"""
    
    try:
        print("🔍 Verificando documentação OpenAPI...")
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            print(f"✅ OpenAPI carregado com {len(paths)} endpoints")
            
            # Procurar endpoints de desenvolvimento
            desenvolvimento_paths = []
            for path, methods in paths.items():
                if 'desenvolvimento' in path:
                    for method in methods.keys():
                        desenvolvimento_paths.append(f"{method.upper()} {path}")
            
            print(f"\n📋 Endpoints de desenvolvimento encontrados ({len(desenvolvimento_paths)}):")
            for endpoint in desenvolvimento_paths:
                print(f"   - {endpoint}")
            
            # Procurar especificamente pelo endpoint de formulário
            formulario_found = False
            for path in paths.keys():
                if 'formulario/os' in path:
                    print(f"\n✅ ENDPOINT DE FORMULÁRIO ENCONTRADO: {path}")
                    
                    # Mostrar detalhes do endpoint
                    path_info = paths[path]
                    for method, details in path_info.items():
                        print(f"   Método: {method.upper()}")
                        print(f"   Operação: {details.get('operationId', 'N/A')}")
                        print(f"   Resumo: {details.get('summary', 'N/A')}")
                    
                    formulario_found = True
                    break
            
            if not formulario_found:
                print("\n❌ ENDPOINT DE FORMULÁRIO NÃO ENCONTRADO")
                print("   O endpoint /desenvolvimento/formulario/os/{numero_os} não está na documentação")
                print("   Isso indica que o servidor não carregou as mudanças")
            
            return formulario_found
            
        else:
            print(f"❌ Erro ao obter OpenAPI: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar OpenAPI: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 VERIFICAÇÃO DA DOCUMENTAÇÃO OPENAPI")
    print("=" * 50)
    
    endpoint_encontrado = verificar_openapi()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO:")
    if endpoint_encontrado:
        print("✅ ENDPOINT ESTÁ REGISTRADO")
        print("   O problema pode estar na autenticação ou na lógica do endpoint")
    else:
        print("❌ ENDPOINT NÃO ESTÁ REGISTRADO")
        print("   SOLUÇÕES:")
        print("   1. Reiniciar o servidor backend")
        print("   2. Verificar se há erros de sintaxe no código")
        print("   3. Verificar se o router está sendo incluído corretamente")
        print("\n   COMANDO PARA REINICIAR:")
        print("   cd RegistroOS/registrooficial/backend")
        print("   python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()
