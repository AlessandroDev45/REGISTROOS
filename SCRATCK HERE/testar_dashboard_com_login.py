#!/usr/bin/env python3
"""
Testa o Dashboard com login automático
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def testar_dashboard_completo():
    """Testa todos os endpoints do Dashboard com autenticação"""
    print("🔐 Testando Dashboard com autenticação...")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login automático
    print("\n1. 🔑 Fazendo login automático...")
    try:
        login_response = session.post(f"{BASE_URL}/api/test-login/admin@registroos.com")
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            print(f"   ✅ Login realizado: {user_data['user']['nome_completo']}")
            print(f"   👤 Privilégio: {user_data['user']['privilege_level']}")
            print(f"   🏢 Setor: {user_data['user']['setor']}")
        else:
            print(f"   ❌ Falha no login: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Erro no login: {e}")
        return
    
    # 2. Testar endpoints do Dashboard
    print("\n2. 📊 Testando endpoints do Dashboard...")
    
    endpoints = [
        ("/api/apontamentos-detalhados", "Apontamentos Detalhados"),
        ("/api/pcp/programacoes", "Programações PCP"),
        ("/api/pcp/pendencias", "Pendências PCP"),
        ("/api/departamentos", "Departamentos"),
        ("/api/setores", "Setores")
    ]
    
    resultados = {}
    
    for endpoint, nome in endpoints:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    count = len(data)
                    resultados[endpoint] = {"status": "OK", "count": count}
                    print(f"   ✅ {nome}: {count} itens")
                    
                    # Mostrar alguns dados de exemplo
                    if count > 0 and count <= 3:
                        for i, item in enumerate(data, 1):
                            if isinstance(item, dict):
                                # Mostrar campos principais
                                id_field = item.get('id', item.get('numero_os', 'N/A'))
                                print(f"      {i}. ID/OS: {id_field}")
                else:
                    resultados[endpoint] = {"status": "OK", "type": "object"}
                    print(f"   ✅ {nome}: OK (objeto)")
                    
            else:
                resultados[endpoint] = {"status": "ERROR", "code": response.status_code}
                print(f"   ❌ {nome}: Erro {response.status_code}")
                print(f"      Resposta: {response.text[:100]}...")
                
        except Exception as e:
            resultados[endpoint] = {"status": "EXCEPTION", "error": str(e)}
            print(f"   ❌ {nome}: Exceção {e}")
    
    # 3. Testar endpoints específicos com dados
    print("\n3. 🔍 Testando endpoints específicos...")
    
    # Testar apontamentos com filtros
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/apontamentos")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Apontamentos Desenvolvimento: {len(data)} itens")
        else:
            print(f"   ❌ Apontamentos Desenvolvimento: Erro {response.status_code}")
    except Exception as e:
        print(f"   ❌ Apontamentos Desenvolvimento: {e}")
    
    # Testar pendências desenvolvimento
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Pendências Desenvolvimento: {len(data)} itens")
        else:
            print(f"   ❌ Pendências Desenvolvimento: Erro {response.status_code}")
    except Exception as e:
        print(f"   ❌ Pendências Desenvolvimento: {e}")
    
    # 4. Resumo dos resultados
    print("\n4. 📋 Resumo dos resultados:")
    print("=" * 60)
    
    total_endpoints = len(endpoints)
    endpoints_ok = sum(1 for r in resultados.values() if r["status"] == "OK")
    
    print(f"📊 Total de endpoints testados: {total_endpoints}")
    print(f"✅ Endpoints funcionando: {endpoints_ok}")
    print(f"❌ Endpoints com problema: {total_endpoints - endpoints_ok}")
    
    if endpoints_ok == total_endpoints:
        print("\n🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
        print("   O problema do Dashboard pode ser no frontend.")
    else:
        print("\n⚠️ ALGUNS ENDPOINTS TÊM PROBLEMAS:")
        for endpoint, resultado in resultados.items():
            if resultado["status"] != "OK":
                print(f"   ❌ {endpoint}: {resultado}")
    
    # 5. Sugestões de solução
    print("\n5. 💡 Sugestões para resolver o Dashboard:")
    print("=" * 60)
    
    if endpoints_ok == total_endpoints:
        print("✅ Backend funcionando corretamente!")
        print("\n🔧 Verificar no frontend:")
        print("   1. Console do navegador para erros JavaScript")
        print("   2. Network tab para ver se as requisições estão sendo feitas")
        print("   3. Se o usuário está logado corretamente")
        print("   4. Se os cookies de autenticação estão sendo enviados")
        print("\n🛠️ Soluções possíveis:")
        print("   - Fazer logout e login novamente")
        print("   - Limpar cache do navegador")
        print("   - Verificar se o proxy está funcionando")
        print("   - Reiniciar o servidor frontend")
    else:
        print("❌ Problemas no backend encontrados!")
        print("\n🔧 Verificar no backend:")
        print("   1. Logs do servidor para erros")
        print("   2. Conexão com o banco de dados")
        print("   3. Configuração de autenticação")
        print("\n🛠️ Soluções possíveis:")
        print("   - Reiniciar o servidor backend")
        print("   - Verificar configuração do banco")
        print("   - Verificar dependências instaladas")

def main():
    """Função principal"""
    print("🚨 TESTE COMPLETO DO DASHBOARD")
    print("=" * 60)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor backend está rodando")
            testar_dashboard_completo()
        else:
            print(f"❌ Servidor com problema: {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor não acessível: {e}")
        print("\n💡 Soluções:")
        print("   1. Verificar se o servidor backend está rodando")
        print("   2. Confirmar se está na porta 8000")
        print("   3. Reiniciar o servidor se necessário")

if __name__ == "__main__":
    main()
