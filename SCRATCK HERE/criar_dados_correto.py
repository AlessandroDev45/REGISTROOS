#!/usr/bin/env python3
"""
Script final para criar dados com a estrutura correta das tabelas
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def criar_dados_correto():
    """Criar dados com a estrutura correta"""
    print("🚀 CRIANDO DADOS COM ESTRUTURA CORRETA")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar dados base
        cursor.execute("SELECT id, os_numero FROM ordens_servico LIMIT 15")
        oss = cursor.fetchall()
        
        cursor.execute("SELECT id, nome_completo, setor, id_setor FROM tipo_usuarios WHERE is_approved = 1 LIMIT 10")
        usuarios = cursor.fetchall()
        
        cursor.execute("SELECT id, nome FROM tipo_setores WHERE ativo = 1 LIMIT 10")
        setores = cursor.fetchall()
        
        print(f"📊 OSs disponíveis: {len(oss)}")
        print(f"👥 Usuários disponíveis: {len(usuarios)}")
        print(f"🏭 Setores disponíveis: {len(setores)}")
        
        # 1. Criar apontamentos
        print("\n📝 Criando Apontamentos...")
        apontamentos_criados = 0
        
        for i, (os_id, os_numero) in enumerate(oss):
            if i >= 15:
                break
                
            usuario = random.choice(usuarios)
            data_base = datetime.now() - timedelta(days=random.randint(1, 30))
            data_inicio = data_base.replace(hour=8, minute=0, second=0)
            data_fim = data_inicio + timedelta(hours=random.randint(4, 8))
            
            try:
                cursor.execute("""
                    INSERT INTO apontamentos_detalhados (
                        id_os, id_usuario, id_setor, data_hora_inicio, data_hora_fim,
                        status_apontamento, foi_retrabalho, observacao_os, setor,
                        tipo_maquina, tipo_atividade, descricao_atividade,
                        etapa_inicial, etapa_final, aprovado_supervisor
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    os_id, usuario[0], usuario[3],
                    data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                    data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                    "FINALIZADO", False,
                    f"Apontamento {i+1} - Produção realizada",
                    usuario[2], "PRODUCAO", "MANUTENCAO",
                    f"Atividade de produção {i+1}",
                    True, True, random.choice([True, False])
                ))
                
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
            
            try:
                cursor.execute("""
                    INSERT INTO pendencias (
                        numero_os, cliente, data_inicio, id_responsavel_inicio,
                        tipo_maquina, descricao_maquina, descricao_pendencia,
                        status, prioridade, setor_origem, departamento_origem
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    numero_os, f"Cliente {i+1}",
                    data_base.strftime("%Y-%m-%d %H:%M:%S"),
                    usuario[0], "PRODUCAO",
                    f"Equipamento {i+1}",
                    f"Pendência {i+1} - {random.choice(['Material em falta', 'Equipamento com defeito', 'Documentação pendente'])}",
                    random.choice(["ABERTA", "ABERTA", "FECHADA"]),
                    random.choice(["BAIXA", "MEDIA", "ALTA"]),
                    usuario[2], "PRODUCAO"
                ))
                
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
            
            try:
                cursor.execute("""
                    INSERT INTO programacoes (
                        id_ordem_servico, criado_por_id, responsavel_id,
                        inicio_previsto, fim_previsto, id_setor,
                        observacoes, status, prioridade,
                        setor_origem, departamento_origem, cliente_nome
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    os_id, usuario[0], usuario[0],
                    data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                    data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                    setor[0],
                    f"Programação {i+1} - {setor[1]}",
                    random.choice(["PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA"]),
                    random.choice(["BAIXA", "MEDIA", "ALTA"]),
                    usuario[2], "PRODUCAO", f"Cliente {i+1}"
                ))
                
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
            print("1. 🌐 Acessar o dashboard para ver os dados")
            print("2. 📊 Verificar os gráficos atualizados com dados reais")
            print("3. 🏭 Ver o gráfico de pizza dos setores funcionando")
            print("4. 📋 Testar as funcionalidades com setores de produção")
            print("5. 🔄 Ver a atualização automática do dashboard")
        else:
            print("⚠️ Alguns dados não foram criados, mas já há dados suficientes para testar!")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print("1. Acesse o dashboard no navegador")
        print("2. Verifique se os gráficos estão mostrando os dados")
        print("3. Teste a navegação entre as abas")
        print("4. Verifique se o gráfico de pizza dos setores está funcionando")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    criar_dados_correto()
