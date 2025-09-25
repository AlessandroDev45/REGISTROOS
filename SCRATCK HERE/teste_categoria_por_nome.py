#!/usr/bin/env python3
"""
Teste para verificar se o novo endpoint categoria-por-nome está funcionando
"""

import requests
import json

def testar_categoria_por_nome():
    """Testa o novo endpoint que busca categoria por nome_tipo"""
    
    print("🎯 TESTE DO ENDPOINT categoria-por-nome")
    print("=" * 60)
    
    # Usar sessão para manter cookies
    session = requests.Session()
    
    # Fazer login primeiro
    print("1️⃣ Fazendo login...")
    login_url = "http://localhost:8000/api/login"
    
    credenciais = [
        {"username": "ADMIN", "password": "123456"},
        {"username": "ALESSANDRO", "password": "123456"}
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
        print("   ❌ Não foi possível fazer login")
        return
    
    # Testar o novo endpoint
    print(f"\n2️⃣ Testando endpoint categoria-por-nome...")
    
    tipos_teste = [
        'MAQUINA ESTATICA CA',
        'MAQUINA ROTATIVA CA MIT',
        'MAQUINA ROTATIVA CC MCC',
        'MAQUINA ROTATIVA CA GIT'
    ]
    
    for nome_tipo in tipos_teste:
        print(f"\n   🔧 Testando: {nome_tipo}")
        
        url = f"http://localhost:8000/api/tipos-maquina/categoria-por-nome?nome_tipo={nome_tipo}"
        
        try:
            response = session.get(url)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                categoria = data.get('categoria')
                if categoria:
                    print(f"      ✅ Categoria encontrada: {categoria}")
                    
                    # Testar subcategorias para essa categoria
                    print(f"      🎯 Testando subcategorias para categoria '{categoria}'...")
                    sub_url = f"http://localhost:8000/api/tipos-maquina/subcategorias?categoria={categoria}"
                    
                    try:
                        sub_response = session.get(sub_url)
                        if sub_response.status_code == 200:
                            subcategorias = sub_response.json()
                            if isinstance(subcategorias, list) and subcategorias:
                                print(f"         ✅ {len(subcategorias)} subcategorias:")
                                for sub in subcategorias[:3]:  # Mostrar apenas as primeiras 3
                                    print(f"            - {sub}")
                                if len(subcategorias) > 3:
                                    print(f"            ... e mais {len(subcategorias) - 3}")
                            else:
                                print(f"         ❌ Nenhuma subcategoria encontrada")
                        else:
                            print(f"         ❌ Erro subcategorias: {sub_response.status_code}")
                    except Exception as e:
                        print(f"         ❌ Erro ao buscar subcategorias: {e}")
                        
                else:
                    print(f"      ❌ Categoria não encontrada")
            else:
                print(f"      ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {e}")

def verificar_dados_banco():
    """Verifica os dados no banco para entender a estrutura"""
    
    print(f"\n🗄️ VERIFICANDO DADOS NO BANCO")
    print("=" * 60)
    
    import sqlite3
    
    try:
        conn = sqlite3.connect("RegistroOS/registrooficial/backend/registroos_new.db")
        cursor = conn.cursor()
        
        print("📊 Estrutura nome_tipo -> categoria -> subcategoria:")
        cursor.execute("""
            SELECT nome_tipo, categoria, subcategoria 
            FROM tipos_maquina 
            WHERE categoria IS NOT NULL 
            ORDER BY nome_tipo
        """)
        
        results = cursor.fetchall()
        
        for row in results:
            nome_tipo, categoria, subcategoria = row
            print(f"   📋 {nome_tipo}")
            print(f"      └─ Categoria: {categoria}")
            if subcategoria:
                partes = subcategoria.split(',')
                print(f"      └─ Subcategorias: {len(partes)} partes")
                for parte in partes[:2]:  # Mostrar apenas as primeiras 2
                    print(f"         • {parte.strip()}")
                if len(partes) > 2:
                    print(f"         • ... e mais {len(partes) - 2}")
            else:
                print(f"      └─ Subcategorias: Nenhuma")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")

def main():
    """Função principal"""
    
    print("🎯 TESTE COMPLETO - CATEGORIA POR NOME_TIPO")
    print("=" * 70)
    
    # 1. Verificar dados no banco
    verificar_dados_banco()
    
    # 2. Testar endpoint
    testar_categoria_por_nome()
    
    print(f"\n📋 INSTRUÇÕES PARA TESTAR NO FRONTEND:")
    print("=" * 70)
    print("1. Acesse: http://localhost:3001/desenvolvimento")
    print("2. Busque uma OS (ex: 12345)")
    print("3. Selecione um tipo de máquina:")
    print("   - MAQUINA ESTATICA CA (deve mostrar subcategorias de TRANSFORMADOR)")
    print("   - MAQUINA ROTATIVA CA MIT (deve mostrar subcategorias de MOTOR CA)")
    print("   - MAQUINA ROTATIVA CC MCC (deve mostrar subcategorias de MOTOR CC)")
    print("   - MAQUINA ROTATIVA CA GIT (deve mostrar subcategorias de GERADOR CA)")
    print("4. As subcategorias devem aparecer AUTOMATICAMENTE")
    print("5. Não precisa mais selecionar categoria manualmente!")
    
    print(f"\n✅ SOLUÇÃO IMPLEMENTADA:")
    print("=" * 70)
    print("✅ Endpoint categoria-por-nome criado")
    print("✅ Frontend modificado para buscar categoria automaticamente")
    print("✅ Subcategorias carregadas automaticamente após seleção do tipo")
    print("✅ Sistema agora entende: nome_tipo → categoria → subcategorias")

if __name__ == "__main__":
    main()
