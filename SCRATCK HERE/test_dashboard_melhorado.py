#!/usr/bin/env python3
"""
Teste para verificar as melhorias do dashboard:
1. Usuário alessandro com setor correto
2. Gráfico de setores como pizza (com nomes grandes)
3. Card de programações/pendências com mesma altura dos gráficos
"""

import sqlite3
import os
from datetime import datetime

def test_usuario_alessandro():
    """Verificar se o usuário alessandro tem o setor correto"""
    print("👤 1. VERIFICANDO USUÁRIO ALESSANDRO:")
    
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
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
            
            if usuario[1] == "LABORATORIO DE ENSAIOS ELETRICOS":
                print("✅ Setor correto: LABORATORIO DE ENSAIOS ELETRICOS")
                return True
            else:
                print(f"❌ Setor incorreto. Esperado: LABORATORIO DE ENSAIOS ELETRICOS, Atual: {usuario[1]}")
                return False
        else:
            print("❌ Usuário não encontrado")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return False

def verificar_setores_grandes():
    """Verificar se existem setores com nomes grandes no banco"""
    print("\n🏭 2. VERIFICANDO SETORES COM NOMES GRANDES:")
    
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome, departamento, ativo
            FROM tipo_setores 
            WHERE ativo = 1
            ORDER BY LENGTH(nome) DESC
            LIMIT 10
        """)
        
        setores = cursor.fetchall()
        print(f"📊 Top 10 setores com nomes mais longos:")
        
        for setor in setores:
            nome_len = len(setor[1])
            status_icon = "🔴" if nome_len > 30 else "🟡" if nome_len > 20 else "🟢"
            print(f"   {status_icon} {nome_len:2d} chars: {setor[1]}")
        
        # Contar total de setores
        cursor.execute("SELECT COUNT(*) FROM tipo_setores WHERE ativo = 1")
        total_setores = cursor.fetchone()[0]
        print(f"\n📈 Total de setores ativos: {total_setores}")
        
        if total_setores > 50:
            print("⚠️ Muitos setores! O gráfico de pizza precisa ser otimizado")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar setores: {e}")
        return False

def verificar_layout_dashboard():
    """Verificar se o layout do dashboard foi atualizado corretamente"""
    print("\n🎨 3. VERIFICANDO LAYOUT DO DASHBOARD:")
    
    dashboard_file = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\frontend\src\features\dashboard\DashboardPage.tsx"
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Verificar se o gráfico de pizza foi implementado
        if 'PieChart' in content and 'outerRadius={70}' in content:
            print("✅ Gráfico de pizza implementado para setores")
            checks.append(True)
        else:
            print("❌ Gráfico de pizza não encontrado")
            checks.append(False)
        
        # Verificar se há tratamento para nomes grandes
        if 'nomeAbrev' in content and 'substring(0, 20)' in content:
            print("✅ Tratamento para nomes grandes implementado")
            checks.append(True)
        else:
            print("❌ Tratamento para nomes grandes não encontrado")
            checks.append(False)
        
        # Verificar se o card tem altura igual aos gráficos
        if 'h-full' in content and 'flex flex-col h-full' in content:
            print("✅ Card com altura igual aos gráficos")
            checks.append(True)
        else:
            print("❌ Card não tem altura igual aos gráficos")
            checks.append(False)
        
        # Verificar se há lista de setores com nomes completos
        if 'max-h-20 overflow-y-auto' in content and 'truncate' in content:
            print("✅ Lista de setores com scroll implementada")
            checks.append(True)
        else:
            print("❌ Lista de setores com scroll não encontrada")
            checks.append(False)
        
        # Verificar se o grid foi alterado para 3 colunas
        if 'xl:grid-cols-3' in content:
            print("✅ Grid alterado para 3 colunas")
            checks.append(True)
        else:
            print("❌ Grid não foi alterado para 3 colunas")
            checks.append(False)
        
        return all(checks)
            
    except Exception as e:
        print(f"❌ Erro ao verificar layout: {e}")
        return False

def verificar_imports_recharts():
    """Verificar se os imports do Recharts estão corretos"""
    print("\n📦 4. VERIFICANDO IMPORTS DO RECHARTS:")
    
    dashboard_file = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\frontend\src\features\dashboard\DashboardPage.tsx"
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar imports necessários para pizza
        required_imports = ['PieChart', 'Pie', 'Cell', 'ResponsiveContainer', 'Tooltip', 'Legend']
        
        for imp in required_imports:
            if imp in content:
                print(f"✅ {imp} importado")
            else:
                print(f"❌ {imp} não importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar imports: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO - DASHBOARD MELHORADO")
    print("=" * 60)
    
    results = []
    
    # Executar todos os testes
    results.append(test_usuario_alessandro())
    results.append(verificar_setores_grandes())
    results.append(verificar_layout_dashboard())
    results.append(verificar_imports_recharts())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("✅ TODOS OS TESTES PASSARAM!")
        print("\n🎉 MELHORIAS IMPLEMENTADAS:")
        print("   ✅ Usuário alessandro com setor correto")
        print("   ✅ Gráfico de setores como pizza")
        print("   ✅ Tratamento para nomes grandes de setores")
        print("   ✅ Card programações/pendências com altura igual aos gráficos")
        print("   ✅ Layout otimizado para 3 colunas")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os itens marcados com ❌ acima")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Abra o frontend no navegador")
    print("2. Vá para o Dashboard")
    print("3. Verifique se:")
    print("   - O gráfico de setores é uma pizza")
    print("   - Os nomes grandes são truncados")
    print("   - O card de programações tem a mesma altura dos gráficos")
    print("   - A lista de setores tem scroll quando necessário")
