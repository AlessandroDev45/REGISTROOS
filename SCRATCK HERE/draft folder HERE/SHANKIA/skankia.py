import requests
import json

# --- Configurações da API Sankhya (extraídas do PDF fornecido) ---
BASE_URL = "https://api.sankhya.com.br"

# Dados de autenticação (da seção "Segue dados para autenticação:" na página 2)
# ATENÇÃO: Verifique se esses são os valores corretos para sua integração.
# O Appkey fornecido no PDF termina em '93a', não '93a0' ou similar.
APPKEY = "05efeb5d-627e-4e44-b047-030625dd81bf"

# ESTE É O TOKEN QUE ESTÁ INVALIDO/INATIVADO.
# VOCÊ PRECISA OBTER UM NOVO E VÁLIDO DIRETAMENTE DO SUPORTE DA SANKHYA.
# SUBSTITUA O VALOR ABAIXO PELO NOVO TOKEN QUE A SANKHYA LHE FORNECER.
INTEGRATION_TOKEN = "611fa67c-0c4d-4397-9f72-1be5a12f978f" # <--- SUBSTITUA ESTE VALOR QUANDO TIVER O NOVO TOKEN!

USERNAME = "ti@data.com.br"
PASSWORD = "q4]*WKcX+y77"

# Campos a serem consultados para as Ordens de Serviço (extraídos das páginas 5 e 6)
# Lista completa de campos conforme o exemplo no PDF para a requisição de consulta.
SERVICE_ORDER_FIELDS = (
    "NUMOS,CODPARC,RAZAOSOCIAL,CODCENCUS,DESCRCENCUS,DTABERTURAOS,DTALTER,STATUS,TAGMOTOR,"
    "TAGTRAFO,DESCRTAGTRAFO,DESCRTAGMOTOR,CODTIPSER,DESCRICAOTIPOSERVICO,DESCGRUTIPSERV,"
    "CODEQP,SERIE,TAGMOTOR_ABREVIADA,TAGTRAFO_ABREVIADA,POTENCIAW,POTENCIAMW,POTENCIAMVAR,"
    "POTENCIAMVA,POTENCIAKW,POTENCIAKVAR,POTENCIAHP,TENSAOTERCIARIO,TENSAOESTATOR,"
    "TENSAOBAIXA,TENSAOARMADURA,TENSAOALTA,CORRENTEROTOR,CORRENTEESTATOR,CORRENTECAMPO,"
    "CORRENTEBAIXA,CORRENTEARMADURA,CORRENTEALTA,ROTACAO,NROFASES,PESOTOTAL,PESOTANQUEACESS,"
    "PESOPARTEATIVA,PESOLEO,ANOFAB,CODFABEQP,NROPOLOS,CARACTPOLO,FABRICANTE"
)

# --- Função para login e obtenção do bearer token ---
def sankhya_login(appkey, integration_token, username, password):
    """
    Realiza o login na API Sankhya e retorna o bearer token.
    Baseado no CURL de login da página 3 do PDF.
    """
    login_url = f"{BASE_URL}/login"
    
    # Conforme o exemplo CURL na página 3, as credenciais são enviadas nos cabeçalhos.
    headers = {
        "Content-Type": "application/json",
        "token": integration_token,
        "appkey": appkey,
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, headers=headers, data=json.dumps({}))
        response.raise_for_status()
        
        login_data = response.json()
        bearer_token = login_data.get("bearerToken")
        error = login_data.get("error")
        
        if bearer_token:
            print(f"Login bem-sucedido. Bearer Token obtido.")
            return bearer_token
        elif error:
            print(f"Erro no login: {error.get('descricao', 'Erro desconhecido')}")
            return None
        else:
            print(f"Resposta de login inesperada: {login_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de login: {e}")
        return None

# --- Função para consultar ordens de serviço ---
def get_service_orders(bearer_token, appkey, fields):
    """
    Consulta as ordens de serviço na API Sankhya usando o bearer token.
    Baseado no CURL de consulta da página 6 do PDF.
    """
    if not bearer_token:
        print("Bearer token não disponível. Faça o login primeiro.")
        return None

    query_url = f"{BASE_URL}/gateway/v1/mge/service.sbr?serviceName=CRUDServiceProvider.loadRecords&outputType=json"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "appkey": appkey
    }
    
    payload = {
        "serviceName": "CRUDServiceProvider.loadRecords",
        "requestBody": {
            "dataSet": {
                "rootEntity": "AD_TIVIEWINTEGROS",
                "includePresentationFields": "N",
                "offsetPage": "0",
                "criteria": {
                    "expression": {},
                    "parameters": []
                },
                "entity": {
                    "fieldset": {
                        "list": fields
                    }
                }
            }
        }
    }
    
    try:
        response = requests.post(query_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        service_orders_data = response.json()
        print("Consulta de Ordens de Serviço bem-sucedida.")
        return service_orders_data
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de consulta de Ordens de Serviço: {e}")
        return None

# --- Função para logout ---
def sankhya_logout(appkey):
    """
    Realiza o logout da sessão da API Sankhya.
    Baseado no CURL de logout da página 3 do PDF.
    """
    logout_url = f"{BASE_URL}/gateway/v1/mge/service.sbr?serviceName=MobileLoginSP.logout&outputType=json"
    
    headers = {
        "appkey": appkey
    }
    
    try:
        response = requests.post(logout_url, headers=headers, data=json.dumps({}))
        response.raise_for_status()
        
        logout_status = response.json()
        print(f"Logout bem-sucedido: {logout_status}")
        return logout_status
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de logout: {e}")
        return None

# --- Exemplo de uso do fluxo de integração ---
if __name__ == "__main__":
    print("Iniciando o processo de integração com Sankhya...")

    # 1. Login para obter o bearer token
    print("\n--- Tentando fazer login ---")
    bearer_token = sankhya_login(APPKEY, INTEGRATION_TOKEN, USERNAME, PASSWORD)

    if bearer_token:
        # 2. Consultar Ordens de Serviço
        print("\n--- Tentando consultar Ordens de Serviço ---")
        service_orders = get_service_orders(bearer_token, APPKEY, SERVICE_ORDER_FIELDS)
        
        if service_orders:
            print("\nDados das Ordens de Serviço recebidos (exibindo os primeiros 500 caracteres da resposta JSON):")
            print(json.dumps(service_orders, indent=2)[:500] + "...") 
        else:
            print("\nNão foi possível obter as Ordens de Serviço.")
            
        # 3. Logout (recomendado após a conclusão das operações)
        print("\n--- Tentando fazer logout ---")
        sankhya_logout(APPKEY)
    else:
        print("\nFalha ao fazer login. As operações subsequentes não serão executadas.")

    print("\nProcesso de integração concluído.")