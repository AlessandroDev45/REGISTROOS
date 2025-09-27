#!/usr/bin/env python3
"""
Teste para verificar se os endpoints do AtribuicaoProgramacaoModal funcionam
"""

import requests
import json

def testar_endpoints_modal():
    """Testa os endpoints do modal de atribuição"""
    
    print("🧪 TESTE: Endpoints do AtribuicaoProgramacaoModal")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Fazer login
    try:
        print("\n1️⃣ Fazendo login...")
        
        session = requests.Session()
        
        response = session.post(
            f"{base_url}/api/login", 
            json={"username": "user.pcp@registroos.com", "password": "123456"}, 
            timeout=10
        )
        
        print(f"   Status login: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Não foi possível fazer login. Abortando testes.")
            return
        
        print("   ✅ Login realizado com sucesso!")
        
        # 2. Testar endpoint de colaboradores
        print("\n2️⃣ Testando /api/desenvolvimento/colaboradores...")
        try:
            response = session.get(f"{base_url}/api/desenvolvimento/colaboradores", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint funcionando!")
                
                try:
                    data = response.json()
                    print(f"   📊 Colaboradores do setor: {len(data)}")
                    
                    if len(data) > 0:
                        print("   👥 Lista de colaboradores:")
                        for i, colab in enumerate(data[:5], 1):  # Primeiros 5
                            nome = colab.get('nome_completo', 'N/A')
                            setor = colab.get('setor', 'N/A')
                            privilege = colab.get('privilege_level', 'N/A')
                            print(f"      {i}. {nome} - {setor} - {privilege}")
                    else:
                        print("   📋 Nenhum colaborador no setor")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Resposta não é JSON válido")
                    print(f"   Resposta: {response.text[:200]}")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 3. Testar endpoint de usuários (fallback)
        print("\n3️⃣ Testando /api/users/usuarios/ (fallback)...")
        try:
            response = session.get(f"{base_url}/api/users/usuarios/", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint funcionando!")
                
                try:
                    data = response.json()
                    print(f"   📊 Total de usuários: {len(data)}")
                    
                    if len(data) > 0:
                        # Simular filtro por setor (como no frontend)
                        user_data = {"id_setor": 1}  # Exemplo
                        usuarios_filtrados = [user for user in data if user.get('id_setor') == user_data['id_setor']]
                        print(f"   🎯 Usuários do setor {user_data['id_setor']}: {len(usuarios_filtrados)}")
                        
                        if usuarios_filtrados:
                            print("   👥 Primeiros usuários do setor:")
                            for i, user in enumerate(usuarios_filtrados[:3], 1):
                                nome = user.get('nome_completo', 'N/A')
                                setor = user.get('id_setor', 'N/A')
                                print(f"      {i}. {nome} - Setor ID: {setor}")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Resposta não é JSON válido")
                    print(f"   Resposta: {response.text[:200]}")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_endpoints_modal()
