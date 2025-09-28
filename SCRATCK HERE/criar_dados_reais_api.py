#!/usr/bin/env python3
"""
Script para criar dados reais usando a API:
- 15 Apontamentos
- 15 Pendências  
- 15 Programações
Todos com setores de produção reais
"""

import requests
import json
import sqlite3
import os
import random
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

# Credenciais para autenticação
ADMIN_EMAIL = "admin@registroos.com"
ADMIN_PASSWORD = "admin123"

# Variável global para armazenar o token
auth_token = None

def fazer_login():
    """Fazer login e obter token de autenticação"""
    global auth_token
    print("🔐 Fazendo login...")

    try:
        login_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }

        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data,  # Form data para login
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            print("✅ Login realizado com sucesso")
            return True
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return False

def get_headers():
    """Obter headers com autenticação"""
    if auth_token:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    else:
        return {"Content-Type": "application/json"}

def obter_setores_producao():
    """Obter setores de produção do banco de dados"""
    print("🏭 Obtendo setores de produção...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar setores ativos que trabalham com produção
        cursor.execute("""
            SELECT DISTINCT s.id, s.nome, s.departamento, s.id_departamento
            FROM tipo_setores s
            WHERE s.ativo = 1
            AND s.nome NOT LIKE '%COMERCIAL%'
            AND s.nome NOT LIKE '%GESTAO%'
            AND s.nome NOT LIKE '%ADMINISTRATIVO%'
            ORDER BY s.nome
        """)
        
        setores = cursor.fetchall()
        conn.close()
        
        print(f"✅ Encontrados {len(setores)} setores de produção:")
        for setor in setores:
            print(f"   - ID: {setor[0]} | {setor[1]} ({setor[2]})")
        
        return setores
        
    except Exception as e:
        print(f"❌ Erro ao obter setores: {e}")
        return []

def obter_usuarios_producao(setores):
    """Obter usuários dos setores de produção"""
    print("\n👥 Obtendo usuários de produção...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        setor_ids = [str(s[0]) for s in setores]
        
        cursor.execute(f"""
            SELECT id, nome_completo, email, setor, id_setor
            FROM tipo_usuarios
            WHERE id_setor IN ({','.join(setor_ids)})
            AND is_approved = 1
            ORDER BY nome_completo
        """)
        
        usuarios = cursor.fetchall()
        conn.close()
        
        print(f"✅ Encontrados {len(usuarios)} usuários de produção:")
        for usuario in usuarios[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - {usuario[1]} ({usuario[3]})")
        
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao obter usuários: {e}")
        return []

def gerar_numero_os():
    """Gerar número de OS aleatório"""
    return random.randint(20000, 99999)

def criar_apontamentos(usuarios, setores):
    """Criar 15 apontamentos usando a API"""
    print("\n📝 Criando apontamentos...")
    
    apontamentos_criados = []
    
    for i in range(15):
        try:
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            # Data aleatória nos últimos 30 dias
            data_base = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Dados do apontamento (modelo correto)
            numero_os = str(gerar_numero_os())
            hora_inicio = f"{random.randint(7, 16):02d}:{random.choice(['00', '30'])}"
            hora_fim_int = int(hora_inicio.split(':')[0]) + random.randint(1, 8)
            hora_fim = f"{min(hora_fim_int, 23):02d}:{random.choice(['00', '30'])}"

            apontamento_data = {
                "numero_os": numero_os,
                "cliente": f"Cliente {i+1}",
                "equipamento": f"Equipamento {setor[1][:10]}",
                "tipo_maquina": "PRODUCAO",
                "tipo_atividade": "MANUTENCAO",
                "descricao_atividade": f"Atividade de produção {i+1}",
                "data_inicio": data_base.strftime("%Y-%m-%d"),
                "hora_inicio": hora_inicio,
                "data_fim": data_base.strftime("%Y-%m-%d"),
                "hora_fim": hora_fim,
                "observacao": f"Apontamento {i+1} - {setor[1]}",
                "observacao_geral": f"Observação geral do apontamento {i+1}",
                "resultado_global": random.choice(["APROVADO", "APROVADO", "PENDENTE"]),
                "retrabalho": random.choice([False, False, False, True]),
                "setor": setor[1],
                "departamento": setor[2],
                "usuario_id": usuario[0]
            }
            
            # Fazer requisição para a API (endpoint correto)
            response = requests.post(
                f"{BASE_URL}/api/desenvolvimento/os/apontamentos",
                json=apontamento_data,
                headers=get_headers()
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Apontamento {i+1}/15 criado - OS {apontamento_data['numero_os']} ({setor[1]})")
                apontamentos_criados.append(apontamento_data)
            else:
                print(f"❌ Erro ao criar apontamento {i+1}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao criar apontamento {i+1}: {e}")
    
    return apontamentos_criados

def criar_pendencias(usuarios, setores):
    """Criar 15 pendências usando a API"""
    print("\n⚠️ Criando pendências...")
    
    pendencias_criadas = []
    
    tipos_pendencia = [
        "MATERIAL_FALTANTE",
        "EQUIPAMENTO_DEFEITO", 
        "DOCUMENTACAO_PENDENTE",
        "QUALIDADE_REJEITADA",
        "PROCESSO_BLOQUEADO"
    ]
    
    for i in range(15):
        try:
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            # Data aleatória nos últimos 15 dias
            data_base = datetime.now() - timedelta(days=random.randint(1, 15))
            
            # Dados da pendência
            pendencia_data = {
                "numero_os": gerar_numero_os(),
                "setor": setor[1],
                "tipo_pendencia": random.choice(tipos_pendencia),
                "descricao": f"Pendência {i+1} no setor {setor[1]} - {random.choice(['Material em falta', 'Equipamento com defeito', 'Documentação pendente', 'Problema de qualidade', 'Processo bloqueado'])}",
                "data_abertura": data_base.strftime("%Y-%m-%d"),
                "prioridade": random.choice(["BAIXA", "MEDIA", "ALTA"]),
                "status": random.choice(["ABERTA", "ABERTA", "ABERTA", "FECHADA"]),  # Maioria aberta
                "usuario_abertura_id": usuario[0]
            }
            
            # Se fechada, adicionar data de fechamento
            if pendencia_data["status"] == "FECHADA":
                data_fechamento = data_base + timedelta(days=random.randint(1, 10))
                pendencia_data["data_fechamento"] = data_fechamento.strftime("%Y-%m-%d")
                pendencia_data["solucao"] = f"Solução aplicada para pendência {i+1}"
            
            # Fazer requisição para a API (endpoint correto)
            response = requests.post(
                f"{BASE_URL}/api/pcp/pendencias",
                json=pendencia_data,
                headers=get_headers()
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Pendência {i+1}/15 criada - OS {pendencia_data['numero_os']} ({setor[1]}) - {pendencia_data['status']}")
                pendencias_criadas.append(pendencia_data)
            else:
                print(f"❌ Erro ao criar pendência {i+1}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao criar pendência {i+1}: {e}")
    
    return pendencias_criadas

def criar_programacoes(usuarios, setores):
    """Criar 15 programações usando a API"""
    print("\n📅 Criando programações...")
    
    programacoes_criadas = []
    
    for i in range(15):
        try:
            usuario = random.choice(usuarios)
            setor = next((s for s in setores if s[0] == usuario[4]), setores[0])
            
            # Data de início nos próximos 30 dias
            data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
            data_fim = data_inicio + timedelta(hours=random.randint(4, 16))
            
            # Dados da programação
            programacao_data = {
                "numero_os": gerar_numero_os(),
                "setor": setor[1],
                "descricao": f"Programação {i+1} - Atividade de produção no setor {setor[1]}",
                "inicio_previsto": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                "fim_previsto": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                "prioridade": random.choice(["BAIXA", "MEDIA", "ALTA"]),
                "status": random.choice(["PROGRAMADA", "PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA"]),
                "observacoes": f"Observações da programação {i+1} para o setor {setor[1]}",
                "usuario_responsavel_id": usuario[0]
            }
            
            # Fazer requisição para a API (endpoint correto)
            response = requests.post(
                f"{BASE_URL}/api/pcp/programacoes",
                json=programacao_data,
                headers=get_headers()
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Programação {i+1}/15 criada - OS {programacao_data['numero_os']} ({setor[1]}) - {programacao_data['status']}")
                programacoes_criadas.append(programacao_data)
            else:
                print(f"❌ Erro ao criar programação {i+1}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao criar programação {i+1}: {e}")
    
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 CRIANDO DADOS REAIS COM API")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Servidor API está rodando")
    except:
        print("❌ Servidor API não está rodando!")
        print("   Inicie o backend primeiro: uvicorn main:app --reload")
        return

    # Fazer login
    if not fazer_login():
        print("❌ Não foi possível fazer login!")
        return
    
    # Obter dados base
    setores = obter_setores_producao()
    if not setores:
        print("❌ Nenhum setor de produção encontrado!")
        return
    
    usuarios = obter_usuarios_producao(setores)
    if not usuarios:
        print("❌ Nenhum usuário de produção encontrado!")
        return
    
    # Criar registros
    print(f"\n🎯 Criando registros com {len(setores)} setores e {len(usuarios)} usuários...")
    
    apontamentos = criar_apontamentos(usuarios, setores)
    pendencias = criar_pendencias(usuarios, setores)
    programacoes = criar_programacoes(usuarios, setores)
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA CRIAÇÃO:")
    print(f"   ✅ Apontamentos criados: {len(apontamentos)}/15")
    print(f"   ✅ Pendências criadas: {len(pendencias)}/15")
    print(f"   ✅ Programações criadas: {len(programacoes)}/15")
    
    total_criados = len(apontamentos) + len(pendencias) + len(programacoes)
    print(f"\n🎉 Total de registros criados: {total_criados}/45")
    
    if total_criados == 45:
        print("✅ TODOS OS DADOS FORAM CRIADOS COM SUCESSO!")
    else:
        print("⚠️ Alguns registros não foram criados. Verifique os logs acima.")
    
    print("\n💡 Agora você pode:")
    print("1. Acessar o dashboard para ver os dados")
    print("2. Verificar os gráficos atualizados")
    print("3. Testar as funcionalidades com dados reais")

if __name__ == "__main__":
    main()
