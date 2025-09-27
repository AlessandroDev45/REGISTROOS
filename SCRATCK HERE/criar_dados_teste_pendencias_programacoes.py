#!/usr/bin/env python3
"""
Script para criar dados de teste para pendências e programações
Usa dados reais da API: ordens de serviço, clientes, equipamentos e usuários
"""

import requests
import json
import random
from datetime import datetime, timedelta
import sys

# Configurações da API
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Token de autenticação (substitua por um token válido)
AUTH_TOKEN = "seu_token_aqui"

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def fazer_requisicao(method, endpoint, data=None):
    """Função auxiliar para fazer requisições à API"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=HEADERS, json=data)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ Erro na requisição {method} {endpoint}: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def buscar_dados_base():
    """Busca dados base da API para criar testes"""
    print("🔍 Buscando dados base da API...")
    
    dados = {
        "ordens_servico": [],
        "usuarios": [],
        "clientes": [],
        "equipamentos": [],
        "setores": []
    }
    
    # Buscar ordens de serviço
    print("   📋 Buscando ordens de serviço...")
    os_data = fazer_requisicao("GET", "/os")
    if os_data:
        dados["ordens_servico"] = os_data[:10]  # Limitar a 10 para teste
        print(f"   ✅ {len(dados['ordens_servico'])} ordens de serviço encontradas")
    
    # Buscar usuários
    print("   👥 Buscando usuários...")
    users_data = fazer_requisicao("GET", "/admin/usuarios")
    if users_data:
        dados["usuarios"] = users_data[:20]  # Limitar a 20 para teste
        print(f"   ✅ {len(dados['usuarios'])} usuários encontrados")
    
    # Buscar clientes
    print("   🏢 Buscando clientes...")
    clientes_data = fazer_requisicao("GET", "/clientes")
    if clientes_data:
        dados["clientes"] = clientes_data[:10]  # Limitar a 10 para teste
        print(f"   ✅ {len(dados['clientes'])} clientes encontrados")
    
    # Buscar equipamentos
    print("   🔧 Buscando equipamentos...")
    equipamentos_data = fazer_requisicao("GET", "/equipamentos")
    if equipamentos_data:
        dados["equipamentos"] = equipamentos_data[:10]  # Limitar a 10 para teste
        print(f"   ✅ {len(dados['equipamentos'])} equipamentos encontrados")
    
    # Buscar setores
    print("   🏭 Buscando setores...")
    setores_data = fazer_requisicao("GET", "/setores")
    if setores_data:
        dados["setores"] = setores_data[:10]  # Limitar a 10 para teste
        print(f"   ✅ {len(dados['setores'])} setores encontrados")
    
    return dados

def criar_apontamento_teste(os_numero, usuario_id):
    """Cria um apontamento de teste para gerar pendência"""
    print(f"   📝 Criando apontamento para OS {os_numero}...")
    
    apontamento_data = {
        "numero_os": os_numero,
        "cliente": "Cliente Teste",
        "equipamento": "Equipamento Teste",
        "tipo_maquina": "TIPO_TESTE",
        "tipo_atividade": "MANUTENCAO",
        "descricao_atividade": "Atividade de teste",
        "data_inicio": datetime.now().strftime("%Y-%m-%d"),
        "hora_inicio": "08:00",
        "data_fim": datetime.now().strftime("%Y-%m-%d"),
        "hora_fim": "17:00",
        "observacao": "Apontamento criado para teste de pendência",
        "resultado_global": "PENDENTE",
        "usuario_id": usuario_id
    }
    
    return fazer_requisicao("POST", "/desenvolvimento/os/apontamentos", apontamento_data)

def criar_pendencias_teste(dados):
    """Cria pendências de teste"""
    print("📋 Criando pendências de teste...")
    
    if not dados["ordens_servico"] or not dados["usuarios"]:
        print("❌ Dados insuficientes para criar pendências")
        return []
    
    pendencias_criadas = []
    tipos_maquina = ["BOMBA_CENTRIFUGA", "MOTOR_ELETRICO", "COMPRESSOR", "TURBINA", "GERADOR"]
    prioridades = ["BAIXA", "NORMAL", "ALTA", "URGENTE"]
    
    for i in range(5):  # Criar 5 pendências
        try:
            os = random.choice(dados["ordens_servico"])
            usuario = random.choice(dados["usuarios"])
            
            # Primeiro criar um apontamento para ter origem da pendência
            apontamento = criar_apontamento_teste(os.get("os_numero", f"TEST{i+1:03d}"), usuario.get("id"))
            
            if not apontamento:
                print(f"   ❌ Falha ao criar apontamento para pendência {i+1}")
                continue
            
            # Criar pendência via endpoint de apontamento com pendência
            pendencia_data = {
                "inpNumOS": os.get("os_numero", f"TEST{i+1:03d}"),
                "inpCliente": random.choice(dados.get("clientes", [{"razao_social": "Cliente Teste"}])).get("razao_social", "Cliente Teste"),
                "inpEquipamento": random.choice(dados.get("equipamentos", [{"nome": "Equipamento Teste"}])).get("nome", "Equipamento Teste"),
                "selMaq": random.choice(tipos_maquina),
                "observacao": f"Pendência de teste #{i+1} - Problema identificado durante manutenção",
                "pendencia_descricao": f"Descrição detalhada da pendência {i+1}: Necessário verificar componente X",
                "pendencia_prioridade": random.choice(prioridades),
                "inpData": datetime.now().strftime("%Y-%m-%d"),
                "inpHora": "08:00",
                "inpDataFim": datetime.now().strftime("%Y-%m-%d"),
                "inpHoraFim": "17:00"
            }
            
            resultado = fazer_requisicao("POST", "/apontamentos-pendencia", pendencia_data)
            
            if resultado:
                pendencias_criadas.append(resultado)
                print(f"   ✅ Pendência {i+1} criada: ID {resultado.get('pendencia_id')}")
            else:
                print(f"   ❌ Falha ao criar pendência {i+1}")
                
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    print(f"✅ {len(pendencias_criadas)} pendências criadas com sucesso")
    return pendencias_criadas

def criar_programacoes_teste(dados):
    """Cria programações de teste"""
    print("📅 Criando programações de teste...")
    
    if not dados["ordens_servico"] or not dados["usuarios"] or not dados["setores"]:
        print("❌ Dados insuficientes para criar programações")
        return []
    
    programacoes_criadas = []
    
    # Filtrar usuários PCP (assumindo que têm privilege_level ADMIN ou SUPERVISOR)
    usuarios_pcp = [u for u in dados["usuarios"] if u.get("privilege_level") in ["ADMIN", "SUPERVISOR"]]
    if not usuarios_pcp:
        usuarios_pcp = dados["usuarios"][:3]  # Usar os primeiros 3 se não houver PCP
    
    for i in range(3):  # Criar 3 programações
        try:
            os = random.choice(dados["ordens_servico"])
            usuario_pcp = random.choice(usuarios_pcp)
            usuario_responsavel = random.choice(dados["usuarios"])
            setor = random.choice(dados["setores"])
            
            inicio_previsto = datetime.now() + timedelta(days=random.randint(1, 7))
            fim_previsto = inicio_previsto + timedelta(days=random.randint(1, 5))
            
            programacao_data = {
                "os_numero": os.get("os_numero", f"PROG{i+1:03d}"),
                "inicio_previsto": inicio_previsto.isoformat(),
                "fim_previsto": fim_previsto.isoformat(),
                "id_setor": setor.get("id", 1),
                "responsavel_id": usuario_responsavel.get("id"),
                "observacoes": f"Programação de teste #{i+1} - Manutenção preventiva programada",
                "prioridade": random.choice(["BAIXA", "NORMAL", "ALTA"]),
                "status": "PROGRAMADA"
            }
            
            resultado = fazer_requisicao("POST", "/pcp/programacoes", programacao_data)
            
            if resultado:
                programacoes_criadas.append(resultado)
                print(f"   ✅ Programação {i+1} criada: ID {resultado.get('id')}")
            else:
                print(f"   ❌ Falha ao criar programação {i+1}")
                
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    print(f"✅ {len(programacoes_criadas)} programações criadas com sucesso")
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 Iniciando criação de dados de teste...")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está respondendo corretamente")
            sys.exit(1)
    except:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        sys.exit(1)
    
    # Buscar dados base
    dados = buscar_dados_base()
    
    if not any(dados.values()):
        print("❌ Nenhum dado base encontrado. Verifique a API.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Criar pendências
    pendencias = criar_pendencias_teste(dados)
    
    print("\n" + "=" * 60)
    
    # Criar programações
    programacoes = criar_programacoes_teste(dados)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA CRIAÇÃO DE DADOS")
    print("=" * 60)
    print(f"📋 Pendências criadas: {len(pendencias)}")
    print(f"📅 Programações criadas: {len(programacoes)}")
    
    if pendencias:
        print("\n📋 Pendências:")
        for p in pendencias:
            print(f"   - ID: {p.get('pendencia_id')} | OS: {p.get('numero_os', 'N/A')}")
    
    if programacoes:
        print("\n📅 Programações:")
        for p in programacoes:
            print(f"   - ID: {p.get('id')} | Status: {p.get('status', 'N/A')}")
    
    print("\n🎉 Dados de teste criados com sucesso!")
    print("\nPara testar as funcionalidades:")
    print("1. Acesse a aba 'Pendências' para ver as pendências criadas")
    print("2. Teste o botão 'Resolver via Apontamento'")
    print("3. Acesse a aba 'Programação' para ver as programações")
    print("4. Teste a criação de apontamentos para OSs com programação")

if __name__ == "__main__":
    main()
