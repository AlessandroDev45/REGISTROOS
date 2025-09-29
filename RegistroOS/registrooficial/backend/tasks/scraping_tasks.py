"""
TASKS ASSÍNCRONAS PARA SCRAPING
===============================

Implementa scraping assíncrono com filas para produção
Mantém toda a lógica de criação de dados existente
"""

import os
import sys
import json
import logging
import importlib.util
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import os

# Importação condicional do Celery
try:
    from celery import current_task, Celery
    CELERY_AVAILABLE = True
    # Configurar Celery diretamente aqui para evitar importação circular
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app = Celery('scraping_tasks', broker=redis_url, backend=redis_url)
except ImportError:
    CELERY_AVAILABLE = False
    # Mock para quando Celery não estiver disponível
    current_task = None

    # Mock app com decoradores que não fazem nada
    class MockApp:
        def task(self, *args, **kwargs):
            _ = args, kwargs  # Silenciar warning
            def decorator(func):
                return func
            return decorator

        @property
        def control(self):
            return MockControl()

    class MockControl:
        def inspect(self):
            return MockInspect()

    class MockInspect:
        def active(self):
            return {}

        def scheduled(self):
            return {}

        def stats(self):
            return {}

    app = MockApp()
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Obtém sessão do banco de dados"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def import_scraping_module():
    """Importa dinamicamente o módulo de scraping"""
    script_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\scripts\scrape_os_data.py"
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script de scraping não encontrado: {script_path}")
    
    spec = importlib.util.spec_from_file_location("scrape_os_data", script_path)
    if spec is None:
        raise ImportError(f"Could not load spec from {script_path}")

    scrape_module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"No loader found for spec from {script_path}")

    spec.loader.exec_module(scrape_module)
    
    return scrape_module

def create_cliente_from_data(db, os_data: Dict[str, Any]) -> Optional[int]:
    """Cria cliente baseado nos dados do scraping"""
    try:
        cliente_nome = os_data.get('CLIENTE', os_data.get('NOME CLIENTE', ''))
        cliente_cnpj = os_data.get('CNPJ', '')
        
        if not cliente_nome or not cliente_nome.strip():
            return None
        
        # Buscar cliente existente
        check_sql = text("""
            SELECT id FROM clientes 
            WHERE LOWER(razao_social) LIKE LOWER(:nome)
            LIMIT 1
        """)
        
        result = db.execute(check_sql, {"nome": f"%{cliente_nome.strip()}%"}).fetchone()
        
        if result:
            logger.info(f"✅ Cliente existente encontrado: {cliente_nome} (ID: {result[0]})")
            return result[0]
        
        # Criar novo cliente
        insert_sql = text("""
            INSERT INTO clientes (
                razao_social, nome_fantasia, cnpj_cpf, contato_principal,
                telefone_contato, email_contato, endereco, data_criacao, data_ultima_atualizacao
            ) VALUES (
                :razao_social, :nome_fantasia, :cnpj_cpf, :contato_principal,
                :telefone_contato, :email_contato, :endereco, :data_criacao, :data_ultima_atualizacao
            )
        """)
        
        db.execute(insert_sql, {
            "razao_social": cliente_nome.strip(),
            "nome_fantasia": cliente_nome.strip(),
            "cnpj_cpf": cliente_cnpj.strip() if cliente_cnpj else None,
            "contato_principal": "Contato via scraping",
            "telefone_contato": "",
            "email_contato": "",
            "endereco": os_data.get('MUNICIPIO', ''),
            "data_criacao": datetime.now().isoformat(),
            "data_ultima_atualizacao": datetime.now().isoformat()
        })
        
        # Obter ID do cliente criado
        cliente_id = db.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
        logger.info(f"✅ Novo cliente criado: {cliente_nome} (ID: {cliente_id})")
        
        return cliente_id
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar cliente: {e}")
        return None

def create_equipamento_from_data(db, os_data: Dict[str, Any]) -> Optional[int]:
    """Cria equipamento baseado nos dados do scraping"""
    try:
        equipamento_desc = os_data.get('DESCRIÇÃO', os_data.get('TIPO DO EQUIPAMENTO', ''))
        equipamento_fabricante = os_data.get('FABRICANTE', '')
        equipamento_modelo = os_data.get('MODELO', '')
        equipamento_serie = os_data.get('NUMERO DE SERIE', '')
        
        if not equipamento_desc or not equipamento_desc.strip():
            return None
        
        # Buscar equipamento existente
        check_sql = text("""
            SELECT id FROM equipamentos 
            WHERE LOWER(descricao) LIKE LOWER(:desc)
            LIMIT 1
        """)
        
        result = db.execute(check_sql, {"desc": f"%{equipamento_desc.strip()[:50]}%"}).fetchone()
        
        if result:
            logger.info(f"✅ Equipamento existente encontrado: {equipamento_desc[:50]} (ID: {result[0]})")
            return result[0]
        
        # Criar novo equipamento
        insert_sql = text("""
            INSERT INTO equipamentos (
                descricao, tipo, fabricante, modelo, numero_serie, 
                data_criacao, data_ultima_atualizacao
            ) VALUES (
                :descricao, :tipo, :fabricante, :modelo, :numero_serie,
                :data_criacao, :data_ultima_atualizacao
            )
        """)
        
        db.execute(insert_sql, {
            "descricao": equipamento_desc.strip(),
            "tipo": os_data.get('TIPO DO EQUIPAMENTO', 'Equipamento via scraping'),
            "fabricante": equipamento_fabricante.strip() if equipamento_fabricante else None,
            "modelo": equipamento_modelo.strip() if equipamento_modelo else None,
            "numero_serie": equipamento_serie.strip() if equipamento_serie else None,
            "data_criacao": datetime.now().isoformat(),
            "data_ultima_atualizacao": datetime.now().isoformat()
        })
        
        # Obter ID do equipamento criado
        equipamento_id = db.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
        logger.info(f"✅ Novo equipamento criado: {equipamento_desc[:50]} (ID: {equipamento_id})")
        
        return equipamento_id
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar equipamento: {e}")
        return None

def save_os_with_relationships(db, os_data: Dict[str, Any], numero_os: str, cliente_id: Optional[int], equipamento_id: Optional[int]) -> bool:
    """Salva OS com relacionamentos no banco"""
    try:
        equipamento_desc = os_data.get('DESCRIÇÃO', os_data.get('TIPO DO EQUIPAMENTO', ''))
        cliente_nome = os_data.get('CLIENTE', os_data.get('NOME CLIENTE', ''))
        cliente_cnpj = os_data.get('CNPJ', '')
        
        insert_sql = text("""
            INSERT OR REPLACE INTO ordens_servico (
                os_numero, id_cliente, id_equipamento, descricao_maquina, 
                status_os, data_criacao, prioridade, observacoes_gerais
            ) VALUES (
                :os_numero, :id_cliente, :id_equipamento, :descricao, 
                :status, datetime('now'), :prioridade, :observacoes
            )
        """)
        
        db.execute(insert_sql, {
            "os_numero": os_data.get('OS', numero_os),
            "id_cliente": cliente_id,
            "id_equipamento": equipamento_id,
            "status": os_data.get('STATUS DA OS', 'COLETADA VIA SCRAPING'),
            "descricao": equipamento_desc[:200] if equipamento_desc else f"Equipamento da OS {numero_os}",
            "prioridade": "MEDIA",
            "observacoes": f"OS criada via scraping assíncrono - Cliente: {cliente_nome} - CNPJ: {cliente_cnpj}"
        })
        
        db.commit()
        logger.info(f"✅ OS {numero_os} salva com relacionamentos: Cliente ID {cliente_id}, Equipamento ID {equipamento_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar OS: {e}")
        db.rollback()
        return False

@app.task(bind=True, max_retries=3)
def scrape_os_task(self, numero_os: str, user_id: int) -> Dict[str, Any]:
    """
    Task assíncrona para scraping de OS
    Mantém toda a lógica de criação de dados existente
    """
    task_id = self.request.id
    logger.info(f"🚀 Iniciando scraping assíncrono para OS {numero_os} (Task: {task_id}, User: {user_id})")
    
    try:
        # Atualizar progresso: Iniciando
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'status': 'Iniciando scraping...', 'numero_os': numero_os}
        )
        
        # 1. Verificar se OS já existe no banco
        db = get_db()
        
        check_sql = text("SELECT * FROM ordens_servico WHERE os_numero = :numero_os")
        existing_os = db.execute(check_sql, {"numero_os": numero_os}).fetchone()
        
        if existing_os:
            logger.info(f"✅ OS {numero_os} já existe no banco")
            db.close()
            return {
                "status": "found_existing",
                "message": f"OS {numero_os} já existe no sistema",
                "data": dict(existing_os._mapping) if hasattr(existing_os, '_mapping') else dict(existing_os),
                "fonte": "banco_local"
            }
        
        # Atualizar progresso: Executando scraping
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'status': 'Executando scraping externo...', 'numero_os': numero_os}
        )
        
        # 2. Executar scraping externo
        scrape_module = import_scraping_module()
        scraped_data = scrape_module.execute_scraping(numero_os)
        
        if not scraped_data or len(scraped_data) == 0:
            logger.warning(f"⚠️ Nenhum dado coletado para OS {numero_os}")
            db.close()
            return {
                "status": "not_found",
                "message": f"OS {numero_os} não encontrada no sistema externo",
                "data": None
            }
        
        # Atualizar progresso: Processando dados
        self.update_state(
            state='PROGRESS',
            meta={'progress': 60, 'status': 'Processando dados coletados...', 'numero_os': numero_os}
        )
        
        # 3. Processar dados coletados
        os_data = scraped_data[0]  # Primeiro resultado
        logger.info(f"📊 Dados coletados para OS {numero_os}: {len(os_data)} campos")
        
        # 4. Criar/buscar cliente
        cliente_id = create_cliente_from_data(db, os_data)
        
        # 5. Criar/buscar equipamento
        equipamento_id = create_equipamento_from_data(db, os_data)
        
        # Atualizar progresso: Salvando no banco
        self.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'status': 'Salvando dados no banco...', 'numero_os': numero_os}
        )
        
        # 6. Salvar OS com relacionamentos
        if save_os_with_relationships(db, os_data, numero_os, cliente_id, equipamento_id):
            # Buscar OS criada para retornar dados completos
            final_sql = text("""
                SELECT os.*, c.razao_social as cliente_nome, e.descricao as equipamento_descricao
                FROM ordens_servico os
                LEFT JOIN clientes c ON os.id_cliente = c.id
                LEFT JOIN equipamentos e ON os.id_equipamento = e.id
                WHERE os.os_numero = :numero_os
            """)
            
            final_result = db.execute(final_sql, {"numero_os": numero_os}).fetchone()
            
            db.close()
            
            # Atualizar progresso: Concluído
            self.update_state(
                state='PROGRESS',
                meta={'progress': 100, 'status': 'Scraping concluído com sucesso!', 'numero_os': numero_os}
            )
            
            logger.info(f"✅ Scraping concluído com sucesso para OS {numero_os}")
            
            return {
                "status": "success",
                "message": f"OS {numero_os} coletada e salva com sucesso",
                "data": dict(final_result._mapping) if final_result and hasattr(final_result, '_mapping') else {},
                "fonte": "scraping",
                "cliente_id": cliente_id,
                "equipamento_id": equipamento_id,
                "scraped_fields": len(os_data)
            }
        else:
            db.close()
            raise Exception("Falha ao salvar OS no banco de dados")
    
    except Exception as e:
        logger.error(f"❌ Erro no scraping da OS {numero_os}: {e}")
        
        # Retry automático
        if self.request.retries < 3:
            logger.info(f"🔄 Tentativa {self.request.retries + 1}/3 para OS {numero_os}")
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)
        
        # Falha final
        return {
            "status": "error",
            "message": f"Erro no scraping da OS {numero_os}: {str(e)}",
            "data": None,
            "retries": self.request.retries
        }

@app.task
def cleanup_old_tasks():
    """Remove tasks antigas do Redis"""
    try:
        # Implementar limpeza de tasks antigas
        logger.info("🧹 Executando limpeza de tasks antigas")
        return {"status": "success", "message": "Limpeza executada"}
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        return {"status": "error", "message": str(e)}

@app.task
def get_queue_status():
    """Retorna status da fila de scraping"""
    try:
        inspect = app.control.inspect()
        
        # Obter informações dos workers
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        
        total_active = sum(len(tasks) for tasks in (active_tasks or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
        
        return {
            "active_tasks": total_active,
            "scheduled_tasks": total_scheduled,
            "total_queue": total_active + total_scheduled,
            "workers_online": len(active_tasks or {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter status da fila: {e}")
        return {"error": str(e)}
