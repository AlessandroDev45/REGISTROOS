#!/usr/bin/env python3
"""
Script para corrigir todos os formulários com:
1. Funcionalidade de fechar ao clicar fora
2. Corrigir problema de campos que se limpam
"""

import os
import re

# Lista de formulários para corrigir
FORMULARIOS = [
    'TipoAtividadeForm.tsx',
    'TipoFalhaForm.tsx', 
    'TipoTesteForm.tsx',
    'DescricaoAtividadeForm.tsx',
    'CausaRetrabalhoForm.tsx'
]

BASE_PATH = "RegistroOS/registrooficial/frontend/src/features/admin/components/config"

def corrigir_formulario(nome_arquivo):
    """Corrige um formulário específico"""
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    print(f"🔧 Corrigindo {nome_arquivo}...")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 1. Adicionar import do useClickOutside se não existir
    if 'useClickOutside' not in conteudo:
        # Encontrar a linha de imports do React
        import_react = re.search(r"import React, \{ ([^}]+) \} from 'react';", conteudo)
        if import_react:
            imports_atuais = import_react.group(1)
            if 'useRef' in imports_atuais:
                # Remover useRef e adicionar apenas o que precisamos
                novos_imports = imports_atuais.replace('useRef', '').replace(', ,', ',').strip(', ')
            else:
                novos_imports = imports_atuais
            
            nova_linha_react = f"import React, {{ {novos_imports} }} from 'react';"
            conteudo = conteudo.replace(import_react.group(0), nova_linha_react)
        
        # Adicionar import do useClickOutside após os imports do React
        linhas = conteudo.split('\n')
        for i, linha in enumerate(linhas):
            if linha.startswith("import React"):
                # Inserir após a linha de imports do React
                linhas.insert(i + 1, "import { useClickOutside } from '../../../../hooks/useClickOutside';")
                break
        conteudo = '\n'.join(linhas)
    
    # 2. Substituir useRef por useClickOutside
    conteudo = re.sub(
        r'const formRef = useRef<HTMLDivElement>\(null\);',
        'const formRef = useClickOutside<HTMLDivElement>(onCancel);',
        conteudo
    )
    
    # 3. Remover useEffect de clique fora se existir
    conteudo = re.sub(
        r'// Detectar clique fora.*?}, \[onCancel\]\);',
        '',
        conteudo,
        flags=re.DOTALL
    )
    
    # 4. Corrigir useEffect de initialData para só executar em edição
    conteudo = re.sub(
        r'useEffect\(\(\) => \{\s*if \(initialData\) \{',
        'useEffect(() => {\n        if (initialData && isEdit) {',
        conteudo
    )
    
    # 5. Adicionar isEdit na dependência do useEffect se não existir
    conteudo = re.sub(
        r'}, \[initialData\]\);',
        '}, [initialData, isEdit]);',
        conteudo
    )
    
    # Salvar arquivo corrigido
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ {nome_arquivo} corrigido!")
    return True

def main():
    print("🚀 CORRIGINDO TODOS OS FORMULÁRIOS")
    print("=" * 50)
    
    sucessos = 0
    for formulario in FORMULARIOS:
        if corrigir_formulario(formulario):
            sucessos += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 CONCLUÍDO! {sucessos}/{len(FORMULARIOS)} formulários corrigidos")
    
    print("\n📋 CORREÇÕES APLICADAS:")
    print("✅ Adicionado import useClickOutside")
    print("✅ Substituído useRef por useClickOutside")
    print("✅ Removido useEffect de clique fora manual")
    print("✅ Corrigido useEffect de initialData para só executar em edição")
    print("✅ Adicionado isEdit nas dependências do useEffect")

if __name__ == "__main__":
    main()
