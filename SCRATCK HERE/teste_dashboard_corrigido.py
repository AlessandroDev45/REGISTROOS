#!/usr/bin/env python3
"""
Teste para verificar se a correção do Dashboard está funcionando
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
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

def simular_frontend_mapping(cookies):
    """Simular o mapeamento que o frontend faz"""
    print(f"\n🔍 Simulando mapeamento do frontend...")
    
    try:
        response = requests.get(DASHBOARD_URL, cookies=cookies)
        
        if response.status_code == 200:
            api_data = response.json()
            print(f"✅ API retornou {len(api_data)} apontamentos")
            
            if len(api_data) > 0:
                # Simular o mapeamento do frontend
                apontamentos_convertidos = []
                
                for apt in api_data:
                    convertido = {
                        'id': apt.get('id'),
                        'numero_os': apt.get('numero_os') or f"APT-{apt.get('id')}",
                        'cliente': apt.get('cliente') or 'Cliente não informado',
                        'equipamento': apt.get('equipamento') or 'Equipamento não informado',
                        'data_hora_inicio': apt.get('data_hora_inicio') or apt.get('data_inicio'),
                        'data_hora_fim': apt.get('data_hora_fim') or apt.get('data_fim'),
                        'tempo_trabalhado': apt.get('tempo_trabalhado'),
                        'tipo_atividade': apt.get('tipo_atividade') or 'N/A',
                        'descricao_atividade': apt.get('descricao_atividade') or 'N/A',
                        'status_apontamento': apt.get('status_apontamento') or apt.get('status') or 'N/A',
                        'setor': apt.get('setor') or 'N/A',
                        'departamento': apt.get('departamento') or 'N/A',
                        'nome_tecnico': apt.get('nome_tecnico') or apt.get('usuario') or 'N/A',
                        'aprovado_supervisor': apt.get('aprovado_supervisor') or False,
                        'foi_retrabalho': apt.get('foi_retrabalho') or False,
                        'servico_de_campo': apt.get('servico_de_campo') or False,
                        'observacoes': apt.get('observacoes') or '',
                        'observacao_os': apt.get('observacao_os') or '',
                        'causa_retrabalho': apt.get('causa_retrabalho') or '',
                        'data_aprovacao_supervisor': apt.get('data_aprovacao_supervisor')
                    }
                    apontamentos_convertidos.append(convertido)
                
                print(f"\n📋 Resultado do mapeamento:")
                print(f"   Total convertidos: {len(apontamentos_convertidos)}")
                
                # Verificar primeiro apontamento
                if len(apontamentos_convertidos) > 0:
                    primeiro = apontamentos_convertidos[0]
                    print(f"\n   📝 Primeiro apontamento mapeado:")
                    print(f"      ID: {primeiro['id']}")
                    print(f"      OS: {primeiro['numero_os']}")
                    print(f"      Cliente: {primeiro['cliente']}")
                    print(f"      Equipamento: {primeiro['equipamento']}")
                    print(f"      Data/Hora Início: {primeiro['data_hora_inicio']}")
                    print(f"      Data/Hora Fim: {primeiro['data_hora_fim']}")
                    print(f"      Status: {primeiro['status_apontamento']}")
                    print(f"      Técnico: {primeiro['nome_tecnico']}")
                    print(f"      Tempo Trabalhado: {primeiro['tempo_trabalhado']}")
                    
                    # Verificar se campos críticos estão preenchidos
                    campos_criticos = ['data_hora_inicio', 'data_hora_fim', 'status_apontamento', 'nome_tecnico']
                    problemas = []
                    
                    for campo in campos_criticos:
                        valor = primeiro[campo]
                        if valor is None or valor == 'N/A' or valor == '':
                            problemas.append(campo)
                    
                    if problemas:
                        print(f"\n   ⚠️ Campos com problemas: {', '.join(problemas)}")
                    else:
                        print(f"\n   ✅ Todos os campos críticos estão preenchidos!")
                
                return True
            else:
                print("   ⚠️ Nenhum apontamento retornado pela API")
                return False
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def verificar_campos_especificos(cookies):
    """Verificar campos específicos que estavam com problema"""
    print(f"\n🔍 Verificando campos específicos...")
    
    try:
        response = requests.get(DASHBOARD_URL, cookies=cookies)
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 0:
                apt = data[0]
                
                print(f"   📋 Campos da API:")
                print(f"      data_hora_inicio: {apt.get('data_hora_inicio')}")
                print(f"      data_inicio: {apt.get('data_inicio')}")
                print(f"      data_hora_fim: {apt.get('data_hora_fim')}")
                print(f"      data_fim: {apt.get('data_fim')}")
                print(f"      status_apontamento: {apt.get('status_apontamento')}")
                print(f"      status: {apt.get('status')}")
                print(f"      nome_tecnico: {apt.get('nome_tecnico')}")
                print(f"      usuario: {apt.get('usuario')}")
                
                # Verificar se o mapeamento funcionará
                data_hora_inicio = apt.get('data_hora_inicio') or apt.get('data_inicio')
                data_hora_fim = apt.get('data_hora_fim') or apt.get('data_fim')
                status = apt.get('status_apontamento') or apt.get('status')
                nome_tecnico = apt.get('nome_tecnico') or apt.get('usuario')
                
                print(f"\n   🔄 Após mapeamento:")
                print(f"      data_hora_inicio: {data_hora_inicio}")
                print(f"      data_hora_fim: {data_hora_fim}")
                print(f"      status_apontamento: {status}")
                print(f"      nome_tecnico: {nome_tecnico}")
                
                if all([data_hora_inicio, status, nome_tecnico]):
                    print(f"\n   ✅ Mapeamento funcionará corretamente!")
                    if data_hora_fim:
                        print(f"   ✅ Data/hora fim também está presente!")
                    else:
                        print(f"   ⚠️ Data/hora fim está ausente (normal para apontamentos em andamento)")
                else:
                    print(f"\n   ❌ Mapeamento tem problemas!")
                
                return True
            else:
                print("   ⚠️ Nenhum apontamento para verificar")
                return False
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Dashboard Corrigido - Mapeamento de Campos")
    print("=" * 60)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return
    
    # Verificar campos específicos
    verificar_campos_especificos(cookies)
    
    # Simular mapeamento do frontend
    sucesso = simular_frontend_mapping(cookies)
    
    print("\n" + "=" * 60)
    if sucesso:
        print("🏁 ✅ Teste concluído com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Acesse o frontend em http://localhost:3001")
        print("   2. Vá para 'Desenvolvimento' > 'Meu Dashboard'")
        print("   3. Verifique se os apontamentos aparecem corretamente")
        print("   4. Confirme se a coluna 'Fim' mostra as horas")
    else:
        print("🏁 ❌ Teste encontrou problemas!")
        print("\n💡 Possíveis soluções:")
        print("   1. Verificar se há apontamentos no banco")
        print("   2. Verificar logs do backend")
        print("   3. Verificar autenticação")

if __name__ == "__main__":
    main()
