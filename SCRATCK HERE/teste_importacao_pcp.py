#!/usr/bin/env python3
"""
TESTE DE IMPORTAÇÃO - Verificar se o módulo pcp_routes pode ser importado
"""

import sys
import os

# Adicionar o diretório backend ao path
backend_dir = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
sys.path.insert(0, backend_dir)

def test_import():
    print("🔍 TESTE DE IMPORTAÇÃO: pcp_routes")
    print("=" * 50)
    
    try:
        print("1. Testando importação do módulo pcp_routes...")
        from routes.pcp_routes import router as pcp_router
        print("   ✅ Módulo importado com sucesso")
        
        print(f"   📋 Tipo do router: {type(pcp_router)}")
        print(f"   📋 Tags do router: {pcp_router.tags}")
        
        # Verificar rotas registradas
        print("\n2. Verificando rotas registradas...")
        routes = pcp_router.routes
        print(f"   📊 Total de rotas: {len(routes)}")
        
        for i, route in enumerate(routes):
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"   {i+1}. {list(route.methods)[0]} {route.path}")
        
        # Procurar especificamente pela rota programacao-form-data
        print("\n3. Procurando rota 'programacao-form-data'...")
        found = False
        for route in routes:
            if hasattr(route, 'path') and 'programacao-form-data' in route.path:
                print(f"   ✅ Encontrada: {list(route.methods)[0]} {route.path}")
                found = True
        
        if not found:
            print("   ❌ Rota 'programacao-form-data' NÃO encontrada!")
            
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
    except Exception as e:
        print(f"   ❌ Erro geral: {e}")

if __name__ == "__main__":
    test_import()
