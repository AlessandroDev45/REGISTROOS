"""
CONFIGURAÇÃO DO CELERY PARA SCRAPING ASSÍNCRONO
===============================================

Sistema de filas para scraping escalável em produção
"""

import os
import sys
import logging
from celery import Celery
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Celery
app = Celery('scraping_tasks')

# Configurações do Redis/Broker
app.conf.update(
    # Broker (Redis)
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Configurações de task
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # Configurações de performance
    task_routes={
        'scraping_tasks.scrape_os_task': {'queue': 'scraping'},
        'scraping_tasks.cleanup_task': {'queue': 'maintenance'},
    },
    
    # Limites de recursos
    worker_concurrency=3,  # Máximo 3 workers simultâneos
    task_time_limit=300,   # 5 minutos timeout
    task_soft_time_limit=240,  # 4 minutos soft timeout
    
    # Retry configurações
    task_default_retry_delay=60,  # 1 minuto entre retries
    task_max_retries=3,
    
    # Rate limiting
    task_annotations={
        'scraping_tasks.scrape_os_task': {
            'rate_limit': '10/h',  # 10 por hora por worker
        }
    },
    
    # Configurações de resultado
    result_expires=3600,  # Resultados expiram em 1 hora
    task_ignore_result=False,
    
    # Configurações de monitoramento
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Importar tasks
# Importações serão feitas dinamicamente para evitar circular imports

# Auto-discovery de tasks
app.autodiscover_tasks(['tasks'])

# Configurar beat schedule para limpeza automática
app.conf.beat_schedule = {
    'cleanup-old-tasks': {
        'task': 'scraping_tasks.cleanup_old_tasks',
        'schedule': timedelta(hours=1),  # Executar a cada hora
    },
}

if __name__ == '__main__':
    app.start()
