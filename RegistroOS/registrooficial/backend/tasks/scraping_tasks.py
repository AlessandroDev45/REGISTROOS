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
from typing import Dict, Any, Optional, List

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
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
)

# Configurar engine com WAL mode e timeout para evitar bloqueios
engine = create_engine(
    DATABASE_URL,
    pool_timeout=20,
    pool_recycle=300,
    pool_pre_ping=True,
    connect_args={
        "timeout": 30,
        "check_same_thread": False
    }
)

# Configurar WAL mode para permitir leituras concorrentes
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # WAL mode permite leituras concorrentes
    cursor.execute("PRAGMA journal_mode=WAL")
    # Timeout para escritas
    cursor.execute("PRAGMA busy_timeout=30000")
    # Otimizações
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Obtém sessão do banco de dados com timeout"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def get_db_with_retry(max_retries=3):
    """Obtém sessão do banco com retry em caso de bloqueio"""
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Testar conexão
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            if db:
                db.close()
            if attempt == max_retries - 1:
                raise e
            time.sleep(0.5 * (attempt + 1))  # Backoff exponencial

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

def import_optimized_scraping_module():
    """Importa dinamicamente o módulo de scraping otimizado"""
    script_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\scripts\scrape_os_data_optimized.py"

    if not os.path.exists(script_path):
        # Fallback para o script original se otimizado não existir
        logger.warning("Script otimizado não encontrado, usando script original")
        return import_scraping_module()

    spec = importlib.util.spec_from_file_location("scrape_os_data_optimized", script_path)
    if spec is None:
        logger.warning("Não foi possível carregar script otimizado, usando script original")
        return import_scraping_module()

    scrape_module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        logger.warning("Loader não encontrado para script otimizado, usando script original")
        return import_scraping_module()

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

# ============================================================================
# NOVAS FUNCIONALIDADES PARA PRODUÇÃO - SEM ALTERAR CÓDIGO EXISTENTE
# ============================================================================

def save_batch_stats(task_id: str, user_id: int, batch_name: str, total_os: int, status: str, success: int = 0, errors: int = 0):
    """Salva estatísticas do processamento em lote"""
    try:
        db = get_db_with_retry()

        # Criar tabela de estatísticas se não existir
        create_stats_table_sql = """
        CREATE TABLE IF NOT EXISTS scraping_batch_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            batch_name TEXT NOT NULL,
            total_os INTEGER NOT NULL,
            success_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.execute(text(create_stats_table_sql))

        # Verificar se já existe registro
        existing = db.execute(
            text("SELECT id FROM scraping_batch_stats WHERE task_id = :task_id"),
            {"task_id": task_id}
        ).fetchone()

        if existing:
            # Atualizar registro existente
            update_sql = """
            UPDATE scraping_batch_stats
            SET success_count = :success, error_count = :errors, status = :status, updated_at = CURRENT_TIMESTAMP
            WHERE task_id = :task_id
            """
            db.execute(text(update_sql), {
                "task_id": task_id,
                "success": success,
                "errors": errors,
                "status": status
            })
        else:
            # Inserir novo registro
            insert_sql = """
            INSERT INTO scraping_batch_stats (task_id, user_id, batch_name, total_os, success_count, error_count, status)
            VALUES (:task_id, :user_id, :batch_name, :total_os, :success, :errors, :status)
            """
            db.execute(text(insert_sql), {
                "task_id": task_id,
                "user_id": user_id,
                "batch_name": batch_name,
                "total_os": total_os,
                "success": success,
                "errors": errors,
                "status": status
            })

        db.commit()

    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"❌ Erro ao salvar estatísticas do lote: {e}")
    finally:
        if db:
            db.close()

def save_scraping_usage_stats(user_id: int, os_number: str, success: bool, processing_time: float = 0):
    """Salva estatísticas de uso individual do scraping"""
    try:
        db = get_db_with_retry()

        # Criar tabela de uso se não existir
        create_usage_table_sql = """
        CREATE TABLE IF NOT EXISTS scraping_usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            os_number TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            processing_time REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.execute(text(create_usage_table_sql))

        # Inserir registro de uso
        insert_sql = """
        INSERT INTO scraping_usage_stats (user_id, os_number, success, processing_time)
        VALUES (:user_id, :os_number, :success, :processing_time)
        """
        db.execute(text(insert_sql), {
            "user_id": user_id,
            "os_number": os_number,
            "success": success,
            "processing_time": processing_time
        })

        db.commit()

    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"❌ Erro ao salvar estatísticas de uso: {e}")
    finally:
        if db:
            db.close()

@app.task(bind=True, max_retries=3)
def scrape_batch_os_task(self, os_numbers: List[str], user_id: int, batch_name: str = None) -> Dict[str, Any]:
    """
    Task assíncrona para scraping em lote de múltiplas OS
    Processa várias OS em paralelo com controle de concorrência
    """
    task_id = self.request.id
    batch_name = batch_name or f"Lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    logger.info(f"🚀 Iniciando scraping em lote: {batch_name} - {len(os_numbers)} OS (Task: {task_id}, User: {user_id})")

    # Salvar estatísticas do lote
    save_batch_stats(task_id, user_id, batch_name, len(os_numbers), "INICIADO")

    try:
        db = get_db()

        # Atualizar progresso inicial
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 0,
                'status': f'Iniciando processamento de {len(os_numbers)} OS...',
                'batch_name': batch_name,
                'total_os': len(os_numbers),
                'processed': 0,
                'success': 0,
                'errors': 0
            }
        )

        results = []
        success_count = 0
        error_count = 0

        # Processar OS em grupos menores para evitar sobrecarga
        batch_size = 5  # Processar 5 OS por vez
        total_batches = (len(os_numbers) + batch_size - 1) // batch_size

        for batch_idx, i in enumerate(range(0, len(os_numbers), batch_size)):
            batch_os = os_numbers[i:i + batch_size]

            logger.info(f"📦 Processando lote {batch_idx + 1}/{total_batches}: {batch_os}")

            # Processar lote atual
            batch_results = []
            for os_num in batch_os:
                start_time = time.time()
                try:
                    # Executar scraping individual com versão otimizada
                    scrape_module = import_optimized_scraping_module()

                    # Usar função otimizada se disponível, senão usar original
                    if hasattr(scrape_module, 'execute_scraping_optimized'):
                        scraped_data = scrape_module.execute_scraping_optimized(os_num, f"batch_{task_id}")
                    else:
                        scraped_data = scrape_module.execute_scraping(os_num)

                    processing_time = time.time() - start_time

                    if scraped_data and len(scraped_data) > 0:
                        # Salvar dados no banco
                        if save_scraped_os_data(db, scraped_data[0], os_num):
                            success_count += 1
                            batch_results.append({"os": os_num, "status": "success", "data": scraped_data[0]})
                            save_scraping_usage_stats(user_id, os_num, True, processing_time)
                            logger.info(f"✅ OS {os_num} processada com sucesso em {processing_time:.2f}s")
                        else:
                            error_count += 1
                            batch_results.append({"os": os_num, "status": "error", "message": "Erro ao salvar no banco"})
                            save_scraping_usage_stats(user_id, os_num, False, processing_time)
                    else:
                        error_count += 1
                        batch_results.append({"os": os_num, "status": "not_found", "message": "OS não encontrada"})
                        save_scraping_usage_stats(user_id, os_num, False, processing_time)

                except Exception as e:
                    processing_time = time.time() - start_time
                    error_count += 1
                    batch_results.append({"os": os_num, "status": "error", "message": str(e)})
                    save_scraping_usage_stats(user_id, os_num, False, processing_time)
                    logger.error(f"❌ Erro ao processar OS {os_num}: {e}")

                # Atualizar progresso
                processed = success_count + error_count
                progress = int((processed / len(os_numbers)) * 100)

                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'status': f'Processando... {processed}/{len(os_numbers)}',
                        'batch_name': batch_name,
                        'total_os': len(os_numbers),
                        'processed': processed,
                        'success': success_count,
                        'errors': error_count,
                        'current_os': os_num
                    }
                )

            results.extend(batch_results)

            # Pequena pausa entre lotes para não sobrecarregar
            if batch_idx < total_batches - 1:
                time.sleep(2)

        # Finalizar processamento
        final_status = "CONCLUIDO" if error_count == 0 else "CONCLUIDO_COM_ERROS"
        save_batch_stats(task_id, user_id, batch_name, len(os_numbers), final_status, success_count, error_count)

        db.close()

        logger.info(f"✅ Lote {batch_name} concluído: {success_count} sucessos, {error_count} erros")

        return {
            "status": "completed",
            "batch_name": batch_name,
            "total_os": len(os_numbers),
            "success_count": success_count,
            "error_count": error_count,
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Erro crítico no processamento do lote {batch_name}: {e}")
        save_batch_stats(task_id, user_id, batch_name, len(os_numbers), "ERRO", 0, len(os_numbers))

        if self.request.retries < 3:
            raise self.retry(countdown=60 * (2 ** self.request.retries))

        return {
            "status": "error",
            "batch_name": batch_name,
            "message": str(e),
            "total_os": len(os_numbers)
        }

def get_scraping_statistics(days: int = 30) -> Dict[str, Any]:
    """Obtém estatísticas detalhadas de uso do scraping"""
    db = None
    try:
        db = get_db_with_retry()

        # Criar tabelas se não existirem
        create_usage_table_sql = """
        CREATE TABLE IF NOT EXISTS scraping_usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            os_number TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            processing_time REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        create_batch_table_sql = """
        CREATE TABLE IF NOT EXISTS scraping_batch_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            batch_name TEXT,
            total_os INTEGER NOT NULL,
            success_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        db.execute(text(create_usage_table_sql))
        db.execute(text(create_batch_table_sql))
        db.commit()

        # Estatísticas gerais dos últimos X dias
        general_stats_sql = """
        SELECT
            COUNT(*) as total_requests,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
            AVG(processing_time) as avg_processing_time,
            MAX(processing_time) as max_processing_time,
            MIN(processing_time) as min_processing_time
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-{} days')
        """.format(days)

        general_stats = db.execute(text(general_stats_sql)).fetchone()

        # Estatísticas por usuário
        user_stats_sql = """
        SELECT
            u.nome_completo,
            u.email,
            u.departamento,
            COUNT(s.id) as total_requests,
            SUM(CASE WHEN s.success = 1 THEN 1 ELSE 0 END) as successful_requests,
            AVG(s.processing_time) as avg_processing_time
        FROM scraping_usage_stats s
        JOIN tipo_usuarios u ON s.user_id = u.id
        WHERE s.created_at >= datetime('now', '-{} days')
        GROUP BY s.user_id, u.nome_completo, u.email, u.departamento
        ORDER BY total_requests DESC
        """.format(days)

        user_stats = db.execute(text(user_stats_sql)).fetchall()

        # Estatísticas por dia (últimos 30 dias)
        daily_stats_sql = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as total_requests,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
            AVG(processing_time) as avg_processing_time
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """

        daily_stats = db.execute(text(daily_stats_sql)).fetchall()

        # Estatísticas de lotes
        batch_stats_sql = """
        SELECT
            batch_name,
            total_os,
            success_count,
            error_count,
            status,
            created_at,
            updated_at
        FROM scraping_batch_stats
        WHERE created_at >= datetime('now', '-{} days')
        ORDER BY created_at DESC
        LIMIT 20
        """.format(days)

        batch_stats = db.execute(text(batch_stats_sql)).fetchall()

        # Top OS mais consultadas
        top_os_sql = """
        SELECT
            os_number,
            COUNT(*) as request_count,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
            AVG(processing_time) as avg_processing_time
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY os_number
        ORDER BY request_count DESC
        LIMIT 10
        """.format(days)

        top_os = db.execute(text(top_os_sql)).fetchall()

        # Converter resultados para dicionários
        return {
            "general_stats": {
                "total_requests": general_stats[0] if general_stats else 0,
                "successful_requests": general_stats[1] if general_stats else 0,
                "failed_requests": general_stats[2] if general_stats else 0,
                "success_rate": round((general_stats[1] / general_stats[0] * 100) if general_stats and general_stats[0] > 0 else 0, 2),
                "avg_processing_time": round(general_stats[3], 2) if general_stats and general_stats[3] else 0,
                "max_processing_time": round(general_stats[4], 2) if general_stats and general_stats[4] else 0,
                "min_processing_time": round(general_stats[5], 2) if general_stats and general_stats[5] else 0
            },
            "user_stats": [
                {
                    "name": row[0],
                    "email": row[1],
                    "department": row[2],
                    "total_requests": row[3],
                    "successful_requests": row[4],
                    "success_rate": round((row[4] / row[3] * 100) if row[3] > 0 else 0, 2),
                    "avg_processing_time": round(row[5], 2) if row[5] else 0
                }
                for row in user_stats
            ],
            "daily_stats": [
                {
                    "date": row[0],
                    "total_requests": row[1],
                    "successful_requests": row[2],
                    "success_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2),
                    "avg_processing_time": round(row[3], 2) if row[3] else 0
                }
                for row in daily_stats
            ],
            "batch_stats": [
                {
                    "batch_name": row[0],
                    "total_os": row[1],
                    "success_count": row[2],
                    "error_count": row[3],
                    "status": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "success_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in batch_stats
            ],
            "top_os": [
                {
                    "os_number": row[0],
                    "request_count": row[1],
                    "success_count": row[2],
                    "success_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2),
                    "avg_processing_time": round(row[3], 2) if row[3] else 0
                }
                for row in top_os
            ]
        }

    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas de scraping: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()
