#!/usr/bin/env python3
"""
Criar dados de teste para programações e pendências para o dashboard
"""

import sqlite3
from datetime import datetime, timedelta

def criar_programacoes_teste():
    """Criar programações de teste"""
    print("📅 Criando programações de teste...")
    
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela programacoes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='programacoes'")
        if not cursor.fetchone():
            print("⚠️ Tabela 'programacoes' não existe. Criando...")
            cursor.execute("""
                CREATE TABLE programacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_ordem_servico INTEGER,
                    responsavel_id INTEGER,
                    inicio_previsto DATETIME,
                    fim_previsto DATETIME,
                    status VARCHAR(50) DEFAULT 'ENVIADA',
                    criado_por_id INTEGER,
                    observacoes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    id_setor INTEGER,
                    historico TEXT
                )
            """)
        
        # Buscar dados existentes
        cursor.execute("SELECT id FROM ordens_servico LIMIT 3")
        os_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM tipo_usuarios LIMIT 3")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM tipo_setores LIMIT 3")
        setor_ids = [row[0] for row in cursor.fetchall()]
        
        if not os_ids or not user_ids or not setor_ids:
            print("❌ Dados insuficientes para criar programações")
            return
        
        # Criar programações de teste
        programacoes_teste = [
            {
                'id_ordem_servico': os_ids[0],
                'responsavel_id': user_ids[0],
                'inicio_previsto': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'fim_previsto': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'EM_ANDAMENTO',
                'criado_por_id': user_ids[0],
                'observacoes': 'Programação de teste em andamento',
                'id_setor': setor_ids[0],
                'historico': 'Criada automaticamente para teste'
            },
            {
                'id_ordem_servico': os_ids[1] if len(os_ids) > 1 else os_ids[0],
                'responsavel_id': user_ids[1] if len(user_ids) > 1 else user_ids[0],
                'inicio_previsto': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'fim_previsto': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'ENVIADA',
                'criado_por_id': user_ids[0],
                'observacoes': 'Programação de teste enviada',
                'id_setor': setor_ids[1] if len(setor_ids) > 1 else setor_ids[0],
                'historico': 'Criada automaticamente para teste'
            },
            {
                'id_ordem_servico': os_ids[2] if len(os_ids) > 2 else os_ids[0],
                'responsavel_id': user_ids[2] if len(user_ids) > 2 else user_ids[0],
                'inicio_previsto': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'fim_previsto': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'CONCLUIDA',
                'criado_por_id': user_ids[0],
                'observacoes': 'Programação de teste concluída',
                'id_setor': setor_ids[2] if len(setor_ids) > 2 else setor_ids[0],
                'historico': 'Criada automaticamente para teste'
            }
        ]
        
        for prog in programacoes_teste:
            columns = ', '.join(prog.keys())
            placeholders = ', '.join(['?' for _ in prog])
            values = list(prog.values())
            
            sql = f"INSERT INTO programacoes ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        
        conn.commit()
        print(f"✅ {len(programacoes_teste)} programações criadas")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM programacoes")
        count = cursor.fetchone()[0]
        print(f"📊 Total de programações na tabela: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar programações: {e}")

def criar_pendencias_teste():
    """Criar pendências de teste"""
    print("\n⚠️ Criando pendências de teste...")
    
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela pendencias
        cursor.execute("PRAGMA table_info(pendencias)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Colunas existentes na tabela pendencias: {columns}")

        if not columns:
            print("⚠️ Tabela 'pendencias' não existe. Criando...")
            cursor.execute("""
                CREATE TABLE pendencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_os VARCHAR(50),
                    cliente VARCHAR(255),
                    tipo_maquina VARCHAR(255),
                    descricao_maquina VARCHAR(255),
                    descricao_pendencia TEXT,
                    status VARCHAR(50) DEFAULT 'ABERTA',
                    data_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_fechamento DATETIME,
                    id_responsavel_inicio INTEGER,
                    id_apontamento_origem INTEGER,
                    solucao_aplicada TEXT,
                    observacoes_fechamento TEXT
                )
            """)
            # Atualizar lista de colunas
            cursor.execute("PRAGMA table_info(pendencias)")
            columns = [row[1] for row in cursor.fetchall()]
        
        # Buscar dados existentes
        cursor.execute("SELECT os_numero FROM ordens_servico LIMIT 3")
        os_numeros = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM tipo_usuarios LIMIT 2")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not os_numeros or not user_ids:
            print("❌ Dados insuficientes para criar pendências")
            return
        
        # Criar pendências de teste (apenas com colunas existentes)
        pendencias_base = [
            {
                'numero_os': os_numeros[0],
                'cliente': 'Cliente Teste A',
                'tipo_maquina': 'Equipamento Elétrico',
                'descricao_maquina': 'Motor de teste',
                'descricao_pendencia': 'Necessário recalibração do equipamento após teste',
                'status': 'ABERTA',
                'data_inicio': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'id_responsavel_inicio': user_ids[0]
            },
            {
                'numero_os': os_numeros[1] if len(os_numeros) > 1 else os_numeros[0],
                'cliente': 'Cliente Teste B',
                'tipo_maquina': 'Equipamento Mecânico',
                'descricao_maquina': 'Bomba hidráulica',
                'descricao_pendencia': 'Aguardando peça de reposição para finalizar teste',
                'status': 'ABERTA',
                'data_inicio': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'id_responsavel_inicio': user_ids[1] if len(user_ids) > 1 else user_ids[0]
            },
            {
                'numero_os': os_numeros[2] if len(os_numeros) > 2 else os_numeros[0],
                'cliente': 'Cliente Teste C',
                'tipo_maquina': 'Equipamento Eletrônico',
                'descricao_maquina': 'Controlador PLC',
                'descricao_pendencia': 'Pendência resolvida - equipamento aprovado',
                'status': 'FECHADA',
                'data_inicio': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'data_fechamento': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'id_responsavel_inicio': user_ids[0],
                'solucao_aplicada': 'Ajuste de parâmetros realizado',
                'observacoes_fechamento': 'Teste finalizado com sucesso'
            }
        ]

        # Filtrar apenas colunas que existem na tabela
        pendencias_teste = []
        for pend in pendencias_base:
            pend_filtrada = {k: v for k, v in pend.items() if k in columns}
            pendencias_teste.append(pend_filtrada)
        
        for pend in pendencias_teste:
            columns = ', '.join(pend.keys())
            placeholders = ', '.join(['?' for _ in pend])
            values = list(pend.values())
            
            sql = f"INSERT INTO pendencias ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        
        conn.commit()
        print(f"✅ {len(pendencias_teste)} pendências criadas")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM pendencias")
        count = cursor.fetchone()[0]
        print(f"📊 Total de pendências na tabela: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar pendências: {e}")

def main():
    print("🧪 CRIANDO DADOS DE TESTE PARA DASHBOARD")
    print("=" * 50)
    
    criar_programacoes_teste()
    criar_pendencias_teste()
    
    print("\n✅ Dados de teste criados com sucesso!")
    print("🌐 Agora você pode acessar o dashboard e ver as métricas completas")

if __name__ == "__main__":
    main()
