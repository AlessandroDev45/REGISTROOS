#!/usr/bin/env python3
"""
Teste simples para verificar se a API de tipos de atividade está retornando o campo nome
"""

import requests
import json

def test_atividade_api():
    """Testar API de tipos de atividade"""
    
    print("🔧 [DEBUG] Testando API de tipos de atividade...")
    
    try:
        # Fazer requisição para a API
        url = "http://localhost:8000/api/admin/tipos-atividade"
        
        print(f"📡 [REQUEST] GET {url}")
        response = requests.get(url)
        
        print(f"✅ [RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            atividades = response.json()
            print(f"✅ [SUCCESS] Retornou {len(atividades)} tipos de atividade")
            
            if len(atividades) > 0:
                print(f"\n📋 [DADOS] Primeira atividade:")
                primeira = atividades[0]
                print(json.dumps(primeira, indent=2, ensure_ascii=False))
                
                # Verificar campos essenciais
                campos_essenciais = ['id', 'nome', 'nome_tipo', 'descricao', 'departamento', 'setor', 'categoria', 'ativo']
                print(f"\n🔍 [VERIFICAÇÃO] Campos essenciais:")
                for campo in campos_essenciais:
                    valor = primeira.get(campo)
                    if valor is not None and valor != '':
                        print(f"   ✅ {campo}: '{valor}'")
                    else:
                        print(f"   ❌ {campo}: VAZIO ou None")
                        
                # Verificar se todas as atividades têm nome
                sem_nome = [a for a in atividades if not a.get('nome')]
                if len(sem_nome) > 0:
                    print(f"\n❌ [PROBLEMA] {len(sem_nome)} atividades sem campo 'nome'")
                else:
                    print(f"\n✅ [SUCESSO] Todas as atividades têm campo 'nome'")
                    
            else:
                print("⚠️ [AVISO] Nenhuma atividade retornada")
                
        elif response.status_code == 401:
            print("❌ [ERROR] 401 - Não autorizado. Servidor pode estar exigindo autenticação.")
        elif response.status_code == 404:
            print("❌ [ERROR] 404 - Endpoint não encontrado. Verifique se o servidor está rodando.")
        else:
            print(f"❌ [ERROR] Status {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ [ERROR] Não foi possível conectar ao servidor. Verifique se está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ [ERROR] Erro inesperado: {e}")

    print("\n✅ [DEBUG] Teste da API concluído!")

if __name__ == "__main__":
    test_atividade_api()
