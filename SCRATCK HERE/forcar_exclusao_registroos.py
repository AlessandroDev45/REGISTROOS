#!/usr/bin/env python3
"""
Script para forçar a exclusão do arquivo registroos.db
"""

import sys
import os
import time
import shutil

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')

def forcar_exclusao():
    """Força a exclusão do arquivo registroos.db"""
    try:
        print("🗑️ Forçando exclusão do arquivo registroos.db...")
        
        arquivo_origem = os.path.join(backend_path, 'registroos.db')
        
        print(f"  📂 Arquivo: {arquivo_origem}")
        
        if not os.path.exists(arquivo_origem):
            print(f"  ✅ Arquivo já não existe")
            return True
        
        # Fazer backup final
        backup_final = arquivo_origem + f'.backup_final_{int(time.time())}'
        try:
            shutil.copy2(arquivo_origem, backup_final)
            print(f"  💾 Backup final criado: {os.path.basename(backup_final)}")
        except Exception as e:
            print(f"  ⚠️ Erro ao criar backup: {e}")
        
        # Tentar várias abordagens para apagar
        tentativas = [
            lambda: os.remove(arquivo_origem),
            lambda: os.unlink(arquivo_origem),
            lambda: shutil.rmtree(arquivo_origem, ignore_errors=True) if os.path.isdir(arquivo_origem) else os.remove(arquivo_origem)
        ]
        
        for i, tentativa in enumerate(tentativas, 1):
            try:
                print(f"  🔄 Tentativa {i}...")
                tentativa()
                
                # Verificar se foi apagado
                if not os.path.exists(arquivo_origem):
                    print(f"  ✅ Arquivo apagado com sucesso!")
                    return True
                else:
                    print(f"  ⚠️ Arquivo ainda existe após tentativa {i}")
                    
            except Exception as e:
                print(f"  ❌ Tentativa {i} falhou: {e}")
                time.sleep(1)  # Aguardar um pouco antes da próxima tentativa
        
        # Se chegou aqui, não conseguiu apagar
        print(f"  ❌ Não foi possível apagar o arquivo")
        print(f"  ℹ️ O arquivo pode estar sendo usado por outro processo")
        print(f"  ℹ️ Tente fechar todos os programas Python e executar novamente")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def verificar_resultado():
    """Verifica se o arquivo foi apagado"""
    try:
        arquivo_origem = os.path.join(backend_path, 'registroos.db')
        
        if os.path.exists(arquivo_origem):
            print(f"  ❌ Arquivo ainda existe: {arquivo_origem}")
            
            # Mostrar informações do arquivo
            try:
                stat = os.stat(arquivo_origem)
                print(f"    📊 Tamanho: {stat.st_size} bytes")
                print(f"    📅 Modificado: {time.ctime(stat.st_mtime)}")
            except:
                pass
            
            return False
        else:
            print(f"  ✅ Arquivo não existe mais: {arquivo_origem}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
        return False

def main():
    print("🗑️ Forçando exclusão do arquivo registroos.db...")
    print("=" * 50)
    
    # 1. Tentar apagar
    sucesso = forcar_exclusao()
    
    # 2. Verificar resultado
    print(f"\n🔍 Verificando resultado...")
    verificado = verificar_resultado()
    
    print(f"\n🎯 Resultado final:")
    if sucesso and verificado:
        print(f"✅ Arquivo apagado com sucesso!")
        print(f"📂 Agora o servidor usará apenas registroos_new.db")
    elif not verificado:
        print(f"❌ Arquivo ainda existe")
        print(f"💡 Sugestões:")
        print(f"  1. Feche todos os programas Python")
        print(f"  2. Feche o VS Code se estiver aberto")
        print(f"  3. Reinicie o computador se necessário")
        print(f"  4. Apague manualmente pelo Windows Explorer")
    else:
        print(f"⚠️ Status incerto - verifique manualmente")
    
    return sucesso and verificado

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
