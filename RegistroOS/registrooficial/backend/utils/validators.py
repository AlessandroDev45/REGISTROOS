"""
Validadores do Sistema RegistroOS
=================================

Este módulo contém funções de validação para garantir consistência
dos dados em todo o sistema.
"""

import re
from typing import Optional, Union
from fastapi import HTTPException, status
from .text_validators import validar_texto_obrigatorio, validar_texto_opcional, limpar_texto

def validate_os_format(os_number: Union[str, int]) -> bool:
    """
    Validar se a ordem de serviço segue o formato: 5 caracteres numéricos
    
    Args:
        os_number: Número da ordem de serviço para validar
        
    Returns:
        bool: True se válido, False se inválido
        
    Raises:
        HTTPException: Se o formato for inválido
    """
    if not os_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número da OS é obrigatório"
        )
    
    # Converter para string e remover espaços
    os_number = str(os_number).strip()
    
    # Validar formato: exatamente 5 caracteres numéricos
    if not re.match(r'^\d{5}$', os_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de OS inválido. Use 5 caracteres numéricos (ex: 12345), recebido: {os_number}"
        )
    
    return True

def validate_os_format_safe(os_number: Optional[str]) -> bool:
    """
    Validar formato de OS sem lançar exceção
    
    Args:
        os_number: Número da ordem de serviço para validar
        
    Returns:
        bool: True se válido, False se inválido
    """
    if not os_number:
        return False
    
    os_number = str(os_number).strip()
    return bool(re.match(r'^\d{5}$', os_number))

def format_os_number(os_number: Union[str, int]) -> str:
    """
    Formatar número da OS para garantir 5 caracteres numéricos
    
    Args:
        os_number: Número da OS para formatar
        
    Returns:
        str: Número formatado com 5 caracteres
        
    Raises:
        HTTPException: Se não for possível formatar
    """
    if isinstance(os_number, int):
        os_number = str(os_number)
    
    os_number = os_number.strip()
    
    # Remover qualquer caractere não numérico
    cleaned = re.sub(r'[^\d]', '', os_number)
    
    if len(cleaned) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OS deve ter exatamente 5 caracteres numéricos, recebido: {os_number}"
        )
    
    return cleaned

def validate_and_format_os(os_number: Union[str, int]) -> str:
    """
    Validar e formatar número da OS
    
    Args:
        os_number: Número da OS para validar e formatar
        
    Returns:
        str: Número formatado e validado
    """
    validate_os_format(os_number)
    return format_os_number(os_number)

def check_os_exists(os_number: str, db, model_class) -> bool:
    """
    Verificar se a ordem de serviço existe no banco de dados
    
    Args:
        os_number: Número da OS
        db: Sessão do banco de dados
        model_class: Classe do modelo (OrdemServico)
        
    Returns:
        bool: True se existir, False se não existir
    """
    try:
        formatted_os = validate_and_format_os(os_number)
        existing = db.query(model_class).filter(model_class.os_numero == formatted_os).first()
        return existing is not None
    except HTTPException:
        return False

def generate_next_os(db, model_class, prefix: str = "") -> str:
    """
    Gerar próximo número de OS no formato 5 caracteres numéricos

    Args:
        db: Sessão do banco de dados
        model_class: Classe do modelo (OrdemServico)
        prefix: Prefixo para o número da OS (padrão: "" - apenas números)

    Returns:
        str: Próximo número de OS formatado (apenas 5 dígitos)
    """
    # Buscar maior número existente
    last_os = db.query(model_class).order_by(model_class.id.desc()).first()

    if last_os and last_os.os_numero:
        try:
            # Extrair apenas os caracteres numéricos
            numeric_part = ''.join(filter(str.isdigit, str(last_os.os_numero)))
            if numeric_part and len(numeric_part) <= 5:
                last_number = int(numeric_part)
                next_number = last_number + 1

                # Garantir 5 dígitos com zeros à esquerda (SEM PREFIXO)
                return f"{next_number:05d}"
        except (ValueError, IndexError):
            pass

    # Se não conseguir gerar do existente, começar de 10001
    return "10001"
