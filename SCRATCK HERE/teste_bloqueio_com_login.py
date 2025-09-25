#!/usr/bin/env python3
"""
Teste para verificar se o bloqueio da OS 12345 está funcionando com login
"""

import requests
import json

def fazer_login():
    """Faz login e retorna o token"""
    try:
        login_url = "http://localhost:8000/api/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("🔐 Fazendo login...")
        response = requests.post(login_url, data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login realizado com sucesso")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante o login: {e}")
        return None

def testar_os_12345():
    """Testa se a OS 12345 retorna dados de bloqueio corretos"""
    
    print("🧪 TESTE: Verificando bloqueio da OS 12345")
    print("=" * 50)
    
    # Fazer login primeiro
    token = fazer_login()
    if not token:
        print("❌ Não foi possível fazer login. Teste abortado.")
        return
    
    try:
        # URL do endpoint
        url = "http://localhost:8000/api/formulario/os/12345"
        
        # Headers com autenticação
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar campos importantes
            print("\n🔍 VERIFICAÇÕES:")
            print(f"   📋 Número OS: {data.get('numero_os', 'N/A')}")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   👤 Cliente: {data.get('cliente', 'N/A')}")
            print(f"   🔧 Equipamento: {data.get('equipamento', 'N/A')}")
            print(f"   🚫 Bloqueado: {data.get('bloqueado_para_apontamento', 'N/A')}")
            print(f"   ⚠️ Motivo: {data.get('motivo_bloqueio', 'N/A')}")
            
            # Verificar se está bloqueado corretamente
            status_finalizados = [
                'RECUSADA - CONFERIDA',
                'TERMINADA - CONFERIDA', 
                'TERMINADA - EXPEDIDA',
                'OS CANCELADA'
            ]
            
            status_atual = data.get('status', '')
            deveria_estar_bloqueado = status_atual in status_finalizados
            esta_bloqueado = data.get('bloqueado_para_apontamento', False)
            
            print(f"\n🎯 RESULTADO DO TESTE:")
            print(f"   Status atual: {status_atual}")
            print(f"   Deveria estar bloqueado: {deveria_estar_bloqueado}")
            print(f"   Está bloqueado: {esta_bloqueado}")
            
            if deveria_estar_bloqueado == esta_bloqueado:
                print("   ✅ TESTE PASSOU - Bloqueio funcionando corretamente!")
                
                # Testar também no frontend
                print(f"\n🌐 TESTE NO FRONTEND:")
                print(f"   1. Acesse: http://localhost:3001")
                print(f"   2. Faça login")
                print(f"   3. Vá para Desenvolvimento")
                print(f"   4. Digite '12345' no campo OS")
                print(f"   5. Deve mostrar: '{data.get('cliente', 'Cliente não informado')}'")
                print(f"   6. Deve mostrar: '{data.get('equipamento', 'Equipamento não informado')}'")
                print(f"   7. Botões devem estar bloqueados")
                
            else:
                print("   ❌ TESTE FALHOU - Bloqueio não está funcionando!")
                
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    testar_os_12345()
