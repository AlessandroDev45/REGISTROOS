import time
import json
import os
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env no mesmo diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path, override=True)

def get_driver():
    """Inicializa o Chrome em modo anônimo e headless."""
    chrome_options = webdriver.ChromeOptions()
    
    # MODO ANÔNIMO - Evita popups de senha
    chrome_options.add_argument('--incognito')
    
    # MODO HEADLESS - Executa o navegador sem interface gráfica
    chrome_options.add_argument('--headless=new') # Usar '--headless=new' para as versões mais recentes do Chrome
    
    # Configurações básicas para velocidade e estabilidade
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-password-manager')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080') # Definir um tamanho de janela para renderização consistente em headless

    # Desabilita password manager (essencial)
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    print("🚀 Iniciando Chrome em modo anônimo e headless...")
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def click_post_login_element(driver, wait):
    """Clica no elemento específico após o login."""
    try:
        print("🔍 Procurando pelo elemento pós-login...")
        
        # XPath específico fornecido (primeiro elemento da lista de itens do menu lateral)
        target_xpath = '//*[@id="root"]/div/div[1]/div/div/div/div[2]/div'
        
        # Aguarda o elemento estar presente e clicável
        print("⏳ Aguardando elemento ficar disponível...")
        target_element = wait.until(
            EC.element_to_be_clickable((By.XPATH, target_xpath))
        )
        
        # Scroll para o elemento para garantir que esteja visível
        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
        time.sleep(1)
        
        # Clica no elemento
        target_element.click()
        print("✅ Elemento pós-login clicado com sucesso!")
        
        # Aguarda um pouco para o carregamento
        time.sleep(3)
        
        return True
        
    except TimeoutException:
        print("❌ Timeout: Elemento pós-login não encontrado no tempo limite.")
        return False
    except NoSuchElementException:
        print("❌ Elemento pós-login não encontrado na página.")
        return False
    except Exception as e:
        print(f"❌ Erro ao clicar no elemento pós-login: {e}")
        return False

def check_os_not_found(driver, wait):
    """Verifica se a OS não foi encontrada na busca."""
    try:
        # Verificar se há mensagem de "não encontrado" ou similar
        not_found_selectors = [
            "//div[contains(text(), 'não encontrada')]",
            "//div[contains(text(), 'Nenhum resultado')]",
            "//div[contains(text(), 'não foi encontrada')]",
            "//span[contains(text(), 'não encontrada')]",
            "//p[contains(text(), 'não encontrada')]",
            "//div[contains(@class, 'empty') or contains(@class, 'no-data')]"
        ]

        for selector in not_found_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element and element.is_displayed():
                    print(f"⚠️ OS não encontrada - detectado: {element.text}")
                    return True
            except:
                continue

        # Verificar se não há dados carregados após um tempo razoável
        time.sleep(3)

        # Verificar se não há container de detalhes
        try:
            details_xpath = '//div[contains(@class, "ant-card-body")]'
            details_elements = driver.find_elements(By.XPATH, details_xpath)
            if not details_elements:
                print("⚠️ Nenhum container de detalhes encontrado - OS pode não existir")
                return True
        except:
            pass

        return False

    except Exception as e:
        print(f"⚠️ Erro ao verificar se OS não foi encontrada: {e}")
        return False

def enter_search_value(driver, wait, search_value="12345"):
    """Insere valor no campo de busca e pressiona Enter."""
    try:
        print(f"🔍 Procurando pelo campo de entrada para inserir: {search_value}")

        # XPath específico do campo de input (campo de busca por OS)
        input_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]/span/span/input'

        # Aguarda o campo de input estar presente e interagível
        print("⏳ Aguardando campo de entrada ficar disponível...")
        input_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, input_xpath))
        )

        # Scroll para o campo para garantir que esteja visível
        driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        time.sleep(1)

        # Limpa o campo e insere o valor
        input_field.clear()
        input_field.send_keys(search_value)
        print(f"✅ Valor '{search_value}' inserido no campo!")

        # Pressiona Enter
        input_field.send_keys(Keys.ENTER)
        print("✅ Enter pressionado!")

        # Aguarda um pouco para o processamento e carregamento dos detalhes da OS
        time.sleep(5)

        # Verificar se a OS foi encontrada
        if check_os_not_found(driver, wait):
            print(f"❌ OS {search_value} não foi encontrada no sistema")
            return False

        return True

    except TimeoutException:
        print("❌ Timeout: Campo de entrada não encontrado no tempo limite.")
        return False
    except NoSuchElementException:
        print("❌ Campo de entrada não encontrado na página.")
        return False
    except Exception as e:
        print(f"❌ Erro ao inserir valor no campo: {e}")
        return False

def login(driver, wait, url, username, password, os_number):
    """Realiza o login no site com tratamento aprimorado do popup."""
    try:
        driver.get(url)
        print("Acessando a URL:", url)

        # Insere o usuário
        user_field = wait.until(EC.presence_of_element_located((By.ID, "login_username")))
        user_field.clear()
        user_field.send_keys(username)
        print(f"Usuário '{username}' inserido via ID 'login_username'.")

        # Insere a senha
        pass_field = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        pass_field.clear()
        pass_field.send_keys(password)
        print("Senha inserida via ID 'login_password'.")

        # Clica no botão de login
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Entrar')]] | //button[@type='submit'] | //button[contains(@class, 'login-button')]")))
        login_button.click()
        print("Botão de login clicado.")

        # Aguarda o carregamento inicial pós-login
        print("Aguardando carregamento após login...")
        time.sleep(3)

        # Clica no elemento específico pós-login
        print("🎯 Executando clique no elemento pós-login...")
        if click_post_login_element(driver, wait):
            print("✅ Elemento pós-login clicado com sucesso!")
            
            # Insere valor no campo de busca
            print(f"🔍 Executando inserção de valor no campo de busca: {os_number}")
            if enter_search_value(driver, wait, os_number):
                print(f"✅ Valor {os_number} inserido e Enter pressionado com sucesso!")
            else:
                print("⚠️ Não foi possível inserir o valor no campo, mas continuando...")
        else:
            print("⚠️ Não foi possível clicar no elemento pós-login, mas continuando...")

        print("✅ Login realizado em modo anônimo!")
        return True
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o login: {e}")
        return False

def wait_for_os_details_container(driver, wait, max_attempts=5):
    """
    Aguarda o carregamento do contêiner de detalhes da OS, que agora é um 'ant-card-body'
    dentro de uma aba ativa.
    """
    print("🔄 Aguardando carregamento do contêiner de detalhes da OS (ant-card-body na aba ativa)...")

    for attempt in range(max_attempts):
        try:
            print(f"📊 Tentativa {attempt + 1}/{max_attempts} de detectar contêiner de detalhes...")
            time.sleep(5 + (attempt * 2)) # Aumentar o tempo de espera nas primeiras tentativas

            # 1. Tentar localizar o botão da aba "Informações da OS" quando está ativo
            info_os_tab_button_xpath = '//div[contains(@class, "ant-tabs-tab-active")]//div[@role="tab" and contains(text(), "Informações da OS")]'
            
            # Use presence_of_element_located para apenas verificar se o botão existe antes de tentar clicar ou obter atributos
            info_os_tab_button = wait.until(EC.presence_of_element_located((By.XPATH, info_os_tab_button_xpath)))
            
            # Tente clicar no botão para garantir que a aba está ativa (mesmo que já esteja, não faz mal)
            driver.execute_script("arguments[0].click();", info_os_tab_button)
            print("✅ Botão 'Informações da OS' ativo encontrado e clicado (para garantir foco).")
            time.sleep(2) # Pequena pausa para a aba carregar seu conteúdo

            # 2. Localizar o painel da aba ativa que contém os dados da OS
            # O painel pode ter um ID dinâmico, então vamos procurar pelo atributo 'aria-controls' ou por uma classe genérica
            panel_id = info_os_tab_button.get_attribute("aria-controls")
            
            details_container_xpath = ''
            if panel_id:
                print(f"🔍 ID do painel associado via aria-controls: {panel_id}")
                # Procurar o ant-card-body dentro do painel com o ID dinâmico
                details_container_xpath = f'//div[@id="{panel_id}"]//div[contains(@class, "ant-card-body")]'
            else:
                print("⚠️ Atributo 'aria-controls' não encontrado no botão da aba. Tentando seletor alternativo para o contêiner de detalhes.")
                # Fallback: procurar por um ant-card-body dentro de qualquer painel ativo
                details_container_xpath = '//div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-card-body")]'
            
            # Aguarda até que o ant-card-body esteja presente
            details_container_element = wait.until(EC.presence_of_element_located((By.XPATH, details_container_xpath)))

            # 3. Verificar se há tags <p> dentro do ant-card-body, indicando que os dados foram carregados
            p_elements = details_container_element.find_elements(By.TAG_NAME, "p")
            if p_elements:
                print(f"✅ Contêiner 'ant-card-body' detectado com {len(p_elements)} tags <p> de dados.")
                return details_container_element
            else:
                print(f"⚠️ Contêiner 'ant-card-body' encontrado, mas sem tags <p> com dados. Tentando novamente.")
            
        except TimeoutException:
            print(f"⚠️ Timeout na tentativa {attempt + 1}: Botão da aba ou contêiner de detalhes não encontrado no tempo limite.")
        except NoSuchElementException:
            print(f"⚠️ Elemento não encontrado na tentativa {attempt + 1}.")
        except Exception as e:
            print(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
            import traceback
            traceback.print_exc()

    print("❌ Não foi possível detectar o contêiner de detalhes da OS após todas as tentativas.")
    return None

def scrape_os_details_data_only(driver, wait):
    """Extrai os detalhes da OS e retorna apenas os dados (sem salvar em arquivo)."""
    scraped_data_list = []

    # Modelo de dados da OS, preenchido com vazios para garantir todas as chaves
    os_template = {
        "NOME CLIENTE": "", "CNPJ": "", "CENTRO DE CUSTO": "", "NÚMERO DA OS": "",
        "DESCRIÇÃO": "", "OS": "", "CLIENTE": "", "CLIENTE MUNICIPIO": "",
        "DEPARTAMENTO": "", "MUNICIPIO": "", "CODIGO DO CLIENTE": "",
        "DATA DA CRIACAO DA PROPOSTA": "", "DATA DA EMISSAO": "", "DATA DA APROVACAO": "",
        "DATA DA CONCLUSAO": "", "DATA DA SAIDA": "", "USUARIO DE CRIACAO": "",
        "MES/ANO": "", "CHAVETA": "", "CLASSIFICACAO DO ATRASO": "",
        "CLASSIFICACAO DO EQUIPAMENTO": "", "NOME DO VENDEDOR": "",
        "CORRENTE ALTA": "", "CORRENTE BAIXA": "", "DATA PROGRAMACAO DA COLETA": "",
        "DIMENSOES PARA TRANSPORTE": "", "DATA DA NOTA FISCAL CLIENTE": "",
        "DATA DE ENVIO ORCAMENTO": "", "DATA DE PREVISAO DE COLETA": "",
        "Nº CONTRATO": "", "TAREFA": "", "FABRICANTE": "", "FREQUANCIA (HZ)": "",
        "IMPEDANCIA": "", "MODELO": "", "Nº DA PROPOSTA": "", "STATUS DA OS": "",
        "TIPO DE SERVICO": "",
        "ACOPLAMENTO": "", "HASTE DO PORTA ESCOVA": "", "Nº PATRIMONIO DO CLIENTE": "",
        "Nº ORDEM COMPRA": "", "NF DATA ENGENHARIA": "", "NUMERO DE SERIE": "",
        "PESO DO OLEO": "", "PESO DO TANQUE": "", "POLARIDADE": "",
        "PORTA ESCOVA": "", "POTENCIA CV/HP": "", "ROTACAO (RPM)": "",
        "TIPO DE ESTATOR/CARCACA": "", "TENSAO DE ALTA": "", "TIPO DE MOTOR/GERADOR": "",
        "TIPO DE SERVICO GERAL": "", "TIPO DE TRANSFORMADOR": "", "VENTILADOR": "",
        "TENSAO DO ROTOR (V)": "", "DATA DE ACOMPANHAMENTO DO SERVICO": "",
        "DATA DE FIM DA PERITAGEM": "", "DATA DE FATURAMENTO": "", "DATA DE INICIO DO SERVICO": "",
        "TIPO DO EQUIPAMENTO": "", "DATA PROGRAMACAO PERITAGEM": "", "ESCOVAS DE CARVAO": "",
        "Nº OS DO CLIENTE": "", "TAG TIPO EQUIPAMENTO": "", "NF CLIENTE": "",
        "HISTORICO DO CLIENTE": "", "PESO DA PARTE ATIVA": "", "PESO TOTAL": "",
        "POLIA": "", "POTENCIA KVA": "", "POTENCIA KW": "", "TIPO DE ROTOR/ARMADURA": "",
        "TENSAO DE BAIXA": "", "OLEO": "", "TENSAO DO ESTATOR (V)": "",
        "VOLUME DO OLEO": "", "DATA DE ACOMPANHAMENTO DA PERITAGEM": "",
        "DATA DE AUTORIZACAO DO SERVICO": "", "DATA DE INICIO DA PERITAGEM": "",
        "TIPO CORRENTE": "", "OBSERVACAO NO RECEBIMENTO": ""
    }

    # Mapeamento dos rótulos da página para as chaves do JSON
    label_to_json_key = {
        "OS": "OS", "CLIENTE": "CLIENTE", "DEPARTAMENTO": "DEPARTAMENTO",
        "CODIGO DO CLIENTE": "CODIGO DO CLIENTE", "DATA DA EMISSAO": "DATA DA EMISSAO",
        "DATA DA CONCLUSAO": "DATA DA CONCLUSAO", "USUARIO DE CRIACAO": "USUARIO DE CRIACAO",
        "ACOPLAMENTO": "ACOPLAMENTO", "MES/ANO": "MES/ANO",
        "CLASSIFICACAO DO ATRASO": "CLASSIFICACAO DO ATRASO", "NOME DO VENDEDOR": "NOME DO VENDEDOR",
        "CORRENTE BAIXA": "CORRENTE BAIXA", "DESCRIÇÃO": "DESCRIÇÃO",
        "DATA DA NOTA FISCAL CLIENTE": "DATA DA NOTA FISCAL CLIENTE",
        "DATA DE PREVISAO DE COLETA": "DATA DE PREVISAO DE COLETA", "TAREFA": "TAREFA",
        "FABRICANTE": "FABRICANTE", "HASTE DO PORTA ESCOVA": "HASTE DO PORTA ESCOVA",
        "MODELO": "MODELO", "Nº PATRIMONIO DO CLIENTE": "Nº PATRIMONIO DO CLIENTE",
        "Nº ORDEM COMPRA": "Nº ORDEM COMPRA", "NF DATA ENGENHARIA": "NF DATA ENGENHARIA",
        "NUMERO DE SERIE": "NUMERO DE SERIE", "PESO DO OLEO": "PESO DO OLEO",
        "PESO DO TANQUE": "PESO DO TANQUE", "POLARIDADE": "POLARIDADE",
        "PORTA ESCOVA": "PORTA ESCOVA", "POTENCIA CV/HP": "POTENCIA CV/HP",
        "ROTACAO (RPM)": "ROTACAO (RPM)", "TIPO DE ESTATOR/CARCACA": "TIPO DE ESTATOR/CARCACA",
        "TENSAO DE ALTA": "TENSAO DE ALTA", "TIPO DE MOTOR/GERADOR": "TIPO DE MOTOR/GERADOR",
        "TIPO DE SERVICO GERAL": "TIPO DE SERVICO GERAL",
        "TIPO DE TRANSFORMADOR": "TIPO DE TRANSFORMADOR", "VENTILADOR": "VENTILADOR",
        "TENSAO DO ROTOR (V)": "TENSAO DO ROTOR (V)",
        "DATA DE ACOMPANHAMENTO DO SERVICO": "DATA DE ACOMPANHAMENTO DO SERVICO",
        "DATA DE FIM DA PERITAGEM": "DATA DE FIM DA PERITAGEM",
        "DATA DE FATURAMENTO": "DATA DE FATURAMENTO", "DATA DE INICIO DO SERVICO": "DATA DE INICIO DO SERVICO",
        "TIPO DO EQUIPAMENTO": "TIPO DO EQUIPAMENTO", "DATA PROGRAMACAO PERITAGEM": "DATA PROGRAMACAO PERITAGEM",
        "CENTRO DE CUSTO": "CENTRO DE CUSTO", "CNPJ": "CNPJ",
        "CLIENTE MUNICIPIO": "CLIENTE MUNICIPIO", "MUNICIPIO": "MUNICIPIO",
        "DATA DA CRIACAO DA PROPOSTA": "DATA DA CRIACAO DA PROPOSTA", "DATA DA APROVACAO": "DATA DA APROVACAO",
        "DATA DA SAIDA": "DATA DA SAIDA", "CHAVETA": "CHAVETA",
        "CLASSIFICACAO DO EQUIPAMENTO": "CLASSIFICACAO DO EQUIPAMENTO",
        "CORRENTE ALTA": "CORRENTE ALTA",
        "DATA PROGRAMACAO DA COLETA": "DATA PROGRAMACAO DA COLETA",
        "DIMENSOES PARA TRANSPORTE": "DIMENSOES PARA TRANSPORTE",
        "DATA DE ENVIO ORCAMENTO": "DATA DE ENVIO ORCAMENTO", "Nº CONTRATO": "Nº CONTRATO",
        "ESCOVAS DE CARVAO": "ESCOVAS DE CARVAO", "FREQUANCIA (HZ)": "FREQUANCIA (HZ)",
        "IMPEDANCIA": "IMPEDANCIA", "Nº OS DO CLIENTE": "Nº OS DO CLIENTE",
        "Nº DA PROPOSTA": "Nº DA PROPOSTA", "TAG TIPO EQUIPAMENTO": "TAG TIPO EQUIPAMENTO",
        "NF CLIENTE": "NF CLIENTE", "HISTORICO DO CLIENTE": "HISTORICO DO CLIENTE",
        "PESO DA PARTE ATIVA": "PESO DA PARTE ATIVA", "PESO TOTAL": "PESO TOTAL",
        "POLIA": "POLIA", "POTENCIA KVA": "POTENCIA KVA", "POTENCIA KW": "POTENCIA KW",
        "TIPO DE ROTOR/ARMADURA": "TIPO DE ROTOR/ARMADURA", "STATUS DA OS": "STATUS DA OS",
        "TIPO DE SERVICO": "TIPO DE SERVICO", "TENSAO DE BAIXA": "TENSAO DE BAIXA",
        "OLEO": "OLEO", "TENSAO DO ESTATOR (V)": "TENSAO DO ESTATOR (V)",
        "VOLUME DO OLEO": "VOLUME DO OLEO",
        "DATA DE ACOMPANHAMENTO DA PERITAGEM": "DATA DE ACOMPANHAMENTO DA PERITAGEM",
        "DATA DE AUTORIZACAO DO SERVICO": "DATA DE AUTORIZACAO DO SERVICO",
        "DATA DE INICIO DA PERITAGEM": "DATA DE INICIO DA PERITAGEM",
        "TIPO CORRENTE": "TIPO CORRENTE", "OBSERVACAO NO RECEBIMENTO": "OBSERVACAO NO RECEBIMENTO",
        "TIPO DE OS": "TIPO DE SERVICO",
        "ACESSORIO DO ROTOR": "ACESSORIO DO ROTOR",
        "ANEL DO PORTA ESCOVA": "ANEL DO PORTA ESCOVA",
    }

    try:
        current_os_data = os_template.copy() # Inicia um novo dicionário para esta OS

        # --- 1. Extrair Informações Globais (fora das abas) ---
        print("🔍 Tentando extrair informações globais da OS...")
        try:
            # Localizar um container que provavelmente contém essas informações de cabeçalho.
            global_info_container_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div[1]/div[1]'
            global_info_container = wait.until(EC.presence_of_element_located((By.XPATH, global_info_container_xpath)))

            global_text = global_info_container.text

            cnpj_match = re.search(r"CNPJ:\s*([\d./-]+)", global_text)
            if cnpj_match:
                current_os_data["CNPJ"] = cnpj_match.group(1).strip()
                print(f"   ✅ CNPJ global extraído: {current_os_data['CNPJ']}")

            codigo_cliente_match = re.search(r"CODIGO CLIENTE:\s*(\S+)", global_text)
            if codigo_cliente_match:
                current_os_data["CODIGO DO CLIENTE"] = codigo_cliente_match.group(1).strip()
                print(f"   ✅ CODIGO DO CLIENTE global extraído: {current_os_data['CODIGO DO CLIENTE']}")

            nome_cliente_match = re.search(r"NOME CLIENTE:\s*(.+?)(?=\n|CNPJ:|CODIGO CLIENTE:|$)", global_text, re.DOTALL)
            if nome_cliente_match:
                current_os_data["NOME CLIENTE"] = nome_cliente_match.group(1).strip()
                current_os_data["CLIENTE"] = nome_cliente_match.group(1).strip()
                print(f"   ✅ NOME CLIENTE global extraído: {current_os_data['NOME CLIENTE']}")

        except TimeoutException:
            print("⚠️ Não foi possível encontrar o container de informações globais no tempo limite.")
        except Exception as e:
            print(f"⚠️ Erro ao extrair informações globais: {e}")

        # --- 2. Extrair Informações do contêiner principal de detalhes (ant-card-body) ---
        details_container = wait_for_os_details_container(driver, wait)

        if not details_container:
            print("❌ Contêiner de detalhes da OS (ant-card-body) não encontrado. Não é possível raspar dados detalhados.")

            # Verificar se há pelo menos dados globais válidos
            if current_os_data.get("OS") or current_os_data.get("NOME CLIENTE") or current_os_data.get("CNPJ"):
                scraped_data_list.append(current_os_data)
                print("✅ Dados globais da OS coletados com sucesso, mas dados detalhados da aba não.")
            else:
                print("❌ Nenhum dado válido encontrado - OS pode não existir no sistema")

            return scraped_data_list

        print("✅ Contêiner de detalhes encontrado. Iniciando extração de dados das tags <p>...")

        p_elements = details_container.find_elements(By.TAG_NAME, "p")

        if not p_elements:
            print("⚠️ Nenhum tag <p> com dados encontrada no contêiner de detalhes.")
            if current_os_data.get("OS") or current_os_data.get("NOME CLIENTE") or current_os_data.get("CNPJ"):
                scraped_data_list.append(current_os_data)
                print("✅ Dados globais da OS coletados com sucesso, mas dados detalhados da aba não.")
            return scraped_data_list

        print(f"🔍 Encontrados {len(p_elements)} tags <p> para processar.")

        for p_element in p_elements:
            try:
                full_text = p_element.text.strip()

                label = ""
                value = ""

                # Tenta pegar o label do <b> se existir
                b_elements_in_p = p_element.find_elements(By.TAG_NAME, "b")
                if b_elements_in_p:
                    label = b_elements_in_p[0].text.strip().replace(":", "").strip() # Remove : e espaços extras

                # Se o label foi encontrado em <b>, o valor é o resto da string após ele e o ':'
                if label and full_text.startswith(label):
                    # Encontrar a posição do label e do primeiro ':' após ele
                    label_end_pos = full_text.find(label) + len(label)
                    colon_pos = full_text.find(':', label_end_pos)

                    if colon_pos != -1: # Se encontrou um ':'
                        value = full_text[colon_pos + 1:].strip()
                    else: # Se não tem ':', o valor é o que vem depois do label
                        value = full_text[label_end_pos:].strip()
                elif ":" in full_text: # Se não tem <b>, tenta dividir pelo primeiro ':'
                    parts = full_text.split(':', 1)
                    if len(parts) == 2:
                        label_from_text = parts[0].strip()
                        value = parts[1].strip()
                        if not label and label_from_text: # Se o label de <b> estava vazio, usa este
                            label = label_from_text
                else: # Se não encontrou nem <b> nem ':'
                    pass # Ignora parágrafos que não se encaixam no padrão chave:valor

                # Limpeza de caracteres especiais e valores placeholders
                placeholders = ["*", "***", "SELECIONE", "Nº", "*DESCRIÇÃ",
                                "SIMCLASSIFICACAO", "ARQUIVAR", "SIM", "NAO",
                                "OS", "LTDA", "- ITABIRITO", "ITABIRITO", "-", "EQUIPAMENTO SEM PLACA IDENTIFICAÇÃO."]

                original_value = value
                cleaned_value = value

                if cleaned_value: # Só tenta limpar se o valor não estiver vazio
                    for ph in placeholders:
                        # Se o valor é exatamente um placeholder (ignoring case)
                        if cleaned_value.strip().upper() == ph.upper():
                            cleaned_value = ""
                            break
                        # Se o placeholder faz parte do valor (ex: "AIR LIQUIDE BRASIL LTDA - ITABIRITO"), remove-o.
                        # Exceção para datas ou CNPJ que podem conter '-' e não devem ter partes removidas arbitrariamente.
                        if "DATA" not in label.upper() and "CNPJ" not in label.upper() and ph.strip() != "-": # Ignorar '-' como placeholder para evitar quebrar datas/CNPJ
                            cleaned_value = cleaned_value.replace(ph, "").strip()
                            # Limpeza adicional para evitar múltiplos espaços e hifens soltos
                            cleaned_value = re.sub(r'\s{2,}', ' ', cleaned_value).strip()
                            cleaned_value = re.sub(r'-\s*-', '-', cleaned_value).strip('-').strip() # Limpa múltiplos hifens e hifens no início/fim
                value = cleaned_value

                # Mapeamento e preenchimento dos dados
                json_key = label_to_json_key.get(label)
                if json_key and value != "": # Só atualiza se o valor não for vazio
                    # Prioriza dados globais se já existirem e forem válidos, exceto para campos específicos de tab que devem sobrescrever
                    if json_key in ["CNPJ", "CODIGO DO CLIENTE", "NOME CLIENTE", "CLIENTE"]:
                        if current_os_data[json_key] == "" or current_os_data[json_key].strip() == value.strip():
                            current_os_data[json_key] = value
                        # else: manter o valor global se já preenchido e diferente, para evitar regredir
                    else:
                        current_os_data[json_key] = value

                    # Lógica para campos redundantes ou especiais
                    if label == "OS":
                        # Remover zeros à esquerda do número da OS
                        os_numero_limpo = value.lstrip('0') if value and isinstance(value, str) else value
                        if not os_numero_limpo:  # Se ficou vazio após remover zeros, manter pelo menos um zero
                            os_numero_limpo = '0'
                        current_os_data["NÚMERO DA OS"] = os_numero_limpo
                        # Também atualizar o campo OS com o número limpo
                        current_os_data["OS"] = os_numero_limpo
                    elif label == "CLIENTE":
                        current_os_data["NOME CLIENTE"] = value
                        current_os_data["CLIENTE"] = value
                    elif label == "DEPARTAMENTO":
                        if not current_os_data["CENTRO DE CUSTO"]:
                            current_os_data["CENTRO DE CUSTO"] = value
                    elif label == "MUNICIPIO" and current_os_data["CLIENTE MUNICIPIO"] == "":
                        # Tentar preencher CLIENTE MUNICIPIO com MUNICIPIO se o primeiro estiver vazio
                        current_os_data["CLIENTE MUNICIPIO"] = value

                    print(f"   ✅ Mapeado '{label}' ('{value}') para '{json_key}'")
                elif label and value == "": # Se o rótulo foi encontrado mas o valor é vazio (após limpeza)
                    json_key = label_to_json_key.get(label)
                    if json_key:
                        current_os_data[json_key] = "" # Garante que o campo existe mas está vazio
                        print(f"   ✅ Mapeado '{label}' (vazio) para '{json_key}'")
                else:
                    print(f"   ⚠️ Rótulo '{label}' ('{original_value}') não possui mapeamento direto no JSON de saída ou valor vazio.")
            except Exception as e:
                print(f"⚠️ Erro ao processar tag <p>: {e}. Texto completo: '{p_element.text}'")
                continue

        # Verifica se dados essenciais foram coletados antes de adicionar
        if current_os_data.get("OS") or current_os_data.get("NOME CLIENTE") or current_os_data.get("CNPJ"):
            scraped_data_list.append(current_os_data)
            print("✅ Dados da OS (globais e detalhados) coletados com sucesso.")
        else:
            print("❌ Dados da OS insuficientes para serem considerados um registro válido após extração detalhada.")

    except Exception as e:
        print(f"❌ Erro geral no scraping dos detalhes da OS: {e}")
        import traceback
        traceback.print_exc()

    return scraped_data_list

def execute_scraping(os_number):
    """Função principal para executar o scraping de uma OS específica."""
    site_url = os.getenv("SITE_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not all([site_url, username, password]):
        raise Exception("SITE_URL, USERNAME, ou PASSWORD não encontrados no arquivo .env")

    if not os_number or not os_number.strip():
        raise Exception("Número da OS é obrigatório para o scraping")

    driver = None
    wait = None

    try:
        driver = get_driver()
        wait = WebDriverWait(driver, 30) # Timeout aumentado para detecção de elementos

        if login(driver, wait, site_url, username, password, os_number):
            print("Login bem-sucedido e busca realizada. Iniciando o scraping dos detalhes da OS...")
            scraped_data = scrape_os_details_data_only(driver, wait)

            # Verificar se dados foram coletados
            if not scraped_data or len(scraped_data) == 0:
                print(f"❌ Nenhum dado coletado para OS {os_number} - OS pode não existir")
                return []

            # Verificar se os dados coletados são válidos
            valid_data = []
            for data in scraped_data:
                if data.get("OS") or data.get("NOME CLIENTE") or data.get("CNPJ"):
                    valid_data.append(data)
                else:
                    print(f"⚠️ Dados inválidos descartados: {data}")

            if not valid_data:
                print(f"❌ Nenhum dado válido encontrado para OS {os_number}")
                return []

            print(f"✅ {len(valid_data)} registro(s) válido(s) coletado(s) para OS {os_number}")
            return valid_data
        else:
            raise Exception(f"Falha no login ou na busca da OS {os_number}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado no processo principal: {e}")
        # Não re-raise para permitir tratamento mais suave no backend
        return []
    finally:
        if driver:
            print("Fechando o navegador.")
            driver.quit()

if __name__ == "__main__":
    # Para teste direto do script
    os_number = sys.argv[1] if len(sys.argv) > 1 else "12345"
    result = execute_scraping(os_number)
    print(f"Resultado: {result}")
