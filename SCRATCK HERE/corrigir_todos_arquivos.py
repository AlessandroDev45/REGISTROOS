#!/usr/bin/env python3
"""
Script para corrigir todos os problemas nos arquivos de rotas
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
    
    print(f"🔧 Corrigindo {nome_arquivo}...")
    
    # Correções principais
    correções = [
        # Corrigir == True para .is_(True)
        (r'\.ativo == True', r'.ativo.is_(True)'),
        (r'\.is_approved == True', r'.is_approved.is_(True)'),
        (r'\.teste_exclusivo_setor == True', r'.teste_exclusivo_setor.is_(True)'),
        (r'\.pendencia == True', r'.pendencia.is_(True)'),
        (r'\.foi_retrabalho == True', r'.foi_retrabalho.is_(True)'),
        (r'\.aprovado_supervisor == True', r'.aprovado_supervisor.is_(True)'),
        (r'\.trabalha_producao == True', r'.trabalha_producao.is_(True)'),
        
        # Corrigir == False para .is_(False)
        (r'\.ativo == False', r'.ativo.is_(False)'),
        (r'\.is_approved == False', r'.is_approved.is_(False)'),
        (r'\.teste_exclusivo_setor == False', r'.teste_exclusivo_setor.is_(False)'),
        (r'\.foi_retrabalho == False', r'.foi_retrabalho.is_(False)'),
        (r'\.aprovado_supervisor == False', r'.aprovado_supervisor.is_(False)'),
        (r'\.trabalha_producao == False', r'.trabalha_producao.is_(False)'),
        
        # Corrigir nomes de modelos incorretos
        (r'DescricaoAtividade', r'TipoDescricaoAtividade'),
        (r'CausaRetrabalho', r'TipoCausaRetrabalho'),
        
        # Corrigir datetime deprecated
        (r'datetime\.datetime\.utcnow\(\)', r'datetime.datetime.now()'),
        
        # Corrigir problemas de datetime
        (r'\.isoformat\(\) if ([a-zA-Z_]+\.[a-zA-Z_]+) else None', r'.isoformat() if \1 is not None else None'),
        
        # Corrigir comparações com None
        (r'if ([a-zA-Z_]+\.[a-zA-Z_]+):', r'if \1 is not None:'),
        (r'if not ([a-zA-Z_]+\.[a-zA-Z_]+):', r'if \1 is None:'),
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
        ("auth.py", "auth.py"),
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
    
    print("\n🎉 TODAS AS CORREÇÕES CONCLUÍDAS!")

if __name__ == "__main__":
    main()
