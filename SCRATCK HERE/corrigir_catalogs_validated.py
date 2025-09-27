#!/usr/bin/env python3
"""
Script para corrigir todos os problemas no arquivo catalogs_validated.py
"""

import re

def corrigir_arquivo():
    arquivo_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\routes\catalogs_validated.py"
    
    # Ler o arquivo
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print("🔧 Iniciando correções...")
    
    # Correções principais
    correções = [
        # Corrigir == True para .is_(True)
        (r'\.ativo == True', r'.ativo.is_(True)'),
        (r'\.is_approved == True', r'.is_approved.is_(True)'),
        (r'\.teste_exclusivo_setor == True', r'.teste_exclusivo_setor.is_(True)'),
        (r'\.pendencia == True', r'.pendencia.is_(True)'),
        
        # Corrigir == False para .is_(False)
        (r'\.ativo == False', r'.ativo.is_(False)'),
        (r'\.is_approved == False', r'.is_approved.is_(False)'),
        (r'\.teste_exclusivo_setor == False', r'.teste_exclusivo_setor.is_(False)'),
        
        # Corrigir nomes de modelos incorretos
        (r'DescricaoAtividade', r'TipoDescricaoAtividade'),
        (r'CausaRetrabalho', r'TipoCausaRetrabalho'),
        
        # Corrigir comparações com colunas SQLAlchemy
        (r'if ([a-zA-Z_]+\.[a-zA-Z_]+):', r'if \1 is not None:'),
        (r'if not ([a-zA-Z_]+\.[a-zA-Z_]+):', r'if \1 is None:'),
        
        # Corrigir problemas de datetime
        (r'\.isoformat\(\) if ([a-zA-Z_]+\.[a-zA-Z_]+) else None', r'.isoformat() if \1 is not None else None'),
    ]
    
    # Aplicar correções
    for padrao, substituicao in correções:
        conteudo_anterior = conteudo
        conteudo = re.sub(padrao, substituicao, conteudo)
        if conteudo != conteudo_anterior:
            print(f"✅ Aplicada correção: {padrao} -> {substituicao}")
    
    # Salvar arquivo corrigido
    with open(arquivo_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("🎉 Correções aplicadas com sucesso!")

if __name__ == "__main__":
    corrigir_arquivo()
