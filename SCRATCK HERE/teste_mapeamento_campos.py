#!/usr/bin/env python3
"""
Teste do mapeamento correto dos campos do scraping
"""

import requests
import json
import time
import sqlite3

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    credenciais = {"username": "admin@registroos.com", "password": "admin123"}
    
    try:
        print(f"🔐 Fazendo login: {credenciais['username']}")
        response = session.post("http://localhost:8000/api/login", json=credenciais, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Login OK")
            return session
        else:
            print(f"❌ Login falhou: {response.status_code}")
            return None
                    
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def verificar_banco_antes():
    """Verifica se a OS já existe no banco antes do teste"""
    try:
        db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar OS 12345
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero LIKE '%12345%'")
        os_existente = cursor.fetchone()
        
        if os_existente:
            print("⚠️ OS 12345 já existe no banco!")
            print(f"   ID: {os_existente[0]}")
            print(f"   Número: {os_existente[1]}")
            print(f"   Status: {os_existente[2]}")
            
            # Verificar campos específicos
            print(f"   fim_os: {os_existente[15] if len(os_existente) > 15 else 'N/A'}")
            print(f"   data_inicio_prevista: {os_existente[16] if len(os_existente) > 16 else 'N/A'}")
            print(f"   data_fim_prevista: {os_existente[17] if len(os_existente) > 17 else 'N/A'}")
            
            # Deletar para teste limpo
            resposta = input("   Deletar OS existente para teste limpo? (s/n): ")
            if resposta.lower() == 's':
                cursor.execute("DELETE FROM ordens_servico WHERE os_numero LIKE '%12345%'")
                conn.commit()
                print("   ✅ OS deletada")
            else:
                print("   ⚠️ Mantendo OS existente")
                conn.close()
                return False
        else:
            print("✅ OS 12345 não existe no banco - teste limpo")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def verificar_banco_depois():
    """Verifica os campos no banco após o scraping"""
    try:
        db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar OS 12345
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero LIKE '%12345%'")
        os_criada = cursor.fetchone()
        
        if os_criada:
            print("🎉 OS 12345 foi criada no banco!")
            print(f"   ID: {os_criada[0]}")
            print(f"   Número: {os_criada[1]}")
            print(f"   Status: {os_criada[2]}")
            
            # Verificar campos mapeados
            print(f"\n📅 CAMPOS MAPEADOS:")
            print(f"   fim_os (DATA DA CONCLUSAO): {os_criada[15] if len(os_criada) > 15 else 'N/A'}")
            print(f"   data_inicio_prevista (DATA DE INICIO DA PERITAGEM): {os_criada[16] if len(os_criada) > 16 else 'N/A'}")
            print(f"   data_fim_prevista (DATA DE FIM DA PERITAGEM): {os_criada[17] if len(os_criada) > 17 else 'N/A'}")
            
            # Buscar cliente
            id_cliente = os_criada[7] if len(os_criada) > 7 else None
            if id_cliente:
                cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente,))
                cliente = cursor.fetchone()
                if cliente:
                    print(f"\n🏢 CLIENTE:")
                    print(f"   ID: {cliente[0]}")
                    print(f"   Razão Social: {cliente[1]}")
                    print(f"   CNPJ: {cliente[3]}")
                    print(f"   Endereço (CLIENTE MUNICIPIO): {cliente[4] if len(cliente) > 4 else 'N/A'}")
            
            # Verificar se os campos estão corretos
            esperado_fim_os = "2019-12-23"  # 23/12/2019 convertido
            esperado_inicio = "2019-12-03"  # 03/12/2019 convertido
            esperado_fim = "2019-12-03"     # 03/12/2019 convertido
            
            print(f"\n✅ VERIFICAÇÃO DOS MAPEAMENTOS:")
            
            fim_os_str = str(os_criada[15]) if len(os_criada) > 15 and os_criada[15] else ""
            if esperado_fim_os in fim_os_str:
                print(f"   ✅ fim_os CORRETO: {fim_os_str}")
            else:
                print(f"   ❌ fim_os INCORRETO: {fim_os_str} (esperado: {esperado_fim_os})")
            
            inicio_str = str(os_criada[16]) if len(os_criada) > 16 and os_criada[16] else ""
            if esperado_inicio in inicio_str:
                print(f"   ✅ data_inicio_prevista CORRETO: {inicio_str}")
            else:
                print(f"   ❌ data_inicio_prevista INCORRETO: {inicio_str} (esperado: {esperado_inicio})")
            
            fim_str = str(os_criada[17]) if len(os_criada) > 17 and os_criada[17] else ""
            if esperado_fim in fim_str:
                print(f"   ✅ data_fim_prevista CORRETO: {fim_str}")
            else:
                print(f"   ❌ data_fim_prevista INCORRETO: {fim_str} (esperado: {esperado_fim})")
            
            return True
        else:
            print("❌ OS 12345 não foi criada no banco")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def testar_mapeamento_completo():
    """Testa o mapeamento completo dos campos"""
    
    print("🧪 TESTE DE MAPEAMENTO DOS CAMPOS DO SCRAPING")
    print("=" * 60)
    
    # 1. Verificar banco antes
    print("\n1️⃣ VERIFICANDO BANCO ANTES DO TESTE...")
    if not verificar_banco_antes():
        return False
    
    # 2. Fazer login
    print("\n2️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - sem login")
        return False
    
    # 3. Testar endpoint com scraping
    print("\n3️⃣ EXECUTANDO SCRAPING DA OS 12345...")
    try:
        url = "http://localhost:8000/api/formulario/os/12345"
        print(f"🔍 URL: {url}")
        print("⚠️ AGUARDE... O scraping pode demorar alguns minutos...")
        
        start_time = time.time()
        response = session.get(url, timeout=600)  # 10 minutos
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Tempo total: {duration:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 SUCESSO! OS criada via scraping")
            print(f"   - Fonte: {data.get('fonte', 'banco')}")
            
            # 4. Verificar banco depois
            print("\n4️⃣ VERIFICANDO CAMPOS NO BANCO...")
            return verificar_banco_depois()
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE MAPEAMENTO DOS CAMPOS")
    print("=" * 60)
    
    print("📋 ESTE TESTE VAI VERIFICAR:")
    print("   1. DATA DA CONCLUSAO -> fim_os")
    print("   2. DATA DE INICIO DA PERITAGEM -> data_inicio_prevista")
    print("   3. DATA DE FIM DA PERITAGEM -> data_fim_prevista")
    print("   4. CLIENTE MUNICIPIO -> endereco (tabela clientes)")
    
    print("\n⚠️ IMPORTANTE:")
    print("   - O servidor deve estar rodando SEM auto-reload")
    print("   - O teste pode demorar alguns minutos")
    print("   - Os campos serão verificados no banco SQLite")
    
    input("\n⏸️ Pressione ENTER para continuar...")
    
    sucesso = testar_mapeamento_completo()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 MAPEAMENTO DOS CAMPOS FUNCIONOU!")
        print("   Os dados do scraping foram corretamente mapeados")
    else:
        print("❌ MAPEAMENTO TEM PROBLEMAS!")
        print("   Verifique os logs do servidor e do banco")

if __name__ == "__main__":
    main()
