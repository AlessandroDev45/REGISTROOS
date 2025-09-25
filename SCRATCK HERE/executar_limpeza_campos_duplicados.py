#!/usr/bin/env python3
"""
LIMPEZA DE CAMPOS DUPLICADOS E SIMILARES
========================================

Este script remove campos redundantes identificados na análise.

CAMPOS IDENTIFICADOS PARA REMOÇÃO:
- ordens_servico.status_geral (todos NULL, redundante com status_os)
- apontamentos_detalhados.setor (redundante com id_setor FK)
- tipo_usuarios.setor (redundante com id_setor FK)
- tipo_usuarios.departamento (redundante com id_departamento FK)
- tipo_setores.departamento (redundante com id_departamento FK)
- tipos_maquina.setor (redundante, usar id_departamento)
- tipos_maquina.departamento (redundante com id_departamento FK)

EXECUÇÃO:
python executar_limpeza_campos_duplicados.py
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('limpeza_campos_duplicados.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
BACKUP_DIR = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\SCRATCK HERE\backups"

def criar_backup():
    """Criar backup do banco de dados antes da limpeza"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"registroos_backup_limpeza_campos_{timestamp}.db")
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return None

def verificar_inconsistencias():
    """Verificar inconsistências antes da remoção"""
    try:
        logger.info("Verificando inconsistências nos campos duplicados...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar status_geral vs status_os
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status_geral IS NOT NULL THEN 1 END) as status_geral_preenchidos,
                COUNT(CASE WHEN status_os != status_geral THEN 1 END) as diferentes
            FROM ordens_servico
        """)
        
        result = cursor.fetchone()
        logger.info(f"ordens_servico - Total: {result[0]}, status_geral preenchidos: {result[1]}, diferentes: {result[2]}")
        
        # Verificar setor vs id_setor em apontamentos
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN a.setor != s.nome THEN 1 END) as diferentes,
                COUNT(CASE WHEN a.setor IS NOT NULL AND s.nome IS NULL THEN 1 END) as setor_sem_fk
            FROM apontamentos_detalhados a
            LEFT JOIN tipo_setores s ON a.id_setor = s.id
            WHERE a.setor IS NOT NULL
        """)
        
        result = cursor.fetchone()
        logger.info(f"apontamentos_detalhados - Total com setor: {result[0]}, diferentes: {result[1]}, sem FK: {result[2]}")
        
        # Verificar usuários
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN u.setor != s.nome THEN 1 END) as setor_diferente,
                COUNT(CASE WHEN u.departamento != d.nome_tipo THEN 1 END) as dept_diferente
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON u.id_departamento = d.id
            WHERE u.setor IS NOT NULL OR u.departamento IS NOT NULL
        """)
        
        result = cursor.fetchone()
        logger.info(f"tipo_usuarios - Total: {result[0]}, setor diferente: {result[1]}, dept diferente: {result[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar inconsistências: {str(e)}")
        return False

def executar_limpeza():
    """Executar a limpeza dos campos duplicados"""
    try:
        logger.info("Iniciando limpeza de campos duplicados...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Lista de comandos de remoção
        comandos_remocao = [
            # 1. Remover status_geral de ordens_servico (todos NULL)
            {
                'sql': 'ALTER TABLE ordens_servico DROP COLUMN status_geral',
                'descricao': 'Removendo status_geral de ordens_servico'
            },
            
            # 2. Remover setor de apontamentos_detalhados (redundante com id_setor)
            {
                'sql': 'ALTER TABLE apontamentos_detalhados DROP COLUMN setor',
                'descricao': 'Removendo setor de apontamentos_detalhados'
            },
            
            # 3. Remover setor e departamento de tipo_usuarios
            {
                'sql': 'ALTER TABLE tipo_usuarios DROP COLUMN setor',
                'descricao': 'Removendo setor de tipo_usuarios'
            },
            {
                'sql': 'ALTER TABLE tipo_usuarios DROP COLUMN departamento',
                'descricao': 'Removendo departamento de tipo_usuarios'
            },
            
            # 4. Remover departamento de tipo_setores
            {
                'sql': 'ALTER TABLE tipo_setores DROP COLUMN departamento',
                'descricao': 'Removendo departamento de tipo_setores'
            },
            
            # 5. Remover setor e departamento de tipos_maquina
            {
                'sql': 'ALTER TABLE tipos_maquina DROP COLUMN setor',
                'descricao': 'Removendo setor de tipos_maquina'
            },
            {
                'sql': 'ALTER TABLE tipos_maquina DROP COLUMN departamento',
                'descricao': 'Removendo departamento de tipos_maquina'
            },
        ]
        
        # Executar comandos
        for i, comando in enumerate(comandos_remocao, 1):
            try:
                logger.info(f"Executando {i}/{len(comandos_remocao)}: {comando['descricao']}")
                cursor.execute(comando['sql'])
                conn.commit()
                logger.info(f"Sucesso: {comando['descricao']}")
            except sqlite3.OperationalError as e:
                if "no such column" in str(e).lower():
                    logger.info(f"Campo já removido: {comando['descricao']}")
                else:
                    logger.error(f"Erro: {comando['descricao']} - {str(e)}")
                    raise
        
        conn.close()
        logger.info("Limpeza de campos duplicados concluída!")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante limpeza: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def verificar_resultado():
    """Verificar resultado da limpeza"""
    try:
        logger.info("Verificando resultado da limpeza...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estruturas das tabelas principais
        tabelas_verificar = [
            'ordens_servico',
            'apontamentos_detalhados', 
            'tipo_usuarios',
            'tipo_setores',
            'tipos_maquina'
        ]
        
        for tabela in tabelas_verificar:
            cursor.execute(f"PRAGMA table_info({tabela})")
            campos = [row[1] for row in cursor.fetchall()]
            logger.info(f"{tabela}: {len(campos)} campos restantes")
            
            # Verificar se campos duplicados foram removidos
            campos_removidos = []
            if tabela == 'ordens_servico' and 'status_geral' not in campos:
                campos_removidos.append('status_geral')
            elif tabela == 'apontamentos_detalhados' and 'setor' not in campos:
                campos_removidos.append('setor')
            elif tabela == 'tipo_usuarios':
                if 'setor' not in campos:
                    campos_removidos.append('setor')
                if 'departamento' not in campos:
                    campos_removidos.append('departamento')
            elif tabela == 'tipo_setores' and 'departamento' not in campos:
                campos_removidos.append('departamento')
            elif tabela == 'tipos_maquina':
                if 'setor' not in campos:
                    campos_removidos.append('setor')
                if 'departamento' not in campos:
                    campos_removidos.append('departamento')
            
            if campos_removidos:
                logger.info(f"  Campos removidos: {', '.join(campos_removidos)}")
        
        # Verificar contagem de registros
        cursor.execute("SELECT COUNT(*) FROM ordens_servico")
        total_os = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM apontamentos_detalhados")
        total_apontamentos = cursor.fetchone()[0]
        
        logger.info(f"Dados preservados - OS: {total_os}, Apontamentos: {total_apontamentos}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar resultado: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("INICIANDO LIMPEZA DE CAMPOS DUPLICADOS")
    logger.info("=" * 60)
    
    # Verificar se o banco existe
    if not os.path.exists(DB_PATH):
        logger.error(f"Banco de dados não encontrado: {DB_PATH}")
        return False
    
    # 1. Criar backup
    backup_path = criar_backup()
    if not backup_path:
        logger.error("Falha ao criar backup - Abortando limpeza")
        return False
    
    # 2. Verificar inconsistências
    if not verificar_inconsistencias():
        logger.error("Falha ao verificar inconsistências")
        return False
    
    # 3. Executar limpeza
    if not executar_limpeza():
        logger.error("Falha durante limpeza")
        logger.info(f"Backup disponível em: {backup_path}")
        return False
    
    # 4. Verificar resultado
    if not verificar_resultado():
        logger.error("Falha na verificação pós-limpeza")
        logger.info(f"Backup disponível em: {backup_path}")
        return False
    
    logger.info("=" * 60)
    logger.info("LIMPEZA DE CAMPOS DUPLICADOS CONCLUÍDA COM SUCESSO!")
    logger.info("=" * 60)
    logger.info(f"Backup salvo em: {backup_path}")
    logger.info("Campos duplicados removidos com sucesso")
    logger.info("Estrutura do banco otimizada")
    
    return True

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        logger.error("Limpeza falhou - Verifique os logs acima")
        exit(1)
    else:
        logger.info("Limpeza concluída - Banco otimizado")
        exit(0)
