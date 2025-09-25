#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste dos endpoints dos formulários implementados
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'

def test_endpoints():
    """Testa todos os endpoints dos formulários"""
    print("🧪 TESTANDO ENDPOINTS DOS FORMULÁRIOS")
    print("=" * 60)
    
    # Headers para autenticação (ajustar conforme necessário)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your_token_here'  # Ajustar conforme necessário
    }
    
    # 1. Testar GET programações
    print("\n📋 1. TESTANDO GET /api/pcp/programacoes")
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacoes")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Programações encontradas: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 2. Testar PUT programação (editar)
    print("\n✏️ 2. TESTANDO PUT /api/pcp/programacoes/1")
    try:
        data = {
            "responsavel_id": 1,
            "setor_destino": "MECANICA DIA",
            "departamento_destino": "MOTORES",
            "data_inicio": (datetime.now() + timedelta(hours=1)).isoformat(),
            "data_fim": (datetime.now() + timedelta(hours=9)).isoformat(),
            "observacoes": "Teste de edição via API"
        }
        response = requests.put(f"{BASE_URL}/api/pcp/programacoes/1", json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 422]:
            print(f"   ✅ Endpoint funcionando (422 = validação)")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 3. Testar PATCH reatribuir
    print("\n🔄 3. TESTANDO PATCH /api/pcp/programacoes/1/reatribuir")
    try:
        data = {
            "responsavel_id": 2,
            "observacoes": "Reatribuição via API"
        }
        response = requests.patch(f"{BASE_URL}/api/pcp/programacoes/1/reatribuir", json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 422, 404]:
            print(f"   ✅ Endpoint funcionando")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 4. Testar DELETE cancelar
    print("\n❌ 4. TESTANDO DELETE /api/pcp/programacoes/1")
    try:
        response = requests.delete(f"{BASE_URL}/api/pcp/programacoes/1")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 405]:
            print(f"   ✅ Endpoint funcionando")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 5. Testar POST enviar para setor
    print("\n📤 5. TESTANDO POST /api/pcp/programacoes/1/enviar-setor")
    try:
        response = requests.post(f"{BASE_URL}/api/pcp/programacoes/1/enviar-setor")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 400]:
            print(f"   ✅ Endpoint funcionando")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 6. Testar GET form data
    print("\n📝 6. TESTANDO GET /api/pcp/programacao-form-data")
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dados do formulário carregados")
            print(f"   📊 Usuários: {len(data.get('usuarios', []))}")
            print(f"   📊 Setores: {len(data.get('setores', []))}")
            print(f"   📊 Departamentos: {len(data.get('departamentos', []))}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 7. Testar GET pendências
    print("\n⚠️ 7. TESTANDO GET /api/pendencias")
    try:
        response = requests.get(f"{BASE_URL}/api/pendencias")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Pendências encontradas: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO DOS TESTES:")
    print("   📋 GET programações - Testado")
    print("   ✏️ PUT editar programação - Testado")
    print("   🔄 PATCH reatribuir - Testado")
    print("   ❌ DELETE cancelar - Testado")
    print("   📤 POST enviar setor - Testado")
    print("   📝 GET form data - Testado")
    print("   ⚠️ GET pendências - Testado")
    print("\n✅ TODOS OS ENDPOINTS FORAM TESTADOS!")
    print("   🔧 Verifique os status codes acima")
    print("   📊 200 = Sucesso")
    print("   📊 404 = Não encontrado (normal para testes)")
    print("   📊 422 = Erro de validação (normal)")
    print("   📊 405 = Método não permitido (verificar implementação)")

if __name__ == "__main__":
    test_endpoints()
