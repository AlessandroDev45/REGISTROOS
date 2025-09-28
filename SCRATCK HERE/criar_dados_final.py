#!/usr/bin/env python3
"""
Script final para criar dados baseado na estrutura real das tabelas
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def verificar_colunas(cursor, tabela):
    """Verificar colunas de uma tabela"""
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = cursor.fetchall()
    return [col[1] for col in colunas]  # Retorna apenas os nomes das colunas

def criar_dados_final():
    """Criar dados baseado na estrutura real"""
    print("🚀 CRIANDO DADOS BASEADO NA ESTRUTURA REAL")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estruturas
        print("🔍 Verificando estruturas das tabelas...")
        
        apontamentos_cols = verificar_colunas(cursor, 'apontamentos_detalhados')
        pendencias_cols = verificar_colunas(cursor, 'pendencias')
        programacoes_cols = verificar_colunas(cursor, 'programacoes')
        
        print(f"   📋 Apontamentos: {len(apontamentos_cols)} colunas")
        print(f"   ⚠️ Pendências: {len(pendencias_cols)} colunas")
        print(f"   📅 Programações: {len(programacoes_cols)} colunas")
        
        # Buscar dados base
        cursor.execute("SELECT id, os_numero FROM ordens_servico LIMIT 15")
        oss = cursor.fetchall()
        
        cursor.execute("SELECT id, nome_completo, setor FROM tipo_usuarios WHERE is_approved = 1 LIMIT 10")
        usuarios = cursor.fetchall()
        
        cursor.execute("SELECT id, nome FROM tipo_setores WHERE ativo = 1 LIMIT 10")
        setores = cursor.fetchall()
        
        print(f"   📊 OSs disponíveis: {len(oss)}")
        print(f"   👥 Usuários disponíveis: {len(usuarios)}")
        print(f"   🏭 Setores disponíveis: {len(setores)}")
        
        # 1. Criar apontamentos
        print("\n📝 Criando Apontamentos...")
        apontamentos_criados = 0
        
        for i, (os_id, os_numero) in enumerate(oss):
            if i >= 15:
                break
                
            usuario = random.choice(usuarios)
            data_base = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Dados mínimos para apontamento
            dados = {
                'id_ordem_servico': os_id,
                'data_inicio': data_base.strftime("%Y-%m-%d"),
                'hora_inicio': "08:00",
                'data_fim': data_base.strftime("%Y-%m-%d"),
                'hora_fim': "17:00",
                'observacao': f"Apontamento {i+1} - Produção",
                'setor': usuario[2],
                'usuario_id': usuario[0],
                'status_apontamento': "FINALIZADO"
            }
            
            # Adicionar colunas opcionais se existirem
            if 'cliente' in apontamentos_cols:
                dados['cliente'] = f"Cliente {i+1}"
            if 'equipamento' in apontamentos_cols:
                dados['equipamento'] = f"Equipamento {i+1}"
            if 'tipo_maquina' in apontamentos_cols:
                dados['tipo_maquina'] = "PRODUCAO"
            
            try:
                colunas = ', '.join(dados.keys())
                valores = ', '.join(['?' for _ in dados])
                
                cursor.execute(f"""
                    INSERT INTO apontamentos_detalhados ({colunas})
                    VALUES ({valores})
                """, list(dados.values()))
                
                apontamentos_criados += 1
                if i < 3:
                    print(f"   ✅ Apontamento {i+1} criado - OS {os_numero}")
                    
            except Exception as e:
                if i < 3:
                    print(f"   ❌ Erro no apontamento {i+1}: {e}")
        
        print(f"   📊 Total de apontamentos criados: {apontamentos_criados}")
        
        # 2. Criar pendências
        print("\n⚠️ Criando Pendências...")
        pendencias_criadas = 0
        
        for i in range(15):
            numero_os = str(30000 + i)
            usuario = random.choice(usuarios)
            data_base = datetime.now() - timedelta(days=random.randint(1, 15))
            
            # Dados mínimos para pendência
            dados = {
                'numero_os': numero_os,
                'descricao_pendencia': f"Pendência {i+1} - Material em falta",
                'prioridade': random.choice(["BAIXA", "MEDIA", "ALTA"]),
                'status': random.choice(["ABERTA", "ABERTA", "FECHADA"]),
                'setor_origem': usuario[2]
            }
            
            # Adicionar colunas obrigatórias se existirem
            if 'cliente' in pendencias_cols:
                dados['cliente'] = f"Cliente {i+1}"
            if 'tipo_maquina' in pendencias_cols:
                dados['tipo_maquina'] = "PRODUCAO"
            if 'descricao_maquina' in pendencias_cols:
                dados['descricao_maquina'] = f"Equipamento {i+1}"
            if 'data_criacao' in pendencias_cols:
                dados['data_criacao'] = data_base.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                colunas = ', '.join(dados.keys())
                valores = ', '.join(['?' for _ in dados])
                
                cursor.execute(f"""
                    INSERT INTO pendencias ({colunas})
                    VALUES ({valores})
                """, list(dados.values()))
                
                pendencias_criadas += 1
                if i < 3:
                    print(f"   ✅ Pendência {i+1} criada - OS {numero_os}")
                    
            except Exception as e:
                if i < 3:
                    print(f"   ❌ Erro na pendência {i+1}: {e}")
        
        print(f"   📊 Total de pendências criadas: {pendencias_criadas}")
        
        # 3. Criar programações
        print("\n📅 Criando Programações...")
        programacoes_criadas = 0
        
        for i, (os_id, os_numero) in enumerate(oss):
            if i >= 15:
                break
                
            usuario = random.choice(usuarios)
            setor = random.choice(setores)
            data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
            data_fim = data_inicio + timedelta(hours=random.randint(4, 16))
            
            # Dados mínimos para programação
            dados = {
                'id_ordem_servico': os_id,
                'inicio_previsto': data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                'fim_previsto': data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                'id_setor': setor[0],
                'responsavel_id': usuario[0],
                'observacoes': f"Programação {i+1} - {setor[1]}",
                'prioridade': random.choice(["BAIXA", "MEDIA", "ALTA"]),
                'status': random.choice(["PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA"])
            }
            
            # Adicionar colunas opcionais se existirem
            if 'data_criacao' in programacoes_cols:
                dados['data_criacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                colunas = ', '.join(dados.keys())
                valores = ', '.join(['?' for _ in dados])
                
                cursor.execute(f"""
                    INSERT INTO programacoes ({colunas})
                    VALUES ({valores})
                """, list(dados.values()))
                
                programacoes_criadas += 1
                if i < 3:
                    print(f"   ✅ Programação {i+1} criada - OS {os_numero}")
                    
            except Exception as e:
                if i < 3:
                    print(f"   ❌ Erro na programação {i+1}: {e}")
        
        print(f"   📊 Total de programações criadas: {programacoes_criadas}")
        
        # Commit das mudanças
        conn.commit()
        conn.close()
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL:")
        print(f"   ✅ Apontamentos criados: {apontamentos_criados}/15")
        print(f"   ✅ Pendências criadas: {pendencias_criadas}/15")
        print(f"   ✅ Programações criadas: {programacoes_criadas}/15")
        
        total = apontamentos_criados + pendencias_criadas + programacoes_criadas
        print(f"\n🎉 Total de registros criados: {total}/45")
        
        if total >= 30:
            print("✅ DADOS CRIADOS COM SUCESSO!")
            print("\n💡 Agora você pode:")
            print("1. Acessar o dashboard para ver os dados")
            print("2. Verificar os gráficos atualizados com dados reais")
            print("3. Testar as funcionalidades com setores de produção")
            print("4. Ver o gráfico de pizza dos setores funcionando")
        else:
            print("⚠️ Alguns dados não foram criados. Mas o suficiente para testar!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    criar_dados_final()
