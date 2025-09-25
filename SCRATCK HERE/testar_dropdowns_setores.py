#!/usr/bin/env python3
"""
Script para testar se os dropdowns de setores estão funcionando
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/admin"

def test_setores_filtering():
    """Testa se os setores estão sendo filtrados corretamente por departamento"""
    
    print("🔍 TESTANDO FILTRAGEM DE SETORES POR DEPARTAMENTO")
    print("=" * 60)
    
    # 1. Buscar todos os setores
    response = requests.get(f"{BASE_URL}/setores/")
    if response.status_code != 200:
        print(f"❌ Erro ao buscar setores: {response.status_code}")
        return
    
    setores = response.json()
    print(f"✅ Total de setores encontrados: {len(setores)}")
    
    # 2. Agrupar por departamento
    setores_por_dept = {}
    for setor in setores:
        dept = setor.get('departamento', 'SEM_DEPARTAMENTO')
        if dept not in setores_por_dept:
            setores_por_dept[dept] = []
        setores_por_dept[dept].append(setor)
    
    print(f"\n📊 SETORES AGRUPADOS POR DEPARTAMENTO:")
    for dept, setores_dept in setores_por_dept.items():
        print(f"\n🏢 {dept}: {len(setores_dept)} setores")
        for setor in setores_dept[:3]:  # Mostrar apenas os 3 primeiros
            print(f"   - ID: {setor['id']} | Nome: {setor['nome']}")
        if len(setores_dept) > 3:
            print(f"   ... e mais {len(setores_dept) - 3} setores")
    
    # 3. Testar filtragem específica para MOTORES
    print(f"\n🔧 TESTANDO FILTRAGEM PARA MOTORES:")
    setores_motores = [s for s in setores if s.get('departamento') == 'MOTORES']
    print(f"✅ Setores de MOTORES: {len(setores_motores)}")
    for setor in setores_motores[:5]:
        print(f"   - {setor['nome']} (ID: {setor['id']})")
    
    # 4. Testar filtragem específica para TRANSFORMADORES
    print(f"\n⚡ TESTANDO FILTRAGEM PARA TRANSFORMADORES:")
    setores_transformadores = [s for s in setores if s.get('departamento') == 'TRANSFORMADORES']
    print(f"✅ Setores de TRANSFORMADORES: {len(setores_transformadores)}")
    for setor in setores_transformadores[:5]:
        print(f"   - {setor['nome']} (ID: {setor['id']})")
    
    return setores_por_dept

def test_tipos_teste_with_setor():
    """Testa se os tipos de teste estão retornando setor corretamente"""
    
    print(f"\n🧪 TESTANDO TIPOS DE TESTE COM SETOR")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/tipos-teste/")
    if response.status_code != 200:
        print(f"❌ Erro ao buscar tipos de teste: {response.status_code}")
        return
    
    tipos_teste = response.json()
    print(f"✅ Total de tipos de teste: {len(tipos_teste)}")
    
    # Agrupar por setor
    tipos_por_setor = {}
    for tipo in tipos_teste:
        setor = tipo.get('setor', 'SEM_SETOR')
        if setor not in tipos_por_setor:
            tipos_por_setor[setor] = []
        tipos_por_setor[setor].append(tipo)
    
    print(f"\n📊 TIPOS DE TESTE AGRUPADOS POR SETOR:")
    for setor, tipos in tipos_por_setor.items():
        print(f"\n🏭 {setor}: {len(tipos)} tipos")
        for tipo in tipos[:2]:  # Mostrar apenas os 2 primeiros
            print(f"   - {tipo['nome']} (Dept: {tipo.get('departamento', 'N/A')})")

def test_frontend_compatibility():
    """Testa se os dados estão no formato esperado pelo frontend"""
    
    print(f"\n🎯 TESTANDO COMPATIBILIDADE COM FRONTEND")
    print("=" * 60)
    
    # Testar estrutura esperada pelo useCachedSetores
    response = requests.get(f"{BASE_URL}/setores/")
    setores = response.json()
    
    # Verificar se tem os campos esperados
    required_fields = ['id', 'nome', 'departamento', 'ativo']
    
    print("✅ Verificando campos obrigatórios:")
    for field in required_fields:
        has_field = all(field in setor for setor in setores)
        status = "✅" if has_field else "❌"
        print(f"   {status} Campo '{field}': {'Presente' if has_field else 'Ausente'}")
    
    # Testar filtragem como o frontend faz
    print(f"\n🔍 Simulando filtragem do frontend:")
    motores_frontend = [s for s in setores if s.get('departamento') == 'MOTORES' and s.get('ativo')]
    transformadores_frontend = [s for s in setores if s.get('departamento') == 'TRANSFORMADORES' and s.get('ativo')]
    
    print(f"   ✅ Setores MOTORES ativos: {len(motores_frontend)}")
    print(f"   ✅ Setores TRANSFORMADORES ativos: {len(transformadores_frontend)}")
    
    return {
        'motores': motores_frontend,
        'transformadores': transformadores_frontend
    }

def main():
    print("🚀 TESTE COMPLETO DE DROPDOWNS DE SETORES")
    print("=" * 80)
    
    try:
        # Teste 1: Filtragem básica
        setores_por_dept = test_setores_filtering()
        
        # Teste 2: Tipos de teste com setor
        test_tipos_teste_with_setor()
        
        # Teste 3: Compatibilidade frontend
        frontend_data = test_frontend_compatibility()
        
        print(f"\n" + "=" * 80)
        print("✅ RESUMO FINAL:")
        print(f"   🏢 Departamentos encontrados: {len(setores_por_dept) if setores_por_dept else 0}")
        print(f"   🔧 Setores MOTORES: {len(frontend_data['motores']) if frontend_data else 0}")
        print(f"   ⚡ Setores TRANSFORMADORES: {len(frontend_data['transformadores']) if frontend_data else 0}")
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO DURANTE O TESTE: {str(e)}")

if __name__ == "__main__":
    main()
