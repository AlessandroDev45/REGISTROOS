#!/usr/bin/env python3
"""
Teste para verificar se o Dashboard está exibindo corretamente a hora fim
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
APONTAMENTO_URL = f"{BASE_URL}/api/save-apontamento"
DASHBOARD_URL = f"{BASE_URL}/api/apontamentos-detalhados"

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
        print(response.text)
        return None

def criar_apontamento_teste():
    """Criar apontamento de teste com data/hora fim"""
    print("\n🧪 Criando apontamento de teste...")
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return None
    
    # Preparar dados do apontamento
    agora = datetime.now()
    inicio = agora - timedelta(hours=3)  # 3 horas atrás
    fim = agora - timedelta(minutes=15)  # 15 minutos atrás
    
    apontamento_data = {
        "inpNumOS": f"DASH-{agora.strftime('%H%M%S')}",
        "statusOS": "EM_ANDAMENTO",
        "inpCliente": "Cliente Dashboard Test",
        "inpEquipamento": "Equipamento Dashboard Test",
        "selMaq": "MOTOR",
        "selAtiv": "INSTALACAO",
        "selDescAtiv": "Teste Dashboard - Verificar hora fim",
        "categoriaSelecionada": "ELETRICA",
        "subcategoriasSelecionadas": "MOTOR_TRIFASICO",
        "inpData": inicio.strftime("%Y-%m-%d"),
        "inpHora": inicio.strftime("%H:%M"),
        "inpDataFim": fim.strftime("%Y-%m-%d"),
        "inpHoraFim": fim.strftime("%H:%M"),
        "inpRetrabalho": False,
        "observacao_geral": "Teste Dashboard - Verificar se hora fim aparece corretamente",
        "resultado_global": "APROVADO"
    }
    
    print(f"📅 Data/Hora Início: {inicio.strftime('%Y-%m-%d %H:%M')}")
    print(f"📅 Data/Hora Fim: {fim.strftime('%Y-%m-%d %H:%M')}")
    
    try:
        response = requests.post(APONTAMENTO_URL, json=apontamento_data, cookies=cookies)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Apontamento criado com sucesso!")
            print(f"   ID: {result.get('apontamento_id')}")
            return result.get('apontamento_id'), cookies
        else:
            print(f"❌ Erro ao criar apontamento: {response.status_code}")
            print(response.text)
            return None, None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None, None

def verificar_dashboard(cookies):
    """Verificar se o dashboard retorna os dados com hora fim"""
    print("\n🔍 Verificando dados do dashboard...")
    
    try:
        response = requests.get(DASHBOARD_URL, cookies=cookies)
        
        if response.status_code == 200:
            apontamentos = response.json()
            print(f"✅ Dashboard retornou {len(apontamentos)} apontamentos")
            
            # Verificar os últimos 3 apontamentos
            for i, apt in enumerate(apontamentos[:3]):
                print(f"\n📋 Apontamento {i+1}:")
                print(f"   ID: {apt.get('id')}")
                print(f"   OS: {apt.get('numero_os')}")
                print(f"   data_hora_inicio: {apt.get('data_hora_inicio')}")
                print(f"   data_hora_fim: {apt.get('data_hora_fim')}")
                print(f"   tempo_trabalhado: {apt.get('tempo_trabalhado')}")
                print(f"   status: {apt.get('status_apontamento')}")
                
                if apt.get('data_hora_fim'):
                    print("   ✅ data_hora_fim presente!")
                else:
                    print("   ❌ data_hora_fim ausente!")
            
            return True
        else:
            print(f"❌ Erro ao buscar dashboard: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Dashboard - Hora Fim")
    print("=" * 50)
    
    # Criar apontamento de teste
    apontamento_id, cookies = criar_apontamento_teste()
    
    if apontamento_id and cookies:
        # Verificar dashboard
        verificar_dashboard(cookies)
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")
    print("\n💡 Para verificar no frontend:")
    print("   1. Acesse http://localhost:3001")
    print("   2. Vá para 'Desenvolvimento' > 'Meu Dashboard'")
    print("   3. Verifique se a coluna 'Fim' mostra a hora corretamente")

if __name__ == "__main__":
    main()
