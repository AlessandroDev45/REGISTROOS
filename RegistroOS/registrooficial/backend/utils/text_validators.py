"""
Validadores de Texto - RegistroOS Backend
=========================================

Validadores para garantir que todos os campos de texto aceitem apenas:
- Letras maiúsculas (A-Z)
- Números (0-9)
- Caracteres permitidos: espaço, hífen, underscore, ponto, parênteses, barra

Bloqueia:
- Letras minúsculas
- Caracteres especiais não permitidos
"""

import re
from typing import Optional, Union
from fastapi import HTTPException, status

# Caracteres permitidos além de letras maiúsculas e números
CARACTERES_PERMITIDOS = r'A-Z0-9\s\-_.\/\(\)'

# Regex para validação completa
REGEX_TEXTO_VALIDO = re.compile(f'^[{CARACTERES_PERMITIDOS}]*$')

# Regex para caracteres não permitidos
REGEX_CARACTERES_INVALIDOS = re.compile(f'[^{CARACTERES_PERMITIDOS}]')

def limpar_texto(texto: str) -> str:
    """
    Limpa o texto removendo caracteres não permitidos e convertendo para maiúscula
    
    Args:
        texto: Texto para limpar
        
    Returns:
        str: Texto limpo e em maiúsculas
    """
    if not texto:
        return ''
    
    # Converter para maiúscula e remover caracteres não permitidos
    return REGEX_CARACTERES_INVALIDOS.sub('', texto.upper())

def validar_texto(texto: str) -> bool:
    """
    Valida se o texto contém apenas caracteres permitidos
    
    Args:
        texto: Texto para validar
        
    Returns:
        bool: True se válido, False se inválido
    """
    if not texto:
        return True  # Texto vazio é válido
    
    return bool(REGEX_TEXTO_VALIDO.match(texto))

def validar_texto_obrigatorio(texto: Optional[str], nome_campo: str) -> str:
    """
    Valida texto obrigatório e retorna limpo
    
    Args:
        texto: Texto para validar
        nome_campo: Nome do campo para mensagem de erro
        
    Returns:
        str: Texto validado e limpo
        
    Raises:
        HTTPException: Se texto inválido ou vazio
    """
    if not texto or not texto.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{nome_campo} é obrigatório"
        )
    
    texto_limpo = limpar_texto(texto)
    
    if not texto_limpo.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{nome_campo} deve conter pelo menos um caractere válido"
        )
    
    if texto != texto_limpo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{nome_campo} deve conter apenas letras maiúsculas, números e caracteres básicos. "
                   f"Recebido: '{texto}', Esperado: '{texto_limpo}'"
        )
    
    return texto_limpo

def validar_texto_opcional(texto: Optional[str], nome_campo: str) -> Optional[str]:
    """
    Valida texto opcional e retorna limpo
    
    Args:
        texto: Texto para validar (pode ser None)
        nome_campo: Nome do campo para mensagem de erro
        
    Returns:
        str | None: Texto validado e limpo ou None
        
    Raises:
        HTTPException: Se texto inválido
    """
    if not texto:
        return None
    
    texto_limpo = limpar_texto(texto)
    
    if texto != texto_limpo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{nome_campo} deve conter apenas letras maiúsculas, números e caracteres básicos. "
                   f"Recebido: '{texto}', Esperado: '{texto_limpo}'"
        )
    
    return texto_limpo if texto_limpo.strip() else None

def validar_nome_completo(nome: str) -> str:
    """
    Valida nome completo
    
    Args:
        nome: Nome para validar
        
    Returns:
        str: Nome validado
        
    Raises:
        HTTPException: Se nome inválido
    """
    nome_limpo = validar_texto_obrigatorio(nome, "Nome completo")
    
    if len(nome_limpo) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome completo deve ter pelo menos 3 caracteres"
        )
    
    if len(nome_limpo) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome completo deve ter no máximo 100 caracteres"
        )
    
    return nome_limpo

def validar_descricao(descricao: Optional[str]) -> Optional[str]:
    """
    Valida descrição
    
    Args:
        descricao: Descrição para validar
        
    Returns:
        str | None: Descrição validada
        
    Raises:
        HTTPException: Se descrição inválida
    """
    if not descricao:
        return None
    
    descricao_limpa = validar_texto_opcional(descricao, "Descrição")
    
    if descricao_limpa and len(descricao_limpa) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição deve ter no máximo 500 caracteres"
        )
    
    return descricao_limpa

def validar_codigo(codigo: str) -> str:
    """
    Valida código (apenas letras maiúsculas, números, hífen e underscore)
    
    Args:
        codigo: Código para validar
        
    Returns:
        str: Código validado
        
    Raises:
        HTTPException: Se código inválido
    """
    if not codigo or not codigo.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código é obrigatório"
        )
    
    codigo_limpo = codigo.upper().strip()
    
    # Para códigos, permitir apenas letras, números, hífen e underscore
    if not re.match(r'^[A-Z0-9_-]+$', codigo_limpo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código deve conter apenas letras maiúsculas, números, hífen e underscore"
        )
    
    return codigo_limpo

def validar_observacao(observacao: Optional[str]) -> Optional[str]:
    """
    Valida observação
    
    Args:
        observacao: Observação para validar
        
    Returns:
        str | None: Observação validada
        
    Raises:
        HTTPException: Se observação inválida
    """
    return validar_texto_opcional(observacao, "Observação")

def aplicar_validacao_automatica(data: dict, campos_texto: list) -> dict:
    """
    Aplica validação automática a múltiplos campos de um dicionário
    
    Args:
        data: Dicionário com dados
        campos_texto: Lista de campos que devem ser validados como texto
        
    Returns:
        dict: Dados com campos validados
        
    Raises:
        HTTPException: Se algum campo for inválido
    """
    data_validada = data.copy()
    
    for campo in campos_texto:
        if campo in data_validada:
            valor = data_validada[campo]
            if valor is not None:
                data_validada[campo] = limpar_texto(str(valor))
                
                # Verificar se houve mudança
                if str(valor) != data_validada[campo]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Campo '{campo}' deve conter apenas letras maiúsculas, números e caracteres básicos. "
                               f"Recebido: '{valor}', Esperado: '{data_validada[campo]}'"
                    )
    
    return data_validada

# Decorador para validação automática de endpoints
def validar_campos_texto(*campos):
    """
    Decorador para validar automaticamente campos de texto em endpoints
    
    Args:
        *campos: Nomes dos campos a serem validados
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Procurar por dicionários nos argumentos
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    args = list(args)
                    args[i] = aplicar_validacao_automatica(arg, campos)
                    args = tuple(args)
            
            # Procurar por dicionários nos kwargs
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    kwargs[key] = aplicar_validacao_automatica(value, campos)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Validadores específicos para diferentes entidades
class ValidadoresEntidade:
    """Validadores específicos para diferentes entidades do sistema"""
    
    @staticmethod
    def setor(data: dict) -> dict:
        """Valida dados de setor"""
        return aplicar_validacao_automatica(data, ['nome', 'descricao'])
    
    @staticmethod
    def usuario(data: dict) -> dict:
        """Valida dados de usuário"""
        return aplicar_validacao_automatica(data, ['nome_completo'])
    
    @staticmethod
    def ordem_servico(data: dict) -> dict:
        """Valida dados de ordem de serviço"""
        return aplicar_validacao_automatica(data, ['observacao'])
    
    @staticmethod
    def apontamento(data: dict) -> dict:
        """Valida dados de apontamento"""
        return aplicar_validacao_automatica(data, ['observacao', 'resultado'])
    
    @staticmethod
    def equipamento(data: dict) -> dict:
        """Valida dados de equipamento"""
        return aplicar_validacao_automatica(data, ['nome', 'descricao', 'modelo'])
    
    @staticmethod
    def cliente(data: dict) -> dict:
        """Valida dados de cliente"""
        return aplicar_validacao_automatica(data, ['nome', 'observacoes'])
