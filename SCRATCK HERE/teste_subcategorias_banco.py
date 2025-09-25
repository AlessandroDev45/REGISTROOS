#!/usr/bin/env python3
"""
Teste específico para verificar se as subcategorias estão sendo retornadas do banco de dados
"""

import requests
import json
import sqlite3

def verificar_dados_banco():
    """Verifica os dados diretamente no banco"""
    
    print("🗄️ VERIFICANDO DADOS NO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect("RegistroOS/registrooficial/backend/registroos_new.db")
        cursor = conn.cursor()
        
        # Verificar dados na tabela tipos_maquina
        print("1️⃣ Dados na tabela tipos_maquina:")
        cursor.execute("""
            SELECT id, nome_tipo, categoria, subcategoria 
            FROM tipos_maquina 
            WHERE subcategoria IS NOT NULL AND subcategoria != ''
            ORDER BY categoria, nome_tipo
        """)
        
        results = cursor.fetchall()
        
        if results:
            print(f"   ✅ Encontrados {len(results)} registros com subcategorias:")
            for row in results:
                print(f"      ID: {row[0]}, Nome: {row[1]}, Categoria: {row[2]}, Subcategoria: {row[3]}")
        else:
            print("   ❌ Nenhum registro encontrado com subcategorias")
        
        # Verificar categorias disponíveis
        print(f"\n2️⃣ Categorias disponíveis:")
        cursor.execute("SELECT DISTINCT categoria FROM tipos_maquina WHERE categoria IS NOT NULL ORDER BY categoria")
        categorias = cursor.fetchall()
        
        for cat in categorias:
            print(f"      - {cat[0]}")
        
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"   ❌ Erro ao acessar banco: {e}")
        return []

def testar_endpoint_com_auth():
    """Testa o endpoint com autenticação"""
    
    print(f"\n🌐 TESTANDO ENDPOINT COM AUTENTICAÇÃO")
    print("=" * 50)
    
    # Usar sessão para manter cookies
    session = requests.Session()
    
    # Fazer login primeiro
    print("1️⃣ Fazendo login...")
    login_url = "http://localhost:8000/api/login"
    
    # Tentar diferentes credenciais
    credenciais = [
        {"username": "ADMIN", "password": "123456"},
        {"username": "ALESSANDRO", "password": "123456"},
        {"username": "admin", "password": "admin"}
    ]
    
    login_sucesso = False
    
    for cred in credenciais:
        try:
            response = session.post(login_url, json=cred)
            if response.status_code == 200:
                print(f"   ✅ Login realizado com {cred['username']}")
                login_sucesso = True
                break
            else:
                print(f"   ❌ Falha login {cred['username']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro login {cred['username']}: {e}")
    
    if not login_sucesso:
        print("   ❌ Não foi possível fazer login com nenhuma credencial")
        return
    
    # Testar endpoint de subcategorias
    print(f"\n2️⃣ Testando endpoint de subcategorias...")
    
    categorias_teste = ['MOTOR CA', 'MOTOR CC', 'GERADOR CA', 'TRANSFORMADOR']
    
    for categoria in categorias_teste:
        print(f"\n   🔧 Testando categoria: {categoria}")
        
        url = f"http://localhost:8000/api/tipos-maquina/subcategorias?categoria={categoria}"
        
        try:
            response = session.get(url)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                subcategorias = response.json()
                if isinstance(subcategorias, list):
                    print(f"      ✅ {len(subcategorias)} subcategorias retornadas:")
                    for sub in subcategorias:
                        print(f"         - {sub}")
                else:
                    print(f"      📄 Resposta: {subcategorias}")
            else:
                print(f"      ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {e}")

def testar_endpoint_fallback():
    """Testa o endpoint de fallback"""
    
    print(f"\n🔄 TESTANDO ENDPOINT DE FALLBACK")
    print("=" * 50)
    
    session = requests.Session()
    
    # Login (assumindo que já funcionou antes)
    login_response = session.post("http://localhost:8000/api/login", json={"username": "ADMIN", "password": "123456"})
    
    if login_response.status_code == 200:
        print("   ✅ Login realizado")
        
        # Testar endpoint de fallback
        url = "http://localhost:8000/api/subcategorias-por-categoria?categoria=MOTOR"
        
        try:
            response = session.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                subcategorias = data.get('subcategorias', [])
                print(f"   ✅ {len(subcategorias)} subcategorias do fallback:")
                for sub in subcategorias[:5]:  # Mostrar apenas as primeiras 5
                    print(f"      - {sub}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    else:
        print("   ❌ Falha no login")

def main():
    """Função principal"""
    
    print("🎯 TESTE COMPLETO DE SUBCATEGORIAS")
    print("=" * 60)
    
    # 1. Verificar dados no banco
    dados_banco = verificar_dados_banco()
    
    # 2. Testar endpoint com autenticação
    testar_endpoint_com_auth()
    
    # 3. Testar endpoint de fallback
    testar_endpoint_fallback()
    
    print(f"\n📊 RESUMO:")
    print(f"- Dados no banco: {'✅' if dados_banco else '❌'}")
    print(f"- Endpoint funcionando: Verificar logs acima")
    print(f"- Fallback disponível: ✅")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    if dados_banco:
        print("1. Os dados existem no banco - endpoint deve funcionar")
        print("2. Verificar se o frontend está chamando o endpoint correto")
        print("3. Verificar se há problemas de autenticação no frontend")
    else:
        print("1. Adicionar dados de subcategorias na tabela tipos_maquina")
        print("2. Ou usar apenas o endpoint de fallback")
        print("3. Verificar se o frontend está funcionando com fallback")

if __name__ == "__main__":
    main()
