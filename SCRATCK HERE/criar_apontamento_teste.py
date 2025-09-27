#!/usr/bin/env python3
"""
Criar apontamento de teste para verificar se o dashboard funciona
"""

import sqlite3
from datetime import datetime, timedelta

def criar_apontamento_teste():
    """Criar um apontamento de teste no banco de dados"""
    print("🧪 Criando apontamento de teste...")
    
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar uma OS existente
        cursor.execute("SELECT id FROM ordens_servico LIMIT 1")
        os_result = cursor.fetchone()
        if not os_result:
            print("❌ Nenhuma OS encontrada")
            return
        
        os_id = os_result[0]
        print(f"📋 Usando OS ID: {os_id}")
        
        # Buscar um usuário existente
        cursor.execute("SELECT id FROM tipo_usuarios LIMIT 1")
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ Nenhum usuário encontrado")
            return
            
        user_id = user_result[0]
        print(f"👤 Usando usuário ID: {user_id}")
        
        # Buscar um setor existente
        cursor.execute("SELECT id FROM tipo_setores LIMIT 1")
        setor_result = cursor.fetchone()
        if not setor_result:
            print("❌ Nenhum setor encontrado")
            return
            
        setor_id = setor_result[0]
        print(f"🏢 Usando setor ID: {setor_id}")
        
        # Criar apontamento de teste
        agora = datetime.now()
        inicio = agora - timedelta(hours=2)
        fim = agora
        
        apontamento_data = {
            'id_os': os_id,
            'id_usuario': user_id,
            'id_setor': setor_id,
            'data_hora_inicio': inicio.strftime('%Y-%m-%d %H:%M:%S'),
            'data_hora_fim': fim.strftime('%Y-%m-%d %H:%M:%S'),
            'status_apontamento': 'CONCLUIDO',
            'foi_retrabalho': 0,
            'observacao_os': 'Apontamento de teste criado automaticamente',
            'servico_de_campo': 0,
            'aprovado_supervisor': 1,
            'setor': 'TESTE',
            'horas_orcadas': 2.0,
            'tipo_atividade': 'TESTE',
            'descricao_atividade': 'Atividade de teste para verificar dashboard',
            'resultado_global': 'APROVADO'
        }
        
        # Inserir apontamento
        columns = ', '.join(apontamento_data.keys())
        placeholders = ', '.join(['?' for _ in apontamento_data])
        values = list(apontamento_data.values())
        
        sql = f"INSERT INTO apontamentos_detalhados ({columns}) VALUES ({placeholders})"
        
        cursor.execute(sql, values)
        conn.commit()
        
        apontamento_id = cursor.lastrowid
        print(f"✅ Apontamento criado com ID: {apontamento_id}")
        
        # Verificar se foi criado
        cursor.execute("SELECT COUNT(*) FROM apontamentos_detalhados")
        count = cursor.fetchone()[0]
        print(f"📊 Total de apontamentos na tabela: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar apontamento: {e}")

if __name__ == "__main__":
    criar_apontamento_teste()
