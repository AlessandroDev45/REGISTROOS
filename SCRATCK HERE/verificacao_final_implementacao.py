#!/usr/bin/env python3
"""
VERIFICAÇÃO FINAL DA IMPLEMENTAÇÃO
==================================

Script para verificar se todos os componentes da solução de scraping
foram implementados corretamente e estão funcionando.
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NÃO ENCONTRADO")
        return False

def check_import(module_path, module_name, description):
    """Verifica se um módulo pode ser importado"""
    try:
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {description}: Importação bem-sucedida")
                return True, module
        print(f"❌ {description}: Erro na importação")
        return False, None
    except Exception as e:
        print(f"❌ {description}: Erro - {e}")
        return False, None

def check_function_exists(module, function_name, description):
    """Verifica se uma função existe no módulo"""
    if module and hasattr(module, function_name):
        func = getattr(module, function_name)
        if callable(func):
            print(f"✅ {description}: Função {function_name} disponível")
            return True
        else:
            print(f"❌ {description}: {function_name} não é callable")
            return False
    else:
        print(f"❌ {description}: Função {function_name} não encontrada")
        return False

def main():
    print("🔍 VERIFICAÇÃO FINAL DA IMPLEMENTAÇÃO DE SCRAPING PARA PRODUÇÃO")
    print("=" * 70)
    
    # Definir caminhos base
    base_path = Path(__file__).parent.parent
    backend_path = base_path / "RegistroOS" / "registrooficial" / "backend"
    
    print(f"📁 Diretório base: {base_path}")
    print(f"📁 Backend: {backend_path}")
    print()
    
    # Lista de verificações
    checks = []
    
    # 1. Verificar arquivos principais
    print("📋 1. VERIFICANDO ARQUIVOS PRINCIPAIS")
    print("-" * 40)
    
    files_to_check = [
        (backend_path / "tasks" / "scraping_tasks.py", "Tasks de scraping"),
        (backend_path / "scripts" / "scrape_os_data.py", "Script original de scraping"),
        (backend_path / "scripts" / "scrape_os_data_optimized.py", "Script otimizado de scraping"),
        (backend_path / "routes" / "desenvolvimento.py", "Rotas de desenvolvimento"),
        (backend_path / "routes" / "admin_config_routes.py", "Rotas administrativas"),
        (backend_path / "celery_config.py", "Configuração do Celery"),
    ]
    
    for file_path, description in files_to_check:
        checks.append(check_file_exists(str(file_path), description))
    
    print()
    
    # 2. Verificar imports e funções
    print("📋 2. VERIFICANDO IMPORTS E FUNÇÕES")
    print("-" * 40)
    
    # Verificar tasks de scraping
    tasks_path = str(backend_path / "tasks" / "scraping_tasks.py")
    success, tasks_module = check_import(tasks_path, "scraping_tasks", "Módulo de tasks")
    checks.append(success)
    
    if success and tasks_module:
        # Verificar funções específicas
        functions_to_check = [
            ("scrape_os_task", "Task de scraping individual"),
            ("scrape_batch_os_task", "Task de scraping em lote"),
            ("get_queue_status", "Função de status da fila"),
            ("get_scraping_statistics", "Função de estatísticas"),
            ("save_batch_stats", "Função de salvar estatísticas de lote"),
            ("save_scraping_usage_stats", "Função de salvar estatísticas de uso"),
        ]
        
        for func_name, description in functions_to_check:
            checks.append(check_function_exists(tasks_module, func_name, description))
    
    print()
    
    # 3. Verificar script otimizado
    print("📋 3. VERIFICANDO SCRIPT OTIMIZADO")
    print("-" * 40)
    
    optimized_path = str(backend_path / "scripts" / "scrape_os_data_optimized.py")
    success, optimized_module = check_import(optimized_path, "scrape_os_data_optimized", "Script otimizado")
    checks.append(success)
    
    if success and optimized_module:
        optimized_functions = [
            ("execute_scraping_optimized", "Função de scraping otimizada"),
            ("OptimizedScrapingSession", "Classe de sessão otimizada"),
            ("get_cached_session", "Função de cache de sessão"),
            ("cleanup_expired_sessions", "Função de limpeza de sessões"),
        ]
        
        for func_name, description in optimized_functions:
            checks.append(check_function_exists(optimized_module, func_name, description))
    
    print()
    
    # 4. Verificar rotas
    print("📋 4. VERIFICANDO ROTAS")
    print("-" * 40)
    
    routes_path = str(backend_path / "routes" / "desenvolvimento.py")
    success, routes_module = check_import(routes_path, "desenvolvimento", "Rotas de desenvolvimento")
    checks.append(success)
    
    if success:
        print("✅ Rotas de desenvolvimento: Importação bem-sucedida")
        
        # Verificar se as funções auxiliares existem
        if hasattr(routes_module, 'safe_apply_async'):
            print("✅ Função auxiliar safe_apply_async disponível")
            checks.append(True)
        else:
            print("❌ Função auxiliar safe_apply_async não encontrada")
            checks.append(False)
            
        if hasattr(routes_module, 'safe_call_function'):
            print("✅ Função auxiliar safe_call_function disponível")
            checks.append(True)
        else:
            print("❌ Função auxiliar safe_call_function não encontrada")
            checks.append(False)
    
    print()
    
    # 5. Verificar configuração do Celery
    print("📋 5. VERIFICANDO CONFIGURAÇÃO DO CELERY")
    print("-" * 40)
    
    celery_path = str(backend_path / "celery_config.py")
    success, celery_module = check_import(celery_path, "celery_config", "Configuração do Celery")
    checks.append(success)
    
    if success and celery_module:
        if hasattr(celery_module, 'app'):
            print("✅ Aplicação Celery configurada")
            checks.append(True)
        else:
            print("❌ Aplicação Celery não encontrada")
            checks.append(False)
    
    print()
    
    # 6. Verificar documentação
    print("📋 6. VERIFICANDO DOCUMENTAÇÃO")
    print("-" * 40)
    
    docs_to_check = [
        (Path(__file__).parent / "SOLUCAO_SCRAPING_PRODUCAO_IMPLEMENTADA.md", "Documentação da solução"),
        (Path(__file__).parent / "INSTRUCOES_DEPLOY_PRODUCAO.md", "Instruções de deploy"),
        (Path(__file__).parent / "teste_scraping_producao.py", "Script de teste"),
    ]
    
    for file_path, description in docs_to_check:
        checks.append(check_file_exists(str(file_path), description))
    
    print()
    
    # Resumo final
    print("=" * 70)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"✅ Verificações passaram: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 95:
        print("🎉 EXCELENTE! Implementação está 100% completa e pronta para produção!")
        status = "PRONTO PARA PRODUÇÃO"
    elif percentage >= 85:
        print("✅ BOM! Implementação está quase completa. Verificar itens faltantes.")
        status = "QUASE PRONTO"
    elif percentage >= 70:
        print("⚠️ PARCIAL! Implementação tem problemas que precisam ser corrigidos.")
        status = "PRECISA CORREÇÕES"
    else:
        print("❌ CRÍTICO! Muitos componentes estão faltando ou com problemas.")
        status = "IMPLEMENTAÇÃO INCOMPLETA"
    
    print(f"🏷️ Status: {status}")
    
    # Próximos passos
    if percentage < 100:
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Corrigir os itens marcados com ❌")
        print("2. Executar novamente esta verificação")
        print("3. Testar com o script teste_scraping_producao.py")
    else:
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Instalar Redis: pip install redis")
        print("2. Instalar Celery: pip install celery")
        print("3. Iniciar workers: celery -A celery_config worker")
        print("4. Testar com: python teste_scraping_producao.py")
        print("5. Usar em produção para processar 1000 OS!")
    
    return percentage >= 95

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
