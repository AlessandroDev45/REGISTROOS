#!/usr/bin/env python3
"""
Teste para verificar se o dashboard unificado está funcionando
"""

import requests
import json
from datetime import datetime

def test_dashboard_unificado():
    """Testar se o dashboard carrega corretamente com o novo layout"""
    print("🧪 Testando Dashboard Unificado...")
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Testar endpoint de dashboard
        print("\n📊 1. TESTANDO ENDPOINT DE DASHBOARD:")
        response = requests.get(f"{base_url}/dashboard/dados")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de dashboard funcionando")
            
            # Verificar se tem dados de programações
            if 'programacoes' in data:
                prog = data['programacoes']
                print(f"   📋 Programações:")
                print(f"      Total: {prog.get('total', 0)}")
                print(f"      Enviadas: {prog.get('enviadas', 0)}")
                print(f"      Em Andamento: {prog.get('emAndamento', 0)}")
                print(f"      Concluídas: {prog.get('concluidas', 0)}")
            else:
                print("⚠️ Dados de programações não encontrados")
            
            # Verificar se tem dados de pendências
            if 'pendencias' in data:
                pend = data['pendencias']
                print(f"   ⚠️ Pendências:")
                print(f"      Total: {pend.get('total', 0)}")
                print(f"      Abertas: {pend.get('abertas', 0)}")
                print(f"      Fechadas: {pend.get('fechadas', 0)}")
            else:
                print("⚠️ Dados de pendências não encontrados")
                
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            print(f"   Resposta: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o backend está rodando em http://localhost:8000")
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_usuario_alessandro():
    """Testar se o usuário alessandro tem setor correto"""
    print("\n👤 2. TESTANDO USUÁRIO ALESSANDRO:")
    
    import sqlite3
    import os
    
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nome_completo, setor, departamento, id_setor, id_departamento
            FROM tipo_usuarios 
            WHERE email = 'alessandro.souza@data.com.br'
        """)
        
        usuario = cursor.fetchone()
        if usuario:
            print("✅ Usuário encontrado:")
            print(f"   Nome: {usuario[0]}")
            print(f"   Setor: {usuario[1]}")
            print(f"   Departamento: {usuario[2]}")
            print(f"   ID Setor: {usuario[3]}")
            print(f"   ID Departamento: {usuario[4]}")
            
            if usuario[1] == "LABORATORIO DE ENSAIOS ELETRICOS":
                print("✅ Setor correto!")
            else:
                print(f"❌ Setor incorreto. Esperado: LABORATORIO DE ENSAIOS ELETRICOS, Atual: {usuario[1]}")
        else:
            print("❌ Usuário não encontrado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")

def verificar_layout_dashboard():
    """Verificar se o layout do dashboard foi atualizado corretamente"""
    print("\n🎨 3. VERIFICANDO LAYOUT DO DASHBOARD:")
    
    dashboard_file = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\frontend\src\features\dashboard\DashboardPage.tsx"
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se o componente combinado existe
        if 'ProgramacoesPendenciasComponent' in content:
            print("✅ Componente combinado ProgramacoesPendenciasComponent encontrado")
        else:
            print("❌ Componente combinado não encontrado")
        
        # Verificar se o grid foi alterado para 3 colunas
        if 'xl:grid-cols-3' in content:
            print("✅ Grid alterado para 3 colunas")
        else:
            print("❌ Grid não foi alterado")
        
        # Verificar se tem emojis no título
        if '📋 Programações & Pendências' in content:
            print("✅ Título combinado com emojis encontrado")
        else:
            print("❌ Título combinado não encontrado")
        
        # Verificar se as seções separadas foram removidas
        if 'COLUNA 1: PROGRAMAÇÕES' in content and 'COLUNA 2: PENDÊNCIAS' in content:
            print("⚠️ Ainda existem seções separadas de programações e pendências")
        else:
            print("✅ Seções separadas foram removidas")
            
    except Exception as e:
        print(f"❌ Erro ao verificar layout: {e}")

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO - DASHBOARD UNIFICADO")
    print("=" * 50)
    
    test_usuario_alessandro()
    verificar_layout_dashboard()
    test_dashboard_unificado()
    
    print("\n" + "=" * 50)
    print("✅ TESTE CONCLUÍDO!")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Abra o frontend no navegador")
    print("2. Vá para o Dashboard")
    print("3. Verifique se Programações e Pendências estão no mesmo card")
    print("4. Confirme se os gráficos têm mais espaço agora")
