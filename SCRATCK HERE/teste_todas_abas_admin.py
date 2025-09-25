#!/usr/bin/env python3
"""
Script para testar todas as abas administrativas e verificar se os campos de setor estão funcionando
"""

import requests
import json
from typing import Dict, Any

# Configuração da API
API_BASE = "http://localhost:8000/api"

def test_endpoint(endpoint: str, description: str) -> Dict[str, Any]:
    """Testa um endpoint e retorna o resultado"""
    try:
        print(f"\n🔍 Testando {description}...")
        print(f"   URL: {API_BASE}{endpoint}")
        
        response = requests.get(f"{API_BASE}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                total = len(data)
                first_item = data[0] if data else None
                print(f"   ✅ SUCESSO: {total} itens encontrados")
                if first_item:
                    # Verificar se tem campos de setor/departamento
                    has_setor = 'setor' in first_item or 'nome_setor' in first_item
                    has_departamento = 'departamento' in first_item or 'nome_departamento' in first_item
                    has_categoria = 'categoria' in first_item
                    
                    print(f"   📊 Primeiro item: ID={first_item.get('id', 'N/A')}")
                    if has_departamento:
                        dept_value = first_item.get('departamento') or first_item.get('nome_departamento')
                        print(f"   🏢 Departamento: {dept_value}")
                    if has_setor:
                        setor_value = first_item.get('setor') or first_item.get('nome_setor')
                        print(f"   🏭 Setor: {setor_value}")
                    if has_categoria:
                        print(f"   🎯 Categoria: {first_item.get('categoria')}")
                    
                    return {
                        "status": "SUCCESS",
                        "total": total,
                        "has_setor": has_setor,
                        "has_departamento": has_departamento,
                        "has_categoria": has_categoria,
                        "first_item": first_item
                    }
                else:
                    print(f"   ⚠️ VAZIO: Nenhum item encontrado")
                    return {"status": "EMPTY", "total": 0}
            else:
                print(f"   ✅ SUCESSO: Resposta não é lista")
                return {"status": "SUCCESS", "data": data}
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            return {"status": "ERROR", "code": response.status_code, "message": response.text}
            
    except Exception as e:
        print(f"   💥 EXCEÇÃO: {str(e)}")
        return {"status": "EXCEPTION", "error": str(e)}

def test_create_endpoint(endpoint: str, data: Dict[str, Any], description: str) -> Dict[str, Any]:
    """Testa criação em um endpoint"""
    try:
        print(f"\n🆕 Testando criação em {description}...")
        print(f"   URL: {API_BASE}{endpoint}")
        print(f"   Dados: {json.dumps(data, indent=2)}")
        
        response = requests.post(f"{API_BASE}{endpoint}", json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   ✅ CRIAÇÃO SUCESSO: ID={result.get('id', 'N/A')}")
            return {"status": "SUCCESS", "data": result}
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            return {"status": "ERROR", "code": response.status_code, "message": response.text}
            
    except Exception as e:
        print(f"   💥 EXCEÇÃO: {str(e)}")
        return {"status": "EXCEPTION", "error": str(e)}

def main():
    print("🚀 TESTE COMPLETO DE TODAS AS ABAS ADMINISTRATIVAS")
    print("=" * 60)
    
    # Lista de endpoints para testar
    endpoints_to_test = [
        ("/admin/departamentos/", "🏢 Departamentos"),
        ("/admin/setores/", "🏭 Setores"),
        ("/admin/tipos-maquina/", "🔧 Tipos de Máquina"),
        ("/admin/tipos-teste/", "🧪 Tipos de Testes"),
        ("/admin/tipos-atividade/", "📋 Atividades"),
        ("/admin/descricoes-atividade/", "📄 Descrição de Atividades"),
        ("/admin/tipos-falha/", "⚠️ Tipos de Falha"),
        ("/admin/causas-retrabalho/", "🔄 Causas de Retrabalho"),
        ("/estrutura-hierarquica", "🌳 Estrutura Hierárquica")
    ]
    
    results = {}
    
    # Testar todos os endpoints
    for endpoint, description in endpoints_to_test:
        results[endpoint] = test_endpoint(endpoint, description)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL DOS TESTES")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    empty_count = 0
    
    for endpoint, result in results.items():
        status = result.get("status", "UNKNOWN")
        if status == "SUCCESS":
            success_count += 1
            total = result.get("total", "N/A")
            has_setor = result.get("has_setor", False)
            has_departamento = result.get("has_departamento", False)
            has_categoria = result.get("has_categoria", False)
            
            status_setor = "✅" if has_setor else "❌"
            status_dept = "✅" if has_departamento else "❌"
            status_cat = "✅" if has_categoria else "❌"
            
            print(f"{endpoint:<30} ✅ OK ({total} itens) | Setor:{status_setor} Dept:{status_dept} Cat:{status_cat}")
        elif status == "EMPTY":
            empty_count += 1
            print(f"{endpoint:<30} ⚠️ VAZIO")
        else:
            error_count += 1
            print(f"{endpoint:<30} ❌ ERRO")
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   ✅ Sucessos: {success_count}")
    print(f"   ⚠️ Vazios: {empty_count}")
    print(f"   ❌ Erros: {error_count}")
    print(f"   📊 Total: {len(results)}")
    
    if error_count == 0:
        print(f"\n🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
    else:
        print(f"\n⚠️ {error_count} endpoints com problemas precisam de atenção.")

if __name__ == "__main__":
    main()
