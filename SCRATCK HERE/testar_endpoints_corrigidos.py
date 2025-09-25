#!/usr/bin/env python3
"""
Script para testar todos os endpoints administrativos corrigidos
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/admin"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Testa um endpoint e retorna o resultado"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        elif method == "PUT":
            response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
        
        print(f"\n🔍 {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            if response.content:
                result = response.json()
                if isinstance(result, list):
                    print(f"✅ Retornou {len(result)} itens")
                    if result:
                        print(f"📋 Primeiro item: {json.dumps(result[0], indent=2, ensure_ascii=False)}")
                else:
                    print(f"✅ Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False

def main():
    print("🚀 TESTANDO ENDPOINTS ADMINISTRATIVOS CORRIGIDOS")
    print("=" * 60)
    
    # 1. DEPARTAMENTOS (já funcionando)
    print("\n📂 1. DEPARTAMENTOS")
    test_endpoint("GET", "/departamentos/")
    
    # 2. SETORES (já funcionando)
    print("\n🏭 2. SETORES")
    test_endpoint("GET", "/setores/")
    
    # 3. TIPOS DE MÁQUINA (corrigido)
    print("\n🔧 3. TIPOS DE MÁQUINA")
    test_endpoint("GET", "/tipos-maquina/")
    
    # 4. TIPOS DE TESTE (corrigido)
    print("\n🧪 4. TIPOS DE TESTE")
    test_endpoint("GET", "/tipos-teste/")
    
    # Teste de criação com departamento
    test_data = {
        "nome": f"TESTE_SCRIPT_{datetime.now().strftime('%H%M%S')}",
        "departamento": "MOTORES",
        "descricao": "Teste criado via script",
        "tipo_teste": "ESTATICO"
    }
    test_endpoint("POST", "/tipos-teste/", test_data, 200)
    
    # 5. TIPOS DE ATIVIDADE (corrigido)
    print("\n📋 5. TIPOS DE ATIVIDADE")
    test_endpoint("GET", "/tipos-atividade/")
    
    # 6. DESCRIÇÕES DE ATIVIDADE (corrigido)
    print("\n📄 6. DESCRIÇÕES DE ATIVIDADE")
    test_endpoint("GET", "/descricoes-atividade/")
    
    # 7. TIPOS DE FALHA (corrigido)
    print("\n⚠️ 7. TIPOS DE FALHA")
    test_endpoint("GET", "/tipos-falha/")
    
    # 8. CAUSAS DE RETRABALHO (corrigido)
    print("\n🔄 8. CAUSAS DE RETRABALHO")
    test_endpoint("GET", "/causas-retrabalho/")
    
    print("\n" + "=" * 60)
    print("✅ TESTE COMPLETO!")

if __name__ == "__main__":
    main()
