#!/usr/bin/env python3
"""
Script para verificar loops infinitos em useEffect nos formulários
"""

import os
import re

# Lista de formulários para verificar
FORMULARIOS = [
    'TipoAtividadeForm.tsx',
    'TipoFalhaForm.tsx', 
    'TipoTesteForm.tsx',
    'DescricaoAtividadeForm.tsx',
    'CausaRetrabalhoForm.tsx',
    'DepartamentoForm.tsx',
    'SetorForm.tsx',
    'TipoMaquinaForm.tsx'
]

BASE_PATH = "RegistroOS/registrooficial/frontend/src/features/admin/components/config"

def verificar_loops_useeffect(nome_arquivo):
    """Verifica loops infinitos em useEffect"""
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    print(f"🔍 Verificando {nome_arquivo}...")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    problemas = []
    
    # Procurar por useEffect que modifica suas próprias dependências
    useeffects = re.findall(r'useEffect\(\(\) => \{(.*?)\}, \[(.*?)\]\);', conteudo, re.DOTALL)
    
    for i, (corpo, deps) in enumerate(useeffects):
        # Verificar se o corpo do useEffect modifica alguma de suas dependências
        deps_list = [dep.strip() for dep in deps.split(',') if dep.strip()]
        
        for dep in deps_list:
            # Procurar por setState da dependência
            if dep.startswith('formData.'):
                campo = dep.split('.')[1]
                if f'setFormData' in corpo:
                    problemas.append(f"useEffect #{i+1}: modifica formData.{campo} que é dependência")
            elif dep in ['setores', 'departamentos', 'tiposMaquina']:
                setter = f'set{dep.capitalize()}'
                if setter in corpo:
                    problemas.append(f"useEffect #{i+1}: modifica {dep} que é dependência")
    
    # Verificar useEffect sem dependências que modifica estado
    useeffects_sem_deps = re.findall(r'useEffect\(\(\) => \{(.*?)\}\);', conteudo, re.DOTALL)
    for i, corpo in enumerate(useeffects_sem_deps):
        if 'setState' in corpo or 'setFormData' in corpo:
            problemas.append(f"useEffect sem deps #{i+1}: modifica estado sem dependências")
    
    if problemas:
        print(f"⚠️  {nome_arquivo} - PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   - {problema}")
    else:
        print(f"✅ {nome_arquivo} - OK")
    
    return len(problemas) == 0

def main():
    print("🚀 VERIFICANDO LOOPS INFINITOS EM useEffect")
    print("=" * 60)
    
    ok_count = 0
    for formulario in FORMULARIOS:
        if verificar_loops_useeffect(formulario):
            ok_count += 1
        print()
    
    print("=" * 60)
    print(f"🏁 VERIFICAÇÃO CONCLUÍDA! {ok_count}/{len(FORMULARIOS)} formulários OK")

if __name__ == "__main__":
    main()
