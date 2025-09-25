import json
import os
import re

def parse_file(input_file_path, output_file_path):
    """
    Analisa o arquivo de texto e extrai todos os dados das Ordens de Serviço (OS).

    Args:
        input_file_path (str): O caminho para o arquivo de texto de entrada.
        output_file_path (str): O caminho para o arquivo JSON de saída.
    """
    if not os.path.exists(input_file_path):
        print(f"Erro: O arquivo '{input_file_path}' não foi encontrado.")
        return

    with open(input_file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    os_list = []
    # Usando um marcador de início de OS mais robusto
    os_pattern_start_marker = "CODIGO CLIENTE:"

    # Dividir o conteúdo em blocos usando o marcador de início de OS
    raw_os_blocks = content.split(os_pattern_start_marker)[1:] # Pula o primeiro vazio se houver

    for block in raw_os_blocks:
        current_os_data = {}
        lines_in_block = block.strip().split('\n')

        for line in lines_in_block:
            line = line.strip()
            if not line:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Aplica a formatação específica para campos de número de OS
                if key == "NÚMERO DA OS" or key == "OS" or key == "Nº CONTRATO" or \
                   key == "Nº DA PROPOSTA" or key == "Nº ORDEM COMPRA" or \
                   key == "Nº OS DO CLIENTE" or key == "Nº PATRIMONIO DO CLIENTE" or \
                   key == "CODIGO DO CLIENTE" or key == "TAG TIPO EQUIPAMENTO" or \
                   key == "NF DATA ENGENHARIA" or key == "NF CLIENTE" or \
                   key == "NUMERO DE SERIE" or key == "HISTORICO DO CLIENTE" or \
                   key == "PESO DO OLEO" or key == "PESO DA PARTE ATIVA" or \
                   key == "PESO DO TANQUE" or key == "PESO TOTAL" or \
                   key == "POLARIDADE" or key == "POTENCIA KVA" or \
                   key == "POTENCIA CV/HP" or key == "POTENCIA KW" or \
                   key == "ROTACAO (RPM)" or key == "TIPO DE ROTOR/ARMADURA" or \
                   key == "TIPO DE ESTATOR/CARCACA" or key == "STATUS DA OS" or \
                   key == "TENSAO DE ALTA" or key == "TENSAO DE BAIXA" or \
                   key == "TIPO DE MOTOR/GERADOR" or key == "TIPO DE SERVICO" or \
                   key == "TIPO DE SERVICO GERAL" or key == "TIPO SERVICO TRANSFORMADOR" or \
                   key == "TIPO DE TRANSFORMADOR" or key == "OLEO" or \
                   key == "TENSAO DO ESTATOR (V)" or key == "TENSAO DO ROTOR (V)" or \
                   key == "VOLUME DO OLEO" or key == "TIPO DE OS" or \
                   key == "DATA DE ACOMPANHAMENTO DA PERITAGEM" or \
                   key == "DATA DE ACOMPANHAMENTO DO SERVICO" or \
                   key == "DATA DE AUTORIZACAO DO SERVICO" or \
                   key == "DATA DE FIM DA PERITAGEM" or \
                   key == "DATA DE INICIO DA PERITAGEM" or \
                   key == "DATA DE FATURAMENTO" or \
                   key == "DATA DE FIM DO SERVICO" or \
                   key == "DATA DE INICIO DO SERVICO" or \
                   key == "TIPO CORRENTE" or key == "TIPO DO EQUIPAMENTO" or \
                   key == "OBSERVACAO NO RECEBIMENTO" or key == "DATA PROGRAMACAO PERITAGEM" or \
                   key == "DATA DE PROGRAMACAO DA COLETA" or key == "MES/ANO":
                    # Remove zeros à esquerda e trata campos que poderiam ser numéricos
                    if value.isdigit():
                        value = str(int(value))
                    # Para campos como "MES/ANO" que não são apenas dígitos, mas podem ter zeros à esquerda em partes
                    elif "/" in value: # Ex: "05/2025"
                        parts = value.split('/')
                        formatted_parts = [str(int(p)) if p.isdigit() else p for p in parts]
                        value = "/".join(formatted_parts)

                current_os_data[key] = value

        if current_os_data:
            os_list.append(current_os_data)

    print(f"Arquivo '{input_file_path}' lido com sucesso.")
    print(f"Encontrados {len(os_list)} registros de OS.")

    # Escreve os dados parseados em um arquivo JSON
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(os_list, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em '{output_file_path}'.")

if __name__ == "__main__":
    # Define os caminhos de entrada e saída
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "dadosOS.txt")
    output_file = os.path.join(script_dir, "dadosOS.json")

    parse_file(input_file, output_file)
