#!/usr/bin/env python3
"""
Script para corrigir referências a campos que não existem nos modelos
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Cria backup do arquivo antes de modificar"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path

def fix_catalogs_file(file_path):
    """Corrige o arquivo catalogs_validated.py"""
    print(f"\n🔧 Corrigindo: {file_path}")
    
    # Criar backup
    backup_file(file_path)
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remover filtros por id_setor em TipoTeste (não existe)
    content = re.sub(r'TipoTeste\.id_setor == [^,)]+,?\s*', '', content)
    content = re.sub(r',\s*TipoTeste\.id_setor == [^,)]+', '', content)
    
    # Remover filtros por id_departamento em TipoTeste (não existe)
    content = re.sub(r'TipoTeste\.id_departamento == [^,)]+,?\s*', '', content)
    content = re.sub(r',\s*TipoTeste\.id_departamento == [^,)]+', '', content)
    
    # Remover referências a campos inexistentes em dicionários
    content = re.sub(r'"id_setor": tipo\.id_setor,?\s*', '', content)
    content = re.sub(r'"id_departamento": tipo\.id_departamento,?\s*', '', content)
    
    # Remover filtros por id_setor em TipoFalha (não existe)
    content = re.sub(r'TipoFalha\.id_setor == [^,)]+,?\s*', '', content)
    content = re.sub(r',\s*TipoFalha\.id_setor == [^,)]+', '', content)
    
    # Remover referências a campos inexistentes em TipoFalha
    content = re.sub(r'"id_setor": falha\.id_setor,?\s*', '', content)
    content = re.sub(r'"id_departamento": falha\.id_departamento,?\s*', '', content)
    
    # Remover filtros por id_setor em DescricaoAtividade (não existe)
    content = re.sub(r'DescricaoAtividade\.id_setor == [^,)]+,?\s*', '', content)
    content = re.sub(r',\s*DescricaoAtividade\.id_setor == [^,)]+', '', content)
    
    # Remover referências a campos inexistentes em DescricaoAtividade
    content = re.sub(r'"id_setor": descricao\.id_setor,?\s*', '', content)
    content = re.sub(r'"id_departamento": desc\.id_departamento,?\s*', '', content)
    
    # Corrigir linhas com vírgulas duplas
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r'{\s*,', '{', content)
    content = re.sub(r',\s*}', '}', content)
    
    # Verificar se houve mudanças
    if content != original_content:
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Arquivo corrigido: {file_path}")
        return True
    else:
        print(f"ℹ️ Nenhuma correção necessária: {file_path}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando correção de campos inexistentes...")
    
    # Arquivo para corrigir
    file_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\routes\catalogs_validated.py"
    
    if os.path.exists(file_path):
        fix_catalogs_file(file_path)
    else:
        print(f"❌ Arquivo não encontrado: {file_path}")
    
    print(f"\n🎉 Correção concluída!")
    print("⚠️ Reinicie o servidor para aplicar as mudanças.")

if __name__ == "__main__":
    main()
