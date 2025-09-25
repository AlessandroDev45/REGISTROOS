#!/usr/bin/env python3
"""
Script para corrigir referências ao campo 'setor' removido do modelo ApontamentoDetalhado
"""

import os
import re

def corrigir_referencias_apontamento_setor():
    """Corrige referências ao campo 'setor' removido do ApontamentoDetalhado"""
    
    arquivo = r"RegistroOS\registrooficial\backend\routes\desenvolvimento.py"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    print(f"🔧 Corrigindo referências em: {arquivo}")
    
    # Ler o arquivo
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Backup
    backup_file = arquivo + ".backup_apontamento_setor"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"💾 Backup criado: {backup_file}")
    
    # Correções específicas
    correcoes = [
        # 1. Linha 731: setor_nome = apontamento.setor or "Não informado"
        (
            r'setor_nome = apontamento\.setor or "Não informado"',
            '''# Buscar setor através do id_setor
                    setor = db.query(Setor).filter(Setor.id == apontamento.id_setor).first()
                    setor_nome = setor.nome if setor else "Não informado"'''
        ),
        
        # 2. Linhas 1694, 1747, 1815, 2047: apontamento.setor != current_user.setor
        (
            r'if apontamento\.setor != current_user\.setor:',
            '''# Buscar setor do apontamento através do id_setor
            apontamento_setor = db.query(Setor).filter(Setor.id == apontamento.id_setor).first()
            current_user_setor = db.query(Setor).filter(Setor.id == current_user.id_setor).first()
            if (not apontamento_setor or not current_user_setor or 
                apontamento_setor.nome != current_user_setor.nome):'''
        ),
        
        # 3. Linha 1893: query.filter(ApontamentoDetalhado.setor == current_user.setor)
        (
            r'query\.filter\(ApontamentoDetalhado\.setor == current_user\.setor\)',
            'query.filter(ApontamentoDetalhado.id_setor == current_user.id_setor)'
        ),
        
        # 4. Linha 1899: usuario_filtrado.setor == current_user.setor
        (
            r'usuario_filtrado\.setor == current_user\.setor',
            'usuario_filtrado.id_setor == current_user.id_setor'
        )
    ]
    
    # Aplicar correções
    conteudo_corrigido = conteudo
    for padrao, substituicao in correcoes:
        matches = re.findall(padrao, conteudo_corrigido)
        if matches:
            print(f"  ✅ Corrigindo: {len(matches)} ocorrência(s) de '{padrao}'")
            conteudo_corrigido = re.sub(padrao, substituicao, conteudo_corrigido)
        else:
            print(f"  ⚠️ Padrão não encontrado: '{padrao}'")
    
    # Salvar arquivo corrigido
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_corrigido)
    
    print(f"✅ Arquivo corrigido: {arquivo}")
    return True

if __name__ == "__main__":
    print("🚀 Iniciando correção de referências ao campo 'setor' do ApontamentoDetalhado...")
    
    if corrigir_referencias_apontamento_setor():
        print("\n🎉 Correção concluída com sucesso!")
        print("\n📋 Resumo das correções:")
        print("  • apontamento.setor → busca via id_setor")
        print("  • Comparações de setor → comparações via id_setor")
        print("  • Filtros por setor → filtros por id_setor")
    else:
        print("\n❌ Erro durante a correção!")
