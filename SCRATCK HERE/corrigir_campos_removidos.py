#!/usr/bin/env python3
"""
Script para corrigir todas as referências aos campos removidos (setor, departamento)
nos arquivos Python do backend.
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

def fix_file(file_path):
    """Corrige um arquivo específico"""
    print(f"\n🔧 Corrigindo: {file_path}")
    
    # Criar backup
    backup_file(file_path)
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Substituições para campos de usuário
    content = re.sub(r'\.setor(?!\w)', '.id_setor', content)
    content = re.sub(r'\.departamento(?!\w)', '.id_departamento', content)
    
    # Substituições para strings em dicionários/JSON
    content = re.sub(r'"setor":\s*(\w+)\.setor', '"id_setor": \\1.id_setor', content)
    content = re.sub(r'"departamento":\s*(\w+)\.departamento', '"id_departamento": \\1.id_departamento', content)

    # Substituições específicas para chaves de dicionário
    content = re.sub(r'"setor":\s*(\w+)\.id_setor', '"id_setor": \\1.id_setor', content)
    content = re.sub(r'"departamento":\s*(\w+)\.id_departamento', '"id_departamento": \\1.id_departamento', content)
    
    # Substituições específicas para queries SQL
    content = re.sub(r'SELECT.*setor.*departamento.*FROM tipo_usuarios', 
                    'SELECT id, nome_completo, id_setor, id_departamento, privilege_level FROM tipo_usuarios', content)
    
    # Substituições para filtros
    content = re.sub(r'\.filter\(.*\.setor\s*==', '.filter(Setor.id_setor ==', content)
    content = re.sub(r'\.filter\(.*\.departamento\s*==', '.filter(Departamento.id_departamento ==', content)
    
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
    print("🚀 Iniciando correção de campos removidos...")
    
    # Diretório base do backend
    backend_dir = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
    
    # Arquivos para corrigir
    files_to_fix = [
        "routes/auth.py",
        "routes/users.py", 
        "routes/catalogs_validated.py",
        "app/admin_routes_simple.py",
        "app/dependencies.py",
        "routes/pcp_routes.py",
        "app/gestao_routes.py",
        "routes/os_routes_simple.py"
    ]
    
    fixed_count = 0
    
    for file_rel_path in files_to_fix:
        file_path = os.path.join(backend_dir, file_rel_path)
        if os.path.exists(file_path):
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    print(f"\n🎉 Correção concluída! {fixed_count} arquivos foram modificados.")
    print("⚠️ Reinicie o servidor para aplicar as mudanças.")

if __name__ == "__main__":
    main()
