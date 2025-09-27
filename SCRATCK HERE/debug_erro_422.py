#!/usr/bin/env python3
"""
DEBUG DO ERRO 422
=================

Simula exatamente a requisição que o frontend está fazendo
"""

import sys
import os

# Adicionar o caminho do backend ao Python path
backend_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
sys.path.insert(0, backend_path)

# Mudar para o diretório do backend
os.chdir(backend_path)

from pydantic import BaseModel, ValidationError
from typing import Optional

# Importar o modelo exato do backend
class DepartamentoCreate(BaseModel):
    nome_tipo: str
    descricao: Optional[str] = None
    ativo: bool = True

def testar_validacao_pydantic():
    """Testa a validação do Pydantic com os dados exatos do frontend"""
    
    print("🚀 TESTANDO VALIDAÇÃO PYDANTIC")
    print("=" * 50)
    
    # Dados que o frontend está enviando (baseado no log)
    dados_frontend = {
        "nome_tipo": "DFSAFF",
        "descricao": "SDFAFSAF", 
        "ativo": True
    }
    
    print(f"📤 Dados do frontend: {dados_frontend}")
    
    try:
        # Tentar criar o modelo Pydantic
        dept_data = DepartamentoCreate(**dados_frontend)
        print("✅ Validação Pydantic passou!")
        print(f"📋 Modelo criado: {dept_data}")
        print(f"   nome_tipo: '{dept_data.nome_tipo}'")
        print(f"   descricao: '{dept_data.descricao}'")
        print(f"   ativo: {dept_data.ativo}")
        
        return True
        
    except ValidationError as e:
        print("❌ Erro de validação Pydantic!")
        print(f"❌ Detalhes: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def testar_dados_problematicos():
    """Testa vários tipos de dados que podem causar erro 422"""
    
    print(f"\n🔍 TESTANDO DADOS PROBLEMÁTICOS")
    print("=" * 40)
    
    casos_teste = [
        # Caso 1: String vazia
        {"nome_tipo": "", "descricao": "teste", "ativo": True},
        
        # Caso 2: None
        {"nome_tipo": None, "descricao": "teste", "ativo": True},
        
        # Caso 3: Tipo errado
        {"nome_tipo": 123, "descricao": "teste", "ativo": True},
        
        # Caso 4: Campo extra (id)
        {"id": 0, "nome_tipo": "TESTE", "descricao": "teste", "ativo": True},
        
        # Caso 5: ativo como string
        {"nome_tipo": "TESTE", "descricao": "teste", "ativo": "true"},
        
        # Caso 6: Dados válidos
        {"nome_tipo": "TESTE_VALIDO", "descricao": "teste", "ativo": True},
    ]
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n📋 Caso {i}: {caso}")
        try:
            dept_data = DepartamentoCreate(**caso)
            print(f"   ✅ Válido: {dept_data}")
        except ValidationError as e:
            print(f"   ❌ Inválido: {e}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def verificar_imports_backend():
    """Verifica se os imports do backend estão funcionando"""
    
    print(f"\n🔍 VERIFICANDO IMPORTS DO BACKEND")
    print("=" * 40)
    
    try:
        from app.database_models import Departamento
        print("✅ Import Departamento OK")
        
        from routes.admin_config_routes import DepartamentoCreate
        print("✅ Import DepartamentoCreate OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 DEBUG COMPLETO DO ERRO 422")
    print("=" * 60)
    
    # 1. Verificar imports
    if not verificar_imports_backend():
        print("❌ Falha nos imports - não é possível continuar")
        return
    
    # 2. Testar validação com dados do frontend
    if testar_validacao_pydantic():
        print("\n✅ Os dados do frontend são válidos para o Pydantic")
        print("🔍 O erro 422 deve estar vindo de outro lugar...")
    else:
        print("\n❌ Os dados do frontend são inválidos para o Pydantic")
        print("🔧 Este é provavelmente o problema!")
    
    # 3. Testar casos problemáticos
    testar_dados_problematicos()
    
    print(f"\n🎉 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
