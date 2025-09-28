#!/usr/bin/env python3
"""
Script simplificado para criar dados básicos no banco
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def criar_dados_simples():
    """Criar dados simples diretamente no banco"""
    print("🚀 CRIANDO DADOS SIMPLES NO BANCO")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Criar algumas OSs simples
        print("\n📋 Criando Ordens de Serviço...")
        os_criadas = 0
        for i in range(20):
            numero_os = str(20000 + i)
            try:
                cursor.execute("""
                    INSERT INTO ordens_servico (os_numero, status_os, data_criacao)
                    VALUES (?, ?, ?)
                """, (numero_os, "ATIVA", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                os_criadas += 1
                if i < 5:
                    print(f"   ✅ OS {numero_os} criada")
            except sqlite3.IntegrityError:
                pass  # OS já existe
        
        print(f"   📊 Total de OSs criadas: {os_criadas}")
        
        # 2. Criar apontamentos simples
        print("\n📝 Criando Apontamentos...")
        apontamentos_criados = 0
        
        # Buscar OSs existentes
        cursor.execute("SELECT id, os_numero FROM ordens_servico LIMIT 15")
        oss = cursor.fetchall()
        
        # Buscar usuários
        cursor.execute("SELECT id, nome_completo, setor FROM tipo_usuarios WHERE is_approved = 1 LIMIT 10")
        usuarios = cursor.fetchall()
        
        for i, (os_id, os_numero) in enumerate(oss):
            if i >= 15:
                break
                
            usuario = random.choice(usuarios)
            data_base = datetime.now() - timedelta(days=random.randint(1, 30))
            
            try:
                cursor.execute("""
                    INSERT INTO apontamentos_detalhados (
                        numero_os, id_ordem_servico, data_inicio, hora_inicio,
                        data_fim, hora_fim, observacao, setor, usuario_id,
                        data_criacao, status_apontamento
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    os_numero, os_id,
                    data_base.strftime("%Y-%m-%d"), "08:00",
                    data_base.strftime("%Y-%m-%d"), "17:00",
                    f"Apontamento {i+1} - Produção",
                    usuario[2], usuario[0],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "FINALIZADO"
                ))
                apontamentos_criados += 1
                if i < 5:
                    print(f"   ✅ Apontamento {i+1} criado - OS {os_numero}")
            except Exception as e:
                print(f"   ❌ Erro no apontamento {i+1}: {e}")
        
        print(f"   📊 Total de apontamentos criados: {apontamentos_criados}")
        
        # 3. Criar pendências simples
        print("\n⚠️ Criando Pendências...")
        pendencias_criadas = 0
        
        for i in range(15):
            numero_os = str(30000 + i)
            usuario = random.choice(usuarios)
            data_base = datetime.now() - timedelta(days=random.randint(1, 15))
            
            try:
                cursor.execute("""
                    INSERT INTO pendencias (
                        numero_os, descricao_pendencia, prioridade, status,
                        setor_origem, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    numero_os,
                    f"Pendência {i+1} - Material em falta",
                    random.choice(["BAIXA", "MEDIA", "ALTA"]),
                    random.choice(["ABERTA", "ABERTA", "FECHADA"]),
                    usuario[2],
                    data_base.strftime("%Y-%m-%d %H:%M:%S")
                ))
                pendencias_criadas += 1
                if i < 5:
                    print(f"   ✅ Pendência {i+1} criada - OS {numero_os}")
            except Exception as e:
                print(f"   ❌ Erro na pendência {i+1}: {e}")
        
        print(f"   📊 Total de pendências criadas: {pendencias_criadas}")
        
        # 4. Criar programações simples
        print("\n📅 Criando Programações...")
        programacoes_criadas = 0
        
        # Buscar setores
        cursor.execute("SELECT id, nome FROM tipo_setores WHERE ativo = 1 LIMIT 10")
        setores = cursor.fetchall()
        
        for i, (os_id, os_numero) in enumerate(oss):
            if i >= 15:
                break
                
            usuario = random.choice(usuarios)
            setor = random.choice(setores)
            data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
            data_fim = data_inicio + timedelta(hours=random.randint(4, 16))
            
            try:
                cursor.execute("""
                    INSERT INTO programacoes (
                        id_ordem_servico, inicio_previsto, fim_previsto,
                        id_setor, responsavel_id, observacoes, prioridade,
                        status, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    os_id,
                    data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                    data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                    setor[0], usuario[0],
                    f"Programação {i+1} - {setor[1]}",
                    random.choice(["BAIXA", "MEDIA", "ALTA"]),
                    random.choice(["PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA"]),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                programacoes_criadas += 1
                if i < 5:
                    print(f"   ✅ Programação {i+1} criada - OS {os_numero}")
            except Exception as e:
                print(f"   ❌ Erro na programação {i+1}: {e}")
        
        print(f"   📊 Total de programações criadas: {programacoes_criadas}")
        
        # Commit das mudanças
        conn.commit()
        conn.close()
        
        # Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO FINAL:")
        print(f"   ✅ OSs criadas: {os_criadas}")
        print(f"   ✅ Apontamentos criados: {apontamentos_criados}/15")
        print(f"   ✅ Pendências criadas: {pendencias_criadas}/15")
        print(f"   ✅ Programações criadas: {programacoes_criadas}/15")
        
        total = apontamentos_criados + pendencias_criadas + programacoes_criadas
        print(f"\n🎉 Total de registros criados: {total}")
        
        if total >= 30:
            print("✅ DADOS CRIADOS COM SUCESSO!")
            print("\n💡 Agora você pode:")
            print("1. Acessar o dashboard para ver os dados")
            print("2. Verificar os gráficos atualizados")
            print("3. Testar as funcionalidades com dados reais")
        else:
            print("⚠️ Alguns dados não foram criados. Verifique os logs acima.")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    criar_dados_simples()
