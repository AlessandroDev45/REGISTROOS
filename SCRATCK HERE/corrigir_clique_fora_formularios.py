#!/usr/bin/env python3
"""
Script para corrigir clique fora em formulários específicos
"""

import os
import re

# Lista de formulários para corrigir
FORMULARIOS = [
    'TipoFalhaForm.tsx',
    'DescricaoAtividadeForm.tsx',
    'CausaRetrabalhoForm.tsx'
]

BASE_PATH = "RegistroOS/registrooficial/frontend/src/features/admin/components/config"

def corrigir_clique_fora(nome_arquivo):
    """Corrige clique fora em um formulário"""
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    print(f"🖱️ Corrigindo clique fora em {nome_arquivo}...")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 1. Verificar se já tem useClickOutside importado
    if 'useClickOutside' not in conteudo:
        print(f"  ⚠️ useClickOutside não encontrado em {nome_arquivo}")
        return False
    
    # 2. Adicionar hook se não existir
    if 'formRef = useClickOutside' not in conteudo:
        # Encontrar onde adicionar o hook (após os useState)
        pattern = r'(const \[.*?\] = useState.*?\n)'
        matches = list(re.finditer(pattern, conteudo))
        
        if matches:
            # Adicionar após o último useState
            last_match = matches[-1]
            insert_pos = last_match.end()
            
            hook_code = '\n    // Hook para fechar ao clicar fora\n    const formRef = useClickOutside<HTMLDivElement>(onCancel);\n'
            conteudo = conteudo[:insert_pos] + hook_code + conteudo[insert_pos:]
            print(f"  ✅ Hook useClickOutside adicionado")
    
    # 3. Adicionar ref na div principal se não existir
    if 'ref={formRef}' not in conteudo:
        # Procurar pela div principal
        div_pattern = r'(<div className="p-6 bg-white rounded-lg shadow-md">)'
        if re.search(div_pattern, conteudo):
            conteudo = re.sub(div_pattern, r'<div ref={formRef} className="p-6 bg-white rounded-lg shadow-md">', conteudo)
            print(f"  ✅ ref={{formRef}} adicionado à div principal")
    
    # Salvar arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ {nome_arquivo} corrigido com sucesso!")
    return True

def main():
    print("🖱️ CORRIGINDO CLIQUE FORA EM FORMULÁRIOS")
    print("=" * 50)
    
    sucessos = 0
    for formulario in FORMULARIOS:
        if corrigir_clique_fora(formulario):
            sucessos += 1
        print()
    
    print(f"🏁 CONCLUÍDO! {sucessos}/{len(FORMULARIOS)} formulários corrigidos")

if __name__ == "__main__":
    main()
