#!/usr/bin/env python3
"""
ADICIONAR RESULTADOS DE TESTES
==============================

Adiciona resultados de testes aos apontamentos criados
usando a estrutura correta da tabela resultados_teste
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

def conectar_banco():
    """Conecta ao banco de dados"""
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"

    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return None

    return sqlite3.connect(db_path)

def obter_apontamentos_teste():
    """Obtém apontamentos de teste criados"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        # Buscar apontamentos das OSs de teste
        cursor.execute("""
            SELECT a.id 
            FROM apontamentos_detalhados a
            JOIN ordens_servico o ON a.id_os = o.id
            WHERE o.os_numero LIKE 'REAL2025%'
            ORDER BY a.id
        """)
        
        apontamentos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return apontamentos
        
    except Exception as e:
        print(f"❌ Erro ao obter apontamentos: {e}")
        conn.close()
        return []

def obter_tipos_teste():
    """Obtém tipos de teste disponíveis"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, nome FROM tipos_teste WHERE ativo = 1 LIMIT 10")
        tipos_teste = cursor.fetchall()
        conn.close()
        return tipos_teste
        
    except Exception as e:
        print(f"❌ Erro ao obter tipos de teste: {e}")
        conn.close()
        return []

def criar_resultados_testes(apontamentos, tipos_teste, quantidade=15):
    """Cria resultados de testes com estrutura correta"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    resultados_criados = []
    
    print(f"🧪 Criando {quantidade} Resultados de Testes...")
    
    resultados_validos = ['APROVADO', 'REPROVADO', 'CONDICIONAL', 'PENDENTE']
    
    for i in range(min(quantidade, len(apontamentos))):
        try:
            apontamento_id = apontamentos[i]
            tipo_teste = random.choice(tipos_teste)
            
            resultado = random.choice(resultados_validos)
            
            observacoes_teste = [
                f"Teste {tipo_teste[1]} executado conforme norma técnica NBR",
                f"Equipamento calibrado - Certificado de calibração válido",
                f"Condições ambientais controladas: 23°C ± 2°C, 65% UR",
                f"Teste realizado por técnico qualificado e certificado",
                f"Resultado {'dentro' if resultado == 'APROVADO' else 'fora'} dos parâmetros especificados",
                f"Medição realizada com equipamento padrão rastreável",
                f"Procedimento seguido conforme manual de qualidade",
                f"Teste {'aprovado' if resultado == 'APROVADO' else 'necessita revisão'} pelo controle de qualidade",
                f"Inspeção visual: {'Conforme' if resultado == 'APROVADO' else 'Não conforme'}",
                f"Documentação técnica: {'Completa' if resultado == 'APROVADO' else 'Pendente'}"
            ]
            
            cursor.execute("""
                INSERT INTO resultados_teste (
                    id_apontamento, id_teste, resultado, observacao, data_registro
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                apontamento_id,
                tipo_teste[0],  # id
                resultado,
                random.choice(observacoes_teste),
                datetime.now().isoformat()
            ))
            
            resultado_id = cursor.lastrowid
            resultados_criados.append(resultado_id)
            
            print(f"   ✅ {i+1:2d}. ID:{resultado_id} | Apontamento:{apontamento_id} | {tipo_teste[1][:25]} | {resultado}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar resultado {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(resultados_criados)} Resultados de Teste criados!")
    return resultados_criados

def verificar_dados_criados():
    """Verifica os dados criados"""
    conn = conectar_banco()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n📊 VERIFICANDO DADOS CRIADOS:")
    print("=" * 50)
    
    try:
        # Contar OSs de teste
        cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE os_numero LIKE 'REAL2025%'")
        count_os = cursor.fetchone()[0]
        print(f"📋 Ordens de Serviço: {count_os}")
        
        # Contar apontamentos de teste
        cursor.execute("""
            SELECT COUNT(*) 
            FROM apontamentos_detalhados a
            JOIN ordens_servico o ON a.id_os = o.id
            WHERE o.os_numero LIKE 'REAL2025%'
        """)
        count_apontamentos = cursor.fetchone()[0]
        print(f"📊 Apontamentos: {count_apontamentos}")
        
        # Contar pendências de teste
        cursor.execute("SELECT COUNT(*) FROM pendencias WHERE numero_os LIKE 'REAL2025%'")
        count_pendencias = cursor.fetchone()[0]
        print(f"⚠️ Pendências: {count_pendencias}")
        
        # Contar programações de teste
        cursor.execute("""
            SELECT COUNT(*) 
            FROM programacoes p
            JOIN ordens_servico o ON p.id_ordem_servico = o.id
            WHERE o.os_numero LIKE 'REAL2025%'
        """)
        count_programacoes = cursor.fetchone()[0]
        print(f"📅 Programações: {count_programacoes}")
        
        # Contar resultados de teste
        cursor.execute("""
            SELECT COUNT(*) 
            FROM resultados_teste r
            JOIN apontamentos_detalhados a ON r.id_apontamento = a.id
            JOIN ordens_servico o ON a.id_os = o.id
            WHERE o.os_numero LIKE 'REAL2025%'
        """)
        count_resultados = cursor.fetchone()[0]
        print(f"🧪 Resultados de Teste: {count_resultados}")
        
        # Mostrar distribuição de status
        print(f"\n📈 DISTRIBUIÇÃO DE STATUS:")
        
        # Status das OSs
        cursor.execute("""
            SELECT status_os, COUNT(*) 
            FROM ordens_servico 
            WHERE os_numero LIKE 'REAL2025%' 
            GROUP BY status_os
        """)
        print("   📋 Ordens de Serviço:")
        for status, count in cursor.fetchall():
            print(f"      {status}: {count}")
        
        # Status das pendências
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM pendencias 
            WHERE numero_os LIKE 'REAL2025%' 
            GROUP BY status
        """)
        print("   ⚠️ Pendências:")
        for status, count in cursor.fetchall():
            print(f"      {status}: {count}")
        
        # Status das programações
        cursor.execute("""
            SELECT p.status, COUNT(*) 
            FROM programacoes p
            JOIN ordens_servico o ON p.id_ordem_servico = o.id
            WHERE o.os_numero LIKE 'REAL2025%' 
            GROUP BY p.status
        """)
        print("   📅 Programações:")
        for status, count in cursor.fetchall():
            print(f"      {status}: {count}")
        
        # Resultados dos testes
        cursor.execute("""
            SELECT r.resultado, COUNT(*) 
            FROM resultados_teste r
            JOIN apontamentos_detalhados a ON r.id_apontamento = a.id
            JOIN ordens_servico o ON a.id_os = o.id
            WHERE o.os_numero LIKE 'REAL2025%' 
            GROUP BY r.resultado
        """)
        print("   🧪 Resultados de Teste:")
        for resultado, count in cursor.fetchall():
            print(f"      {resultado}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        conn.close()

def main():
    """Função principal"""
    print("🧪 ADICIONANDO RESULTADOS DE TESTES")
    print("=" * 50)
    
    # 1. Obter apontamentos de teste
    print("📊 Obtendo apontamentos de teste...")
    apontamentos = obter_apontamentos_teste()
    
    if not apontamentos:
        print("❌ Nenhum apontamento de teste encontrado!")
        print("💡 Execute primeiro o script criar_dados_realistas_corretos.py")
        return
    
    print(f"✅ {len(apontamentos)} apontamentos encontrados")
    
    # 2. Obter tipos de teste
    print("\n🧪 Obtendo tipos de teste...")
    tipos_teste = obter_tipos_teste()
    
    if not tipos_teste:
        print("❌ Nenhum tipo de teste encontrado!")
        return
    
    print(f"✅ {len(tipos_teste)} tipos de teste encontrados")
    
    # 3. Criar resultados de teste
    resultados = criar_resultados_testes(apontamentos, tipos_teste, len(apontamentos))
    
    # 4. Verificar dados criados
    verificar_dados_criados()
    
    print("\n" + "=" * 50)
    print("🎉 RESULTADOS DE TESTES ADICIONADOS!")
    print(f"🧪 {len(resultados)} resultados criados")
    
    print("\n🎯 AGORA VOCÊ TEM DADOS COMPLETOS PARA TESTAR:")
    print("   1. Dashboard com métricas realistas")
    print("   2. Funcionalidades de pendências")
    print("   3. Funcionalidades de programações")
    print("   4. Apontamentos com relacionamentos")
    print("   5. Resultados de testes com observações")
    print("   6. Todas as funcionalidades implementadas")

if __name__ == "__main__":
    main()
