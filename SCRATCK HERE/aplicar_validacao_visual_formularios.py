#!/usr/bin/env python3
"""
Script para aplicar validação visual em todos os formulários
"""

import os
import re

# Lista de formulários para corrigir
FORMULARIOS = [
    'TipoAtividadeForm.tsx',
    'TipoFalhaForm.tsx', 
    'DescricaoAtividadeForm.tsx',
    'CausaRetrabalhoForm.tsx'
]

BASE_PATH = "RegistroOS/registrooficial/frontend/src/features/admin/components/config"

def aplicar_validacao_visual(nome_arquivo):
    """Aplica validação visual em um formulário"""
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    print(f"🎨 Aplicando validação visual em {nome_arquivo}...")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 1. Substituir StyledInput por input com validação visual
    if 'StyledInput' in conteudo and 'id="nome"' in conteudo:
        # Padrão para encontrar StyledInput do nome
        styled_input_pattern = r'<StyledInput\s+id="nome"[^>]*name="nome"[^>]*value=\{formData\.nome\}[^>]*\/>'
        
        if re.search(styled_input_pattern, conteudo):
            novo_input = '''<input
                        type="text"
                        id="nome"
                        name="nome"
                        value={formData.nome}
                        onChange={handleInputChange}
                        placeholder="Digite o nome"
                        required
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
                            errors.nome 
                                ? 'border-red-500 focus:ring-red-500' 
                                : formData.nome.trim()
                                    ? 'border-green-500 focus:ring-green-500'
                                    : 'border-gray-300 focus:ring-blue-500'
                        }`}
                    />
                    {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
                    {!errors.nome && !formData.nome.trim() && (
                        <p className="mt-1 text-sm text-gray-500">Digite o nome para habilitar o botão</p>
                    )}
                    {!errors.nome && formData.nome.trim() && (
                        <p className="mt-1 text-sm text-green-600">✓ Nome válido</p>
                    )}'''
            
            conteudo = re.sub(styled_input_pattern, novo_input, conteudo)
            print(f"  ✅ Input do nome corrigido")
    
    # 2. Corrigir botão submit para ser desabilitado quando nome está vazio
    button_pattern = r'<button\s+type="submit"[^>]*className="[^"]*"[^>]*>\s*\{[^}]*\}\s*</button>'
    
    if re.search(button_pattern, conteudo):
        novo_botao = '''<button
                        type="submit"
                        disabled={!formData.nome.trim()}
                        className={`px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
                            formData.nome.trim() 
                                ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500' 
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                    >
                        {isEdit ? 'Confirmar Edição' : 'Adicionar'}
                    </button>'''
        
        conteudo = re.sub(button_pattern, novo_botao, conteudo)
        print(f"  ✅ Botão submit corrigido")
    
    # 3. Remover imports não utilizados
    if 'StyledInput' in conteudo and '<StyledInput' not in conteudo:
        # Remover StyledInput dos imports
        conteudo = re.sub(r'StyledInput,?\s*', '', conteudo)
        conteudo = re.sub(r',\s*StyledInput', '', conteudo)
        print(f"  ✅ Import StyledInput removido")
    
    # Salvar arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ {nome_arquivo} atualizado com sucesso!")
    return True

def main():
    print("🎨 APLICANDO VALIDAÇÃO VISUAL EM TODOS OS FORMULÁRIOS")
    print("=" * 60)
    
    sucessos = 0
    for formulario in FORMULARIOS:
        if aplicar_validacao_visual(formulario):
            sucessos += 1
        print()
    
    print(f"🏁 CONCLUÍDO! {sucessos}/{len(FORMULARIOS)} formulários atualizados")

if __name__ == "__main__":
    main()
