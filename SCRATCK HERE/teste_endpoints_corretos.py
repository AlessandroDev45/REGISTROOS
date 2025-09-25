#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste dos endpoints corretos baseado na estrutura real do sistema
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

class TesteEndpointsCorretos:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = None
        self.resultados = {}
    
    def fazer_login(self):
        """Faz login no sistema"""
        print("🔐 FAZENDO LOGIN...")
        
        try:
            login_data = {
                "username": "admin@registroos.com",
                "password": "123456"
            }
            
            response = self.session.post(f"{BASE_URL}/api/token", data=login_data)
            
            if response.status_code == 200:
                self.cookies = response.cookies
                print("   ✅ Login realizado com sucesso")
                return True
            else:
                print(f"   ❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro na requisição de login: {e}")
            return False
    
    def testar_endpoint(self, nome, endpoint, metodo='GET', dados=None):
        """Testa um endpoint específico"""
        try:
            if metodo == 'GET':
                response = self.session.get(f"{BASE_URL}{endpoint}", cookies=self.cookies)
            elif metodo == 'POST':
                response = self.session.post(f"{BASE_URL}{endpoint}", json=dados, cookies=self.cookies)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ {nome}: {len(data)} registros")
                    elif isinstance(data, dict):
                        print(f"   ✅ {nome}: Dados carregados ({len(data)} chaves)")
                    else:
                        print(f"   ✅ {nome}: Resposta válida")
                    self.resultados[nome] = True
                    return True
                except:
                    print(f"   ✅ {nome}: Resposta não-JSON válida")
                    self.resultados[nome] = True
                    return True
            else:
                print(f"   ❌ {nome}: Erro {response.status_code}")
                self.resultados[nome] = False
                return False
                
        except Exception as e:
            print(f"   ❌ {nome}: Exceção - {str(e)[:50]}...")
            self.resultados[nome] = False
            return False
    
    def testar_dashboard(self):
        """Testa endpoints do dashboard"""
        print("\n📊 TESTANDO DASHBOARD")
        print("-" * 40)
        
        # Endpoints corretos baseados no código
        endpoints_dashboard = [
            ("Dashboard OS", "/api/dashboard"),
            ("Dashboard Gestão", "/api/gestao/dashboard"),
            ("Dashboard Executivo", "/api/gestao/dashboard-executivo")
        ]
        
        for nome, endpoint in endpoints_dashboard:
            self.testar_endpoint(nome, endpoint)
    
    def testar_pcp(self):
        """Testa endpoints do PCP"""
        print("\n📅 TESTANDO PCP")
        print("-" * 40)
        
        endpoints_pcp = [
            ("Form Data PCP", "/api/pcp/programacao-form-data"),
            ("Programações", "/api/pcp/programacoes"),
            ("OS PCP", "/api/pcp/ordens-servico")
        ]
        
        for nome, endpoint in endpoints_pcp:
            self.testar_endpoint(nome, endpoint)
    
    def testar_consulta_os(self):
        """Testa consulta de OS"""
        print("\n🔍 TESTANDO CONSULTA OS")
        print("-" * 40)
        
        endpoints_os = [
            ("Listar OS", "/api/ordens-servico"),
            ("OS Simples", "/api/os/"),
            ("Dashboard OS", "/api/dashboard")
        ]
        
        for nome, endpoint in endpoints_os:
            self.testar_endpoint(nome, endpoint)
    
    def testar_administrador(self):
        """Testa módulo administrador"""
        print("\n👨‍💼 TESTANDO ADMINISTRADOR")
        print("-" * 40)
        
        endpoints_admin = [
            ("Usuários", "/api/usuarios"),
            ("Usuários Users", "/api/users/"),
            ("Pendentes Aprovação", "/api/users/pending-approval")
        ]
        
        for nome, endpoint in endpoints_admin:
            self.testar_endpoint(nome, endpoint)
    
    def testar_admin_config(self):
        """Testa configurações administrativas"""
        print("\n⚙️ TESTANDO ADMIN CONFIG")
        print("-" * 40)
        
        endpoints_config = [
            ("Departamentos", "/api/departamentos"),
            ("Setores", "/api/setores"),
            ("Tipos Teste", "/api/tipos-teste"),
            ("Clientes", "/api/clientes"),
            ("Admin Departamentos", "/api/admin/departamentos"),
            ("Admin Setores", "/api/admin/setores")
        ]
        
        for nome, endpoint in endpoints_config:
            self.testar_endpoint(nome, endpoint)
    
    def testar_gestao(self):
        """Testa módulo de gestão"""
        print("\n📈 TESTANDO GESTÃO")
        print("-" * 40)
        
        endpoints_gestao = [
            ("Dashboard Gestão", "/api/gestao/dashboard"),
            ("Relatório Produção", "/api/gestao/relatorio-producao"),
            ("Dashboard Executivo", "/api/gestao/dashboard-executivo")
        ]
        
        for nome, endpoint in endpoints_gestao:
            self.testar_endpoint(nome, endpoint)
    
    def testar_desenvolvimento(self):
        """Testa módulo de desenvolvimento"""
        print("\n🔧 TESTANDO DESENVOLVIMENTO")
        print("-" * 40)
        
        endpoints_dev = [
            ("Apontamentos", "/api/apontamentos"),
            ("Meus Apontamentos", "/api/os/apontamentos/meus"),
            ("Apontamentos Dev", "/api/os/apontamentos/meus"),
            ("Tipos Máquina", "/api/tipos-maquina"),
            ("Tipos Atividade", "/api/tipos-atividade"),
            ("Descrições Atividade", "/api/descricoes-atividade"),
            ("Causas Retrabalho", "/api/causas-retrabalho"),
            ("Colaboradores", "/api/colaboradores"),
            ("Programação", "/api/programacao"),
            ("Pendências", "/api/pendencias")
        ]
        
        for nome, endpoint in endpoints_dev:
            self.testar_endpoint(nome, endpoint)
    
    def testar_relatorios(self):
        """Testa relatórios"""
        print("\n📊 TESTANDO RELATÓRIOS")
        print("-" * 40)
        
        endpoints_relatorios = [
            ("Relatório Completo", "/api/relatorio/completo"),
            ("Relatório Produção", "/api/gestao/relatorio-producao")
        ]
        
        for nome, endpoint in endpoints_relatorios:
            self.testar_endpoint(nome, endpoint)
    
    def executar_teste_completo(self):
        """Executa todos os testes"""
        print("🧪 TESTE COMPLETO DOS ENDPOINTS CORRETOS")
        print("=" * 60)
        
        if not self.fazer_login():
            print("❌ Falha no login - abortando testes")
            return False
        
        # Executar todos os testes
        self.testar_dashboard()
        self.testar_pcp()
        self.testar_consulta_os()
        self.testar_administrador()
        self.testar_admin_config()
        self.testar_gestao()
        self.testar_desenvolvimento()
        self.testar_relatorios()
        
        # Mostrar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINAIS")
        print("=" * 60)
        
        total_testes = len(self.resultados)
        testes_ok = sum(1 for resultado in self.resultados.values() if resultado)
        
        # Agrupar por categoria
        categorias = {
            'Dashboard': [k for k in self.resultados.keys() if 'Dashboard' in k],
            'PCP': [k for k in self.resultados.keys() if 'PCP' in k or 'Programaç' in k],
            'OS': [k for k in self.resultados.keys() if 'OS' in k or 'Listar' in k],
            'Admin': [k for k in self.resultados.keys() if 'Admin' in k or 'Usuários' in k],
            'Gestão': [k for k in self.resultados.keys() if 'Gestão' in k or 'Relatório' in k],
            'Desenvolvimento': [k for k in self.resultados.keys() if any(x in k for x in ['Apontamentos', 'Tipos', 'Descrições', 'Causas', 'Colaboradores', 'Pendências'])]
        }
        
        for categoria, endpoints in categorias.items():
            if endpoints:
                ok_categoria = sum(1 for ep in endpoints if self.resultados.get(ep, False))
                total_categoria = len(endpoints)
                status = "✅" if ok_categoria == total_categoria else "⚠️" if ok_categoria > 0 else "❌"
                print(f"   {status} {categoria}: {ok_categoria}/{total_categoria}")
        
        print(f"\n📈 RESUMO GERAL:")
        print(f"   ✅ Endpoints funcionando: {testes_ok}/{total_testes}")
        print(f"   📊 Taxa de sucesso: {(testes_ok/total_testes)*100:.1f}%")
        
        if testes_ok >= total_testes * 0.8:  # 80% ou mais
            print(f"\n🎉 SISTEMA MAJORITARIAMENTE FUNCIONAL!")
            print(f"   ✅ A maioria dos endpoints está operacional")
            print(f"   🚀 Sistema adequado para uso")
        elif testes_ok >= total_testes * 0.5:  # 50% ou mais
            print(f"\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
            print(f"   🔧 Alguns endpoints precisam de correção")
            print(f"   📋 Funcionalidades básicas disponíveis")
        else:
            print(f"\n❌ SISTEMA PRECISA DE ATENÇÃO")
            print(f"   🔧 Muitos endpoints com problemas")
            print(f"   📋 Revisar configurações e implementações")
        
        return testes_ok >= total_testes * 0.8

def main():
    """Função principal"""
    teste = TesteEndpointsCorretos()
    sucesso = teste.executar_teste_completo()
    
    if sucesso:
        print("\n✅ TESTE DOS ENDPOINTS FINALIZADO COM SUCESSO!")
    else:
        print("\n⚠️ TESTE DOS ENDPOINTS FINALIZADO - VERIFICAR PROBLEMAS!")
    
    return sucesso

if __name__ == "__main__":
    main()
