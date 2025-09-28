#!/usr/bin/env python3
"""
Teste para verificar se a data/hora fim está sendo salva corretamente
na coluna data_hora_fim da tabela apontamentos_detalhados
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
APONTAMENTO_URL = f"{BASE_URL}/api/save-apontamento"

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

def testar_apontamento_com_data_hora_fim():
    """Testar criação de apontamento com data e hora fim"""
    print("\n🧪 Testando apontamento com data/hora fim...")
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return
    
    # Preparar dados do apontamento
    agora = datetime.now()
    inicio = agora - timedelta(hours=2)  # 2 horas atrás
    fim = agora - timedelta(minutes=30)  # 30 minutos atrás
    
    apontamento_data = {
        "inpNumOS": f"TEST-{agora.strftime('%H%M%S')}",
        "statusOS": "EM_ANDAMENTO",
        "inpCliente": "Cliente Teste",
        "inpEquipamento": "Equipamento Teste",
        "selMaq": "BOMBA",
        "selAtiv": "MANUTENCAO",
        "selDescAtiv": "Teste de data/hora fim",
        "categoriaSelecionada": "HIDRAULICA",
        "subcategoriasSelecionadas": "BOMBA_CENTRIFUGA",
        "inpData": inicio.strftime("%Y-%m-%d"),
        "inpHora": inicio.strftime("%H:%M"),
        "inpDataFim": fim.strftime("%Y-%m-%d"),
        "inpHoraFim": fim.strftime("%H:%M"),
        "inpRetrabalho": False,
        "observacao_geral": "Teste de data/hora fim - verificar se está sendo salva corretamente",
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
            print(f"   OS: {result.get('numero_os')}")
            
            # Verificar se retornou informações sobre data_hora_fim
            if 'data_hora_fim' in result:
                print(f"   Data/Hora Fim salva: {result['data_hora_fim']}")
            
            return result.get('apontamento_id')
        else:
            print(f"❌ Erro ao criar apontamento: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def verificar_banco_dados(apontamento_id):
    """Verificar diretamente no banco se a data_hora_fim foi salva"""
    if not apontamento_id:
        return
        
    print(f"\n🔍 Verificando apontamento {apontamento_id} no banco...")
    
    try:
        import sys
        import os
        
        # Adicionar caminho do backend
        backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
        sys.path.append(backend_path)
        
        from config.database_config import get_db
        from app.database_models import ApontamentoDetalhado
        
        # Conectar ao banco
        db = next(get_db())
        
        # Buscar apontamento
        apontamento = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.id == apontamento_id
        ).first()
        
        if apontamento:
            print(f"✅ Apontamento encontrado:")
            print(f"   ID: {apontamento.id}")
            print(f"   data_hora_inicio: {apontamento.data_hora_inicio}")
            print(f"   data_hora_fim: {apontamento.data_hora_fim}")
            print(f"   status_apontamento: {apontamento.status_apontamento}")
            
            if apontamento.data_hora_fim:
                print("✅ data_hora_fim foi salva corretamente!")
                
                # Calcular tempo trabalhado
                if apontamento.data_hora_inicio and apontamento.data_hora_fim:
                    delta = apontamento.data_hora_fim - apontamento.data_hora_inicio
                    horas = delta.total_seconds() / 3600
                    print(f"   Tempo trabalhado: {horas:.2f} horas")
            else:
                print("❌ data_hora_fim está NULL no banco!")
        else:
            print(f"❌ Apontamento {apontamento_id} não encontrado no banco")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE: Data/Hora Fim em Apontamentos")
    print("=" * 50)
    
    # Testar criação de apontamento
    apontamento_id = testar_apontamento_com_data_hora_fim()
    
    # Verificar no banco
    verificar_banco_dados(apontamento_id)
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
