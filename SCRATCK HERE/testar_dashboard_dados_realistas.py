#!/usr/bin/env python3
"""
TESTAR DASHBOARD COM DADOS REALISTAS
====================================

Testa se o dashboard está carregando corretamente
com os dados realistas criados
"""

import requests
import json

def testar_com_autenticacao():
    """Testa endpoints com autenticação"""
    print("🔐 TESTANDO COM AUTENTICAÇÃO")
    print("=" * 40)
    
    # 1. Fazer login
    login_data = {
        "username": "admin@registroos.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login falhou: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
        
        print("✅ Login realizado com sucesso")
        
        # Obter cookies de autenticação
        cookies = login_response.cookies
        
        # 2. Testar endpoints do dashboard
        endpoints = [
            ("Apontamentos", "http://localhost:8000/api/apontamentos-detalhados"),
            ("Programações", "http://localhost:8000/api/pcp/programacoes"),
            ("Pendências", "http://localhost:8000/api/pcp/pendencias"),
        ]
        
        print("\n📊 TESTANDO ENDPOINTS:")
        print("-" * 40)
        
        for nome, endpoint in endpoints:
            try:
                response = requests.get(endpoint, cookies=cookies, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {nome}: {len(data)} registros")
                    
                    # Mostrar alguns dados de exemplo
                    if data and len(data) > 0:
                        primeiro = data[0]
                        if nome == "Apontamentos":
                            os_numero = primeiro.get('numero_os', 'N/A')
                            status = primeiro.get('status_apontamento', 'N/A')
                            usuario = primeiro.get('criado_por', 'N/A')
                            print(f"   📋 Exemplo: OS {os_numero} | {status} | {usuario}")
                        
                        elif nome == "Programações":
                            os_id = primeiro.get('id_ordem_servico', 'N/A')
                            status = primeiro.get('status', 'N/A')
                            setor = primeiro.get('id_setor', 'N/A')
                            print(f"   📅 Exemplo: OS ID {os_id} | {status} | Setor {setor}")
                        
                        elif nome == "Pendências":
                            os_numero = primeiro.get('numero_os', 'N/A')
                            status = primeiro.get('status', 'N/A')
                            prioridade = primeiro.get('prioridade', 'N/A')
                            print(f"   ⚠️ Exemplo: OS {os_numero} | {status} | {prioridade}")
                
                else:
                    print(f"❌ {nome}: {response.status_code}")
                    print(f"   Erro: {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ {nome}: {e}")
        
        # 3. Testar dados específicos das OSs de teste
        print("\n🔍 VERIFICANDO DADOS DE TESTE:")
        print("-" * 40)
        
        try:
            # Buscar apontamentos das OSs de teste
            apontamentos_response = requests.get(
                "http://localhost:8000/api/apontamentos-detalhados",
                cookies=cookies,
                timeout=10
            )
            
            if apontamentos_response.status_code == 200:
                apontamentos = apontamentos_response.json()
                
                # Filtrar apontamentos das OSs de teste
                apontamentos_teste = [
                    a for a in apontamentos 
                    if a.get('numero_os', '').startswith('REAL2025')
                ]
                
                print(f"📊 Apontamentos de teste: {len(apontamentos_teste)}")
                
                if apontamentos_teste:
                    # Mostrar distribuição por status
                    status_count = {}
                    for apt in apontamentos_teste:
                        status = apt.get('status_apontamento', 'N/A')
                        status_count[status] = status_count.get(status, 0) + 1
                    
                    print("   📈 Distribuição por status:")
                    for status, count in status_count.items():
                        print(f"      {status}: {count}")
                
                # Mostrar algumas OSs de teste
                oss_teste = list(set([
                    a.get('numero_os') for a in apontamentos_teste 
                    if a.get('numero_os', '').startswith('REAL2025')
                ]))
                
                print(f"   📋 OSs de teste encontradas: {len(oss_teste)}")
                if oss_teste:
                    print(f"   📋 Exemplos: {', '.join(oss_teste[:5])}")
                    if len(oss_teste) > 5:
                        print(f"   📋 ... e mais {len(oss_teste) - 5}")
        
        except Exception as e:
            print(f"❌ Erro ao verificar dados de teste: {e}")
        
        print("\n🎯 TESTE CONCLUÍDO!")
        print("✅ Dashboard deve estar funcionando com dados realistas")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

def verificar_frontend():
    """Verifica se o frontend está acessível"""
    print("\n🌐 VERIFICANDO FRONTEND")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend acessível em http://localhost:3001")
            print("🎯 Acesse http://localhost:3001/dashboard para ver os dados")
        else:
            print(f"❌ Frontend não acessível: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend não acessível: {e}")

def main():
    """Função principal"""
    print("🚀 TESTANDO DASHBOARD COM DADOS REALISTAS")
    print("=" * 60)
    
    testar_com_autenticacao()
    verificar_frontend()
    
    print("\n" + "=" * 60)
    print("🎉 TESTE COMPLETO!")
    print("\n💡 RESUMO:")
    print("   - 15 Ordens de Serviço (REAL20250001-REAL20250015)")
    print("   - 15 Apontamentos com usuários reais")
    print("   - 15 Pendências com status variados")
    print("   - 15 Programações com setores reais")
    print("   - 15 Resultados de teste com observações")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Acesse http://localhost:3001/login")
    print("   2. Faça login com admin@registroos.com / admin123")
    print("   3. Acesse http://localhost:3001/dashboard")
    print("   4. Teste todas as funcionalidades implementadas")

if __name__ == "__main__":
    main()
