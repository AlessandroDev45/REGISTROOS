#!/usr/bin/env python3
"""
Teste exato do comportamento do frontend
"""

import requests
import time

def test_frontend_exact():
    """Simula exatamente o que o frontend está fazendo"""
    session = requests.Session()
    
    try:
        print("🔐 Simulando login exato do frontend...")
        
        # 1. Primeiro, fazer login como o frontend faz (via /token)
        login_data = {
            'username': 'user.laboratorio_de_ensaios_eletricos@registroos.com',
            'password': '123456'
        }
        
        response = session.post(
            'http://localhost:3001/api/token',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # 2. Verificar se o usuário tem as mesmas permissões
            me_response = session.get('http://localhost:3001/api/me')
            print(f"Me endpoint: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"👤 Usuário: {user_data.get('nome_completo')}")
                print(f"🏢 Setor: {user_data.get('setor')}")
                print(f"🔑 Privilege: {user_data.get('privilege_level')}")
                
                # 3. Tentar acessar o relatório como o frontend
                print(f"\n📊 Testando relatório para OS 6...")
                
                start_time = time.time()
                response = session.get(
                    'http://localhost:3001/api/os/6/relatorio-completo',
                    timeout=30  # Timeout de 30 segundos
                )
                end_time = time.time()
                
                print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Dados recebidos: {len(data)} campos")
                    
                    # Verificar se todos os campos necessários estão presentes
                    required_fields = [
                        'os_dados_gerais',
                        'resumo_gerencial',
                        'apontamentos_por_setor',
                        'resultados_testes',
                        'metricas_consolidadas'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"❌ Campos faltando: {missing_fields}")
                    else:
                        print("✅ Todos os campos necessários estão presentes")
                        
                        # Verificar se resumo_gerencial tem os campos necessários
                        resumo = data.get('resumo_gerencial', {})
                        resumo_fields = ['status_os', 'status_prazo', 'desvio_percentual']
                        
                        for field in resumo_fields:
                            if field in resumo:
                                print(f"  ✅ {field}: {resumo[field]}")
                            else:
                                print(f"  ❌ {field}: FALTANDO")
                    
                    return True
                    
                elif response.status_code == 401:
                    print("❌ Erro de autenticação - usuário não tem permissão")
                    return False
                elif response.status_code == 403:
                    print("❌ Erro de autorização - acesso negado")
                    return False
                elif response.status_code == 404:
                    print("❌ Rota não encontrada")
                    return False
                elif response.status_code == 500:
                    print(f"❌ Erro interno do servidor: {response.text[:200]}")
                    return False
                else:
                    print(f"❌ Status inesperado: {response.status_code}")
                    print(f"Resposta: {response.text[:200]}")
                    return False
            else:
                print(f"❌ Erro ao verificar usuário: {me_response.status_code}")
                return False
        else:
            print(f"❌ Erro no login: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição - servidor pode estar sobrecarregado")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - servidor pode estar offline")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_exact()
    if success:
        print("\n🎉 FRONTEND DEVERIA FUNCIONAR!")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO")
        print("💡 Verificar logs do servidor e console do navegador")
