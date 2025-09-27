#!/usr/bin/env python3
"""
DEBUG ENDPOINT MINHAS PROGRAMAÇÕES
=================================

Debug específico do endpoint /api/desenvolvimento/minhas-programacoes
para identificar onde está falhando.
"""

import requests
import sqlite3
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login como admin...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=ADMIN_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_endpoint_direto(session):
    """Testar o endpoint diretamente com logs detalhados"""
    print("\n🔍 Testando endpoint /api/desenvolvimento/minhas-programacoes...")
    
    try:
        # Fazer requisição com headers detalhados
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = session.get(
            f"{BASE_URL}/api/desenvolvimento/minhas-programacoes",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📋 Tipo de resposta: {type(data)}")
                print(f"📋 Dados retornados: {len(data) if isinstance(data, list) else 'Não é lista'}")
                
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        print(f"   Item {i+1}: {item}")
                else:
                    print(f"   Dados: {data}")
                    
                return data
            except Exception as e:
                print(f"❌ Erro ao parsear JSON: {e}")
                print(f"📄 Resposta raw: {response.text}")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def verificar_dados_banco_detalhado():
    """Verificar dados no banco com mais detalhes"""
    print("\n🔍 Verificando dados no banco com detalhes...")
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query exata do endpoint
        query = """
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor, p.historico,
                   os.os_numero, os.status_os, os.prioridade, u.nome_completo as responsavel_nome,
                   c.razao_social as cliente_nome, e.descricao as equipamento_descricao,
                   s.nome as setor_nome
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            WHERE p.responsavel_id = ?
            ORDER BY p.inicio_previsto DESC
            LIMIT 50
        """
        
        user_id = 1
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        print(f"📋 Query executada para user_id={user_id}")
        print(f"📊 Resultados encontrados: {len(results)}")
        
        for i, row in enumerate(results):
            print(f"\n📋 Resultado {i+1}:")
            print(f"   ID: {row[0]}")
            print(f"   OS ID: {row[1]}")
            print(f"   Responsável ID: {row[2]}")
            print(f"   Início: {row[3]}")
            print(f"   Fim: {row[4]}")
            print(f"   Status: {row[5]}")
            print(f"   Observações: {row[7]}")
            print(f"   Histórico: {row[11]}")
            print(f"   OS Número: {row[12]}")
            print(f"   Responsável Nome: {row[15]}")
            
            # Verificar se algum campo pode estar causando erro
            problemas = []
            if row[3] and not isinstance(row[3], str):
                try:
                    datetime.fromisoformat(str(row[3]))
                except:
                    problemas.append(f"inicio_previsto inválido: {row[3]}")
            
            if row[4] and not isinstance(row[4], str):
                try:
                    datetime.fromisoformat(str(row[4]))
                except:
                    problemas.append(f"fim_previsto inválido: {row[4]}")
            
            if problemas:
                print(f"   ⚠️ Problemas detectados: {problemas}")
        
        conn.close()
        return len(results)
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return 0

def criar_programacao_simples(session):
    """Criar uma programação mais simples para teste"""
    print("\n🧪 Criando programação simples para teste...")
    
    try:
        # Usar endpoint de atribuição que sabemos que funciona
        dados = {
            "responsavel_id": 1,
            "setor_destino": "MECANICA",
            "departamento_destino": "PRODUCAO",
            "data_inicio": "2025-01-15T08:00:00",
            "data_fim": "2025-01-15T17:00:00",
            "observacoes": "Teste debug endpoint"
        }
        
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/atribuir", json=dados)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação criada! ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Erro ao criar: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 DEBUG ENDPOINT MINHAS PROGRAMAÇÕES")
    print("=" * 50)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Verificar dados no banco
    count_banco = verificar_dados_banco_detalhado()
    
    # 3. Testar endpoint
    data_endpoint = testar_endpoint_direto(session)
    
    # 4. Se não há dados, criar programação simples
    if count_banco == 0:
        print("\n💡 Criando programação simples...")
        prog_id = criar_programacao_simples(session)
        
        if prog_id:
            print("\n🔄 Testando novamente após criação...")
            verificar_dados_banco_detalhado()
            testar_endpoint_direto(session)
    
    # 5. Resumo
    print(f"\n📊 RESUMO:")
    print(f"   Programações no banco: {count_banco}")
    print(f"   Endpoint funcionou: {'Sim' if data_endpoint is not None else 'Não'}")
    
    if count_banco > 0 and data_endpoint is None:
        print("\n⚠️ PROBLEMA CONFIRMADO:")
        print("   - Dados existem no banco")
        print("   - Endpoint não retorna dados")
        print("   - Possível erro no processamento Python")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Verificar logs do backend")
        print("   2. Adicionar mais debug no endpoint")
        print("   3. Testar query SQL isoladamente")

if __name__ == "__main__":
    main()
