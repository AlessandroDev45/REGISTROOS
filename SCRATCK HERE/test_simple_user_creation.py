#!/usr/bin/env python3
"""
Teste simples de criação de usuário para debug
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@registroos.com"
ADMIN_PASSWORD = "123456"

def test_simple_creation():
    print("🚀 Teste simples de criação de usuário...")
    
    # 1. Login
    print("🔐 Fazendo login...")
    data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=data)
    if response.status_code != 200:
        print(f"❌ Falha no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return
    
    cookies = response.cookies
    print("✅ Login bem-sucedido!")
    
    # 2. Criar usuário
    print("👤 Criando usuário...")
    user_data = {
        "nome_completo": "TESTE DEBUG",
        "email": "teste.final@registroos.com",
        "matricula": "DEBUG123",
        "setor": "MECANICA DIA",
        "departamento": "MOTORES",
        "cargo": "TECNICO",
        "privilege_level": "USER",
        "trabalha_producao": True
    }
    
    print(f"📤 Enviando dados: {json.dumps(user_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/usuarios",
        json=user_data,
        cookies=cookies
    )
    
    print(f"📥 Status: {response.status_code}")
    print(f"📥 Resposta: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Usuário criado!")
        print(f"🆔 ID: {result.get('id')}")
        print(f"🆔 ID Setor: {result.get('id_setor')}")
        print(f"🆔 ID Departamento: {result.get('id_departamento')}")
    else:
        print("❌ Falha na criação")

if __name__ == "__main__":
    test_simple_creation()
