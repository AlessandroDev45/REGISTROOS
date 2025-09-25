#!/usr/bin/env python3
"""
🔧 CRIAR: Apontamentos de exemplo
Cria alguns apontamentos de exemplo para testar o Dashboard
"""

import sqlite3
import os
from datetime import datetime, timedelta

def criar_apontamentos_exemplo():
    # Caminho para o banco de dados
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    print("🔧 CRIANDO: Apontamentos de exemplo")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Buscar dados existentes para usar nos apontamentos
        print("📋 Buscando dados existentes...")
        
        # Buscar ordens de serviço
        cursor.execute("SELECT id, os_numero FROM ordens_servico LIMIT 5")
        ordens_servico = cursor.fetchall()
        print(f"   Encontradas {len(ordens_servico)} ordens de serviço")
        
        # Buscar usuários
        cursor.execute("SELECT id, nome_completo FROM tipo_usuarios LIMIT 3")
        usuarios = cursor.fetchall()
        print(f"   Encontrados {len(usuarios)} usuários")

        # Buscar setores
        cursor.execute("SELECT id, nome FROM tipo_setores WHERE area_tipo = 'PRODUCAO' LIMIT 5")
        setores = cursor.fetchall()
        print(f"   Encontrados {len(setores)} setores de produção")
        
        if not ordens_servico or not usuarios or not setores:
            print("❌ Dados insuficientes para criar apontamentos")
            return
        
        # 2. Criar apontamentos de exemplo
        print("\n🔧 Criando apontamentos de exemplo...")
        
        apontamentos_exemplo = []
        base_date = datetime.now() - timedelta(days=7)  # Última semana
        
        for i in range(10):  # Criar 10 apontamentos
            os_data = ordens_servico[i % len(ordens_servico)]
            usuario_data = usuarios[i % len(usuarios)]
            setor_data = setores[i % len(setores)]
            
            data_inicio = base_date + timedelta(days=i, hours=8)
            data_fim = data_inicio + timedelta(hours=2 + (i % 4))
            
            apontamento = {
                'id_os': os_data[0],
                'id_usuario': usuario_data[0],
                'id_setor': setor_data[0],  # ID do setor
                'data_hora_inicio': data_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                'data_hora_fim': data_fim.strftime('%Y-%m-%d %H:%M:%S'),
                'status_apontamento': ['EM_ANDAMENTO', 'CONCLUIDO', 'PAUSADO'][i % 3],
                'setor': setor_data[1],  # Nome do setor
                'tipo_atividade': ['MONTAGEM', 'TESTE', 'REPARO', 'INSPEÇÃO'][i % 4],
                'descricao_atividade': f'Atividade de exemplo {i+1}',
                'observacao_os': f'Observação do apontamento {i+1}',
                'foi_retrabalho': i % 4 == 0,  # 25% são retrabalho
                'tipo_maquina': ['MOTOR TRIFASICO', 'MOTOR MONOFASICO', 'TRANSFORMADOR'][i % 3]
            }
            
            apontamentos_exemplo.append(apontamento)
        
        # 3. Inserir apontamentos no banco
        insert_sql = """
            INSERT INTO apontamentos_detalhados (
                id_os, id_usuario, id_setor, data_hora_inicio, data_hora_fim,
                status_apontamento, setor, tipo_atividade,
                descricao_atividade, observacao_os, foi_retrabalho,
                tipo_maquina
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for apt in apontamentos_exemplo:
            cursor.execute(insert_sql, (
                apt['id_os'], apt['id_usuario'], apt['id_setor'],
                apt['data_hora_inicio'], apt['data_hora_fim'],
                apt['status_apontamento'], apt['setor'],
                apt['tipo_atividade'], apt['descricao_atividade'],
                apt['observacao_os'], apt['foi_retrabalho'],
                apt['tipo_maquina']
            ))
        
        conn.commit()
        print(f"✅ Criados {len(apontamentos_exemplo)} apontamentos de exemplo")
        
        # 4. Verificar se foram criados
        cursor.execute("SELECT COUNT(*) FROM apontamentos_detalhados")
        total = cursor.fetchone()[0]
        print(f"📊 Total de apontamentos na tabela: {total}")
        
        # 5. Mostrar alguns exemplos
        cursor.execute("""
            SELECT id, id_os, status_apontamento, setor, tipo_atividade
            FROM apontamentos_detalhados
            ORDER BY id DESC
            LIMIT 5
        """)

        exemplos = cursor.fetchall()
        print(f"\n📋 Últimos {len(exemplos)} apontamentos criados:")
        for apt in exemplos:
            print(f"   ID: {apt[0]} | OS_ID: {apt[1]} | Status: {apt[2]} | Setor: {apt[3]} | Atividade: {apt[4]}")
        
        conn.close()
        print("\n✅ Apontamentos de exemplo criados com sucesso!")
        print("🎯 Agora você pode testar o Dashboard")
        
    except Exception as e:
        print(f"❌ Erro ao criar apontamentos: {e}")

if __name__ == "__main__":
    criar_apontamentos_exemplo()
