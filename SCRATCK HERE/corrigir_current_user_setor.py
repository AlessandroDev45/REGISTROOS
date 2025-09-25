#!/usr/bin/env python3
"""
Script para corrigir todas as referências a current_user.setor no sistema
"""

import os
import re
from datetime import datetime

# Configurações
BACKEND_DIR = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"

def corrigir_current_user_setor():
    """Corrigir referências a current_user.setor nos arquivos Python"""
    arquivo_path = os.path.join(BACKEND_DIR, "routes/desenvolvimento.py")
    
    if not os.path.exists(arquivo_path):
        print(f"⚠️ Arquivo não encontrado: {arquivo_path}")
        return
    
    print(f"🔧 Corrigindo: routes/desenvolvimento.py")
    
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        
        # Padrões específicos para corrigir
        correcoes = [
            # 1. Filtros de query com Usuario.setor
            (r'Usuario\.setor == current_user\.setor', 'Usuario.id_setor == current_user.id_setor'),
            
            # 2. Filtros de query com ApontamentoDetalhado.setor
            (r'ApontamentoDetalhado\.setor == current_user\.setor', 'ApontamentoDetalhado.id_setor == current_user.id_setor'),
            
            # 3. Filtros de query com OrdemServico.setor
            (r'OrdemServico\.setor == current_user\.setor', 'OrdemServico.id_setor == current_user.id_setor'),
            
            # 4. Filtros de query com TipoMaquina.setor
            (r'TipoMaquina\.setor == current_user\.setor', 'TipoMaquina.id_setor == current_user.id_setor'),
            
            # 5. Comparações diretas com pendencia.setor
            (r'pendencia\.setor != current_user\.setor', 'pendencia.id_setor != current_user.id_setor'),
            
            # 6. Comparações diretas com programacao.setor
            (r'programacao\.setor != current_user\.setor', 'programacao.id_setor != current_user.id_setor'),
            
            # 7. Comparações diretas com usuario_filtrado.setor
            (r'usuario_filtrado\.setor == current_user\.setor', 'usuario_filtrado.id_setor == current_user.id_setor'),
            
            # 8. Atribuições diretas de setor
            (r'setor=current_user\.setor,', 'setor="Não informado",  # Será atualizado via id_setor'),
            
            # 9. Uso em dicionários
            (r'"setor_responsavel": current_user\.setor', '"setor_responsavel": "Não informado"  # Será atualizado via id_setor'),
            
            # 10. Condicionais if current_user.setor
            (r'if current_user\.setor:', 'if current_user.id_setor:'),
            
            # 11. Busca de setor por nome
            (r'Setor\.nome == current_user\.setor', 'Setor.id == current_user.id_setor'),
        ]
        
        total_correcoes = 0
        
        for padrao, substituicao in correcoes:
            matches = re.findall(padrao, conteudo)
            if matches:
                conteudo = re.sub(padrao, substituicao, conteudo)
                total_correcoes += len(matches)
                print(f"  ✅ {len(matches)} correções para: {padrao}")
        
        # Correções específicas para linhas problemáticas
        
        # Linha 191: query.join(Usuario).filter(Usuario.setor == current_user.setor)
        conteudo = re.sub(
            r'query\.join\(Usuario\)\.filter\(Usuario\.id_setor == current_user\.id_setor\)',
            'query.filter(ApontamentoDetalhado.id_setor == current_user.id_setor)',
            conteudo
        )
        
        # Linha 1314: setor = db.query(Setor).filter(Setor.id == current_user.id_setor).first()
        # Esta já está correta após a correção anterior
        
        if conteudo != conteudo_original:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"  📝 {total_correcoes} correções aplicadas")
        else:
            print(f"  ℹ️ Nenhuma correção necessária")
        
        return total_correcoes
        
    except Exception as e:
        print(f"  ❌ Erro ao processar arquivo: {e}")
        return 0

def main():
    print("🚀 Iniciando correção de referências current_user.setor...")
    print("=" * 60)
    
    total_correcoes = corrigir_current_user_setor()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA CORREÇÃO:")
    print(f"  - Total de correções aplicadas: {total_correcoes}")
    print("✅ Correção concluída!")

if __name__ == "__main__":
    main()
