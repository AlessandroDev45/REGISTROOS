#!/usr/bin/env python3
"""
Script para adicionar refs aos divs dos formulários
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

def adicionar_ref_formulario(nome_arquivo):
    """Adiciona ref ao div principal do formulário"""
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    print(f"🔧 Adicionando ref ao {nome_arquivo}...")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Procurar pelo padrão do div principal e adicionar ref se não existir
    padrao_div = r'<div className="(p-6 bg-white rounded-lg shadow-md|bg-white shadow-md rounded-lg p-6)">'
    
    if 'ref={formRef}' not in conteudo:
        # Adicionar ref ao div principal
        conteudo = re.sub(
            padrao_div,
            r'<div ref={formRef} className="\1">',
            conteudo
        )
    
    # Salvar arquivo corrigido
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ {nome_arquivo} - ref adicionada!")
    return True

def main():
    print("🚀 ADICIONANDO REFS AOS FORMULÁRIOS")
    print("=" * 50)
    
    sucessos = 0
    for formulario in FORMULARIOS:
        if adicionar_ref_formulario(formulario):
            sucessos += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 CONCLUÍDO! {sucessos}/{len(FORMULARIOS)} formulários corrigidos")

if __name__ == "__main__":
    main()
