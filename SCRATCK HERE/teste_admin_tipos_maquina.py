#!/usr/bin/env python3
"""
Script para testar o endpoint de tipos de máquina do admin
"""

import requests
import json

def testar_admin_tipos_maquina():
    """Testa o endpoint de tipos de máquina do admin"""
    
    print("🧪 TESTE ADMIN - TIPOS DE MÁQUINA")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Primeiro fazer login
    print("\n1️⃣ FAZENDO LOGIN")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        print(f"   Status login: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Login realizado com sucesso!")
            
            # Extrair cookies
            cookies = response.cookies
            print(f"   🍪 Cookies recebidos: {list(cookies.keys())}")
            
            # Testar endpoint de tipos de máquina
            print("\n2️⃣ TESTANDO ENDPOINT TIPOS DE MÁQUINA")
            response = requests.get(f"{base_url}/api/admin/tipos-maquina/", cookies=cookies, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {len(data)} tipos de máquina encontrados")
                
                if data:
                    print(f"   📄 Primeiros 3 itens:")
                    for i, item in enumerate(data[:3], 1):
                        print(f"      {i}. ID: {item.get('id')}, Nome: {item.get('nome_tipo')}, Categoria: {item.get('categoria')}")
                else:
                    print(f"   ⚠️ Lista vazia retornada")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   📄 Resposta: {response.text}")
                
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Testar também sem autenticação
    print("\n3️⃣ TESTANDO SEM AUTENTICAÇÃO")
    try:
        response = requests.get(f"{base_url}/api/admin/tipos-maquina/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   📄 Resposta: {response.text}")
        
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE FINALIZADO")

if __name__ == "__main__":
    testar_admin_tipos_maquina()
