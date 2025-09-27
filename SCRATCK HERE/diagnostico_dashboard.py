#!/usr/bin/env python3
"""
Diagnóstico do Dashboard - verificar endpoints e autenticação
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def testar_servidor():
    """Testa se o servidor está rodando"""
    print("🔍 Testando servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Servidor rodando: {response.json()}")
            return True
        else:
            print(f"   ❌ Servidor com problema: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Servidor não acessível: {e}")
        return False

def testar_endpoints_dashboard():
    """Testa os endpoints que o Dashboard usa"""
    print("\n📊 Testando endpoints do Dashboard...")
    
    endpoints = [
        "/api/apontamentos-detalhados",
        "/api/pcp/programacoes", 
        "/api/pcp/pendencias",
        "/api/departamentos",
        "/api/setores"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {endpoint}: {len(data)} itens")
                else:
                    print(f"   ✅ {endpoint}: OK (objeto)")
            elif response.status_code == 401:
                print(f"   🔐 {endpoint}: Requer autenticação")
            else:
                print(f"   ❌ {endpoint}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exceção {e}")

def testar_com_autenticacao():
    """Testa endpoints com autenticação simulada"""
    print("\n🔐 Testando com autenticação...")
    
    # Simular login para obter token/cookie
    login_data = {
        "username": "admin",  # Ajuste conforme necessário
        "password": "admin123"  # Ajuste conforme necessário
    }
    
    session = requests.Session()
    
    try:
        # Tentar fazer login
        login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            
            # Testar endpoints com sessão autenticada
            endpoints = [
                "/api/apontamentos-detalhados",
                "/api/pcp/programacoes", 
                "/api/pcp/pendencias"
            ]
            
            for endpoint in endpoints:
                try:
                    response = session.get(f"{BASE_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   ✅ {endpoint}: {len(data)} itens (autenticado)")
                        else:
                            print(f"   ✅ {endpoint}: OK (autenticado)")
                    else:
                        print(f"   ❌ {endpoint}: Erro {response.status_code} (autenticado)")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint}: Exceção {e}")
        else:
            print(f"   ❌ Falha no login: {login_response.status_code}")
            print(f"   📄 Resposta: {login_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro no processo de login: {e}")

def verificar_dados_banco():
    """Verifica se há dados no banco para o Dashboard"""
    print("\n💾 Verificando dados no banco...")
    
    import sqlite3
    import os
    
    db_path = "RegistroOS/registrooficial/backend/app/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"   ❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas principais
        tabelas = [
            ("apontamentos_detalhados", "Apontamentos"),
            ("programacoes", "Programações"),
            ("pendencias", "Pendências"),
            ("ordens_servico", "Ordens de Serviço"),
            ("tipo_usuarios", "Usuários")
        ]
        
        for tabela, nome in tabelas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"   📊 {nome}: {count} registros")
            except Exception as e:
                print(f"   ❌ {nome}: Erro ao contar - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao acessar banco: {e}")

def verificar_configuracao_frontend():
    """Verifica configuração do frontend"""
    print("\n🌐 Verificando configuração do frontend...")
    
    # Verificar se o proxy está configurado
    try:
        # Testar acesso direto ao frontend
        frontend_response = requests.get("http://localhost:3001", timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ Frontend acessível em localhost:3001")
        else:
            print(f"   ❌ Frontend com problema: {frontend_response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend não acessível: {e}")
    
    # Verificar proxy para API
    try:
        proxy_response = requests.get("http://localhost:3001/api/health", timeout=5)
        if proxy_response.status_code == 200:
            print("   ✅ Proxy API funcionando")
        else:
            print(f"   ❌ Proxy API com problema: {proxy_response.status_code}")
    except Exception as e:
        print(f"   ❌ Proxy API não funcionando: {e}")

def sugerir_solucoes():
    """Sugere soluções baseadas nos problemas encontrados"""
    print("\n💡 POSSÍVEIS SOLUÇÕES:")
    print("=" * 60)
    
    print("1. 🔐 PROBLEMA DE AUTENTICAÇÃO:")
    print("   - Verifique se o usuário está logado no frontend")
    print("   - Confirme se os cookies de autenticação estão sendo enviados")
    print("   - Teste fazer logout e login novamente")
    
    print("\n2. 🌐 PROBLEMA DE PROXY/CORS:")
    print("   - Verifique se o proxy está configurado no package.json")
    print("   - Confirme se o backend está rodando na porta 8000")
    print("   - Teste acessar a API diretamente no navegador")
    
    print("\n3. 💾 PROBLEMA DE DADOS:")
    print("   - Execute o script de criação de dados de teste")
    print("   - Verifique se há dados nas tabelas do banco")
    print("   - Confirme se as migrações foram executadas")
    
    print("\n4. 🔧 PROBLEMA DE CONFIGURAÇÃO:")
    print("   - Reinicie o servidor backend")
    print("   - Reinicie o servidor frontend")
    print("   - Limpe o cache do navegador")
    
    print("\n5. 📊 PROBLEMA ESPECÍFICO DO DASHBOARD:")
    print("   - Verifique o console do navegador para erros JavaScript")
    print("   - Confirme se todos os endpoints estão respondendo")
    print("   - Teste acessar outras páginas da aplicação")

def main():
    """Função principal"""
    print("🚨 DIAGNÓSTICO DO DASHBOARD")
    print("=" * 60)
    print(f"⏰ Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Executar testes
    servidor_ok = testar_servidor()
    
    if servidor_ok:
        testar_endpoints_dashboard()
        testar_com_autenticacao()
    
    verificar_dados_banco()
    verificar_configuracao_frontend()
    sugerir_solucoes()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO CONCLUÍDO!")
    print("\nPróximos passos:")
    print("1. Analise os resultados acima")
    print("2. Implemente as soluções sugeridas")
    print("3. Teste o Dashboard novamente")
    print("4. Se o problema persistir, verifique os logs do backend")

if __name__ == "__main__":
    main()
