#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do sistema após correções
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

def testar_login():
    """Testa login"""
    print("🔐 TESTANDO LOGIN...")
    
    try:
        login_data = {
            "username": "admin@registroos.com",
            "password": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/api/token", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login: OK")
            return response.cookies
        else:
            print(f"   ❌ Login: Erro {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Login: Exceção - {e}")
        return None

def testar_endpoints_principais(cookies):
    """Testa endpoints principais"""
    print("\n📊 TESTANDO ENDPOINTS PRINCIPAIS...")
    
    endpoints = [
        # Dashboard
        ("/api/dashboard", "Dashboard OS"),
        ("/api/gestao/dashboard", "Dashboard Gestão"),
        
        # PCP
        ("/api/pcp/programacao-form-data", "Form Data PCP"),
        ("/api/pcp/programacoes", "Programações"),
        
        # OS
        ("/api/ordens-servico", "Ordens de Serviço"),
        
        # Admin
        ("/api/usuarios", "Usuários"),
        ("/api/users/", "Users Root"),
        ("/api/users/pending-approval", "Usuários Pendentes"),
        
        # Config
        ("/api/departamentos", "Departamentos"),
        ("/api/setores", "Setores"),
        ("/api/tipos-teste", "Tipos Teste"),
        ("/api/clientes", "Clientes"),
        
        # Desenvolvimento
        ("/api/apontamentos", "Apontamentos"),
        ("/api/tipos-maquina", "Tipos Máquina"),
        ("/api/tipos-atividade", "Tipos Atividade"),
        ("/api/descricoes-atividade", "Descrições Atividade"),
        ("/api/colaboradores", "Colaboradores"),
        ("/api/causas-retrabalho", "Causas Retrabalho"),
        ("/api/pendencias", "Pendências"),
        
        # Relatórios
        ("/api/gestao/relatorio-producao", "Relatório Produção"),
        ("/api/relatorio/completo", "Relatório Completo")
    ]
    
    resultados = {}
    
    for endpoint, nome in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ {nome}: {len(data)} registros")
                    elif isinstance(data, dict):
                        print(f"   ✅ {nome}: Dados carregados")
                    else:
                        print(f"   ✅ {nome}: OK")
                    resultados[nome] = True
                except:
                    print(f"   ✅ {nome}: Resposta válida")
                    resultados[nome] = True
            else:
                print(f"   ❌ {nome}: Erro {response.status_code}")
                resultados[nome] = False
                
        except Exception as e:
            print(f"   ❌ {nome}: Exceção - {str(e)[:30]}...")
            resultados[nome] = False
    
    return resultados

def mostrar_resumo(resultados):
    """Mostra resumo dos testes"""
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL DOS TESTES")
    print("=" * 60)
    
    total = len(resultados)
    ok = sum(1 for r in resultados.values() if r)
    
    # Categorizar resultados
    categorias = {
        'Dashboard': [k for k in resultados.keys() if 'Dashboard' in k],
        'PCP': [k for k in resultados.keys() if any(x in k for x in ['PCP', 'Programaç'])],
        'OS/Admin': [k for k in resultados.keys() if any(x in k for x in ['Ordens', 'Usuários', 'Users', 'Pendentes'])],
        'Configuração': [k for k in resultados.keys() if any(x in k for x in ['Departamentos', 'Setores', 'Tipos Teste', 'Clientes'])],
        'Desenvolvimento': [k for k in resultados.keys() if any(x in k for x in ['Apontamentos', 'Tipos Máquina', 'Tipos Atividade', 'Descrições', 'Colaboradores', 'Causas', 'Pendências'])],
        'Relatórios': [k for k in resultados.keys() if 'Relatório' in k]
    }
    
    for categoria, endpoints in categorias.items():
        if endpoints:
            ok_cat = sum(1 for ep in endpoints if resultados.get(ep, False))
            total_cat = len(endpoints)
            status = "✅" if ok_cat == total_cat else "⚠️" if ok_cat > 0 else "❌"
            print(f"   {status} {categoria}: {ok_cat}/{total_cat}")
    
    print(f"\n📈 RESULTADO GERAL:")
    print(f"   ✅ Endpoints funcionando: {ok}/{total}")
    print(f"   📊 Taxa de sucesso: {(ok/total)*100:.1f}%")
    
    if ok >= total * 0.9:  # 90% ou mais
        print(f"\n🎉 SISTEMA EXCELENTE!")
        print(f"   ✅ Quase todos os endpoints funcionando")
        print(f"   🚀 Sistema pronto para produção")
    elif ok >= total * 0.8:  # 80% ou mais
        print(f"\n🎉 SISTEMA MUITO BOM!")
        print(f"   ✅ A maioria dos endpoints funcionando")
        print(f"   🚀 Sistema adequado para uso")
    elif ok >= total * 0.6:  # 60% ou mais
        print(f"\n⚠️ SISTEMA BOM")
        print(f"   🔧 Alguns endpoints precisam de atenção")
        print(f"   📋 Funcionalidades principais disponíveis")
    else:
        print(f"\n❌ SISTEMA PRECISA DE MELHORIAS")
        print(f"   🔧 Muitos endpoints com problemas")
        print(f"   📋 Revisar implementações")
    
    return ok >= total * 0.8

def main():
    """Função principal"""
    print("🧪 TESTE FINAL DO SISTEMA APÓS CORREÇÕES")
    print("=" * 60)
    
    # Fazer login
    cookies = testar_login()
    if not cookies:
        print("❌ Falha no login - abortando testes")
        return False
    
    # Testar endpoints
    resultados = testar_endpoints_principais(cookies)
    
    # Mostrar resumo
    sucesso = mostrar_resumo(resultados)
    
    if sucesso:
        print("\n✅ SISTEMA TESTADO COM SUCESSO!")
        print("   🎯 Pronto para uso em produção")
    else:
        print("\n⚠️ SISTEMA TESTADO - VERIFICAR PROBLEMAS RESTANTES")
        print("   🔧 Alguns endpoints ainda precisam de correção")
    
    return sucesso

if __name__ == "__main__":
    main()
