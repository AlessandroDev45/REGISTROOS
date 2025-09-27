#!/usr/bin/env python3
"""
Script para corrigir nomes incorretos criados pelo script anterior
"""

import re
import os

def corrigir_arquivo(arquivo_path, nome_arquivo):
    if not os.path.exists(arquivo_path):
        print(f"❌ Arquivo não encontrado: {arquivo_path}")
        return
    
    # Ler o arquivo
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print(f"🔧 Corrigindo nomes incorretos em {nome_arquivo}...")
    
    # Correções de nomes incorretos
    correções = [
        # Corrigir nomes duplicados incorretos
        (r'TipoTipoTipoDescricaoAtividade', r'TipoDescricaoAtividade'),
        (r'TipoTipoTipoCausaRetrabalho', r'TipoCausaRetrabalho'),
        (r'TipoTipoDescricaoAtividade', r'TipoDescricaoAtividade'),
        (r'TipoTipoCausaRetrabalho', r'TipoCausaRetrabalho'),
    ]
    
    # Aplicar correções
    total_correções = 0
    for padrao, substituicao in correções:
        conteudo_anterior = conteudo
        conteudo = re.sub(padrao, substituicao, conteudo)
        if conteudo != conteudo_anterior:
            total_correções += 1
            print(f"  ✅ {padrao} -> {substituicao}")
    
    # Salvar arquivo corrigido
    with open(arquivo_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"  🎉 {total_correções} correções aplicadas em {nome_arquivo}")

def main():
    base_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\routes"
    
    arquivos = [
        ("catalogs_simple.py", "catalogs_simple.py"),
        ("catalogs_validated.py", "catalogs_validated.py"),
        ("desenvolvimento.py", "desenvolvimento.py"),
        ("general.py", "general.py"),
        ("os_routes_simple.py", "os_routes_simple.py"),
        ("pcp_routes_backup.py", "pcp_routes_backup.py"),
        ("relatorio_completo.py", "relatorio_completo.py"),
    ]
    
    for arquivo, nome in arquivos:
        arquivo_path = os.path.join(base_path, arquivo)
        corrigir_arquivo(arquivo_path, nome)
    
    print("\n🎉 TODAS AS CORREÇÕES DE NOMES CONCLUÍDAS!")

if __name__ == "__main__":
    main()
