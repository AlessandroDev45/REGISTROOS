#!/usr/bin/env python3
"""
Script para testar diretamente a função de categorias sem autenticação
"""

import sys
import os

# Adicionar o diretório do backend ao path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import Session
from config.database_config import get_db
from app.database_models import TipoMaquina, Departamento

def test_categorias_function():
    """Testa a lógica da função de categorias diretamente"""
    
    print("🔍 Testando função de categorias...")
    
    try:
        # Obter sessão do banco
        db_gen = get_db()
        db = next(db_gen)
        
        # Teste 1: Sem filtros
        print("\n1. Teste sem filtros:")
        query = db.query(TipoMaquina.categoria).distinct().filter(
            TipoMaquina.categoria.isnot(None),
            TipoMaquina.categoria != '',
            TipoMaquina.ativo == True
        )
        categorias = [row.categoria for row in query.all() if row.categoria]
        print(f"Categorias encontradas: {categorias}")
        
        # Teste 2: Com filtro de departamento MOTORES
        print("\n2. Teste com departamento=MOTORES:")
        departamento = "MOTORES"
        
        # Buscar o ID do departamento pelo nome
        dept_query = db.query(Departamento.id).filter(Departamento.nome_tipo == departamento).first()
        print(f"Departamento {departamento} encontrado: {dept_query is not None}")
        
        if dept_query:
            print(f"ID do departamento: {dept_query.id}")
            
            query = db.query(TipoMaquina.categoria).distinct().filter(
                TipoMaquina.categoria.isnot(None),
                TipoMaquina.categoria != '',
                TipoMaquina.ativo == True,
                TipoMaquina.id_departamento == dept_query.id
            )
            categorias = [row.categoria for row in query.all() if row.categoria]
            print(f"Categorias filtradas por departamento: {categorias}")
            
            # Se não encontrou, usar fallback
            if not categorias:
                print("Nenhuma categoria encontrada, usando fallback...")
                query_all = db.query(TipoMaquina.categoria).distinct().filter(
                    TipoMaquina.categoria.isnot(None),
                    TipoMaquina.categoria != '',
                    TipoMaquina.ativo == True
                )
                categorias = [row.categoria for row in query_all.all() if row.categoria]
                print(f"Categorias fallback: {categorias}")
        
        # Teste 3: Verificar tipos de máquina por departamento
        print("\n3. Verificando tipos de máquina por departamento:")
        for dept in db.query(Departamento).all():
            tipos_count = db.query(TipoMaquina).filter(
                TipoMaquina.id_departamento == dept.id,
                TipoMaquina.ativo == True
            ).count()
            print(f"  {dept.nome_tipo} (ID: {dept.id}): {tipos_count} tipos de máquina")
        
        # Teste 4: Verificar tipos de máquina sem departamento
        tipos_sem_dept = db.query(TipoMaquina).filter(
            TipoMaquina.id_departamento.is_(None),
            TipoMaquina.ativo == True
        ).count()
        print(f"  Sem departamento: {tipos_sem_dept} tipos de máquina")
        
        db.close()
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_categorias_function()
