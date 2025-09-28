#!/usr/bin/env python3
"""
Teste detalhado para capturar erro 422
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
APONTAMENTO_URL = f"{BASE_URL}/api/desenvolvimento/os/apontamentos"

def fazer_login():
    """Fazer login e obter cookies de sessão"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_422_detalhado(cookies):
    """Testar com dados que podem causar 422"""
    
    # Teste com dados que podem ter problemas de validação
    dados_problematicos = {
        "numero_os": "20611",  # OS que sabemos que existe
        "status_os": "FINALIZADO",
        "cliente": "VALE SA",
        "equipamento": "MOTOR CA 315D 300CV B3E",
        "tipo_maquina": "MAQUINA ROTATIVA CA",
        "tipo_atividade": "TESTES PARCIAIS",
        "descricao_atividade": "TESTE DE CARGA NOMINAL",
        "categoria_maquina": "MOTOR DE INDUCAO TRIFASICO ROTOR GAIOLA",
        "subcategorias_maquina": ["Núcleo"],  # Lista que pode causar problema
        "data_inicio": "2025-09-28",
        "hora_inicio": "21:18",
        "data_fim": "2025-09-28",
        "hora_fim": "21:24",
        "retrabalho": True,
        "causa_retrabalho": "CAL001",
        "observacao_geral": "TESTE",
        "resultado_global": "APROVADO",
        "usuario_id": 2,
        "departamento": "MOTORES",
        "setor": "LABORATORIO DE ENSAIOS ELETRICOS",
        "testes_selecionados": {},
        "testes_exclusivos_selecionados": {},
        "tipo_salvamento": "APONTAMENTO",
        "supervisor_config": {
            "horas_orcadas": 0,
            "testes_iniciais": False,
            "testes_parciais": False,
            "testes_finais": False
        }
    }
    
    print(f"\n🔍 Testando dados problemáticos:")
    print(f"📋 Dados: {json.dumps(dados_problematicos, indent=2)}")
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_problematicos,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta completa: {response.text}")
        
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"🔍 Detalhes do erro 422:")
                for error in error_detail.get('detail', []):
                    print(f"   - Campo: {error.get('loc', 'N/A')}")
                    print(f"   - Tipo: {error.get('type', 'N/A')}")
                    print(f"   - Mensagem: {error.get('msg', 'N/A')}")
                    print(f"   - Input: {error.get('input', 'N/A')}")
                    print()
            except:
                print("❌ Não foi possível parsear detalhes do erro")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Capturar erro 422 detalhado")
    print("=" * 60)
    
    cookies = fazer_login()
    if not cookies:
        return
    
    testar_422_detalhado(cookies)
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
