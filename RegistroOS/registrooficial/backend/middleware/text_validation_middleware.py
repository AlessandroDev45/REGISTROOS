"""
Middleware de Validação de Texto - RegistroOS
=============================================

Middleware que aplica automaticamente validação de texto maiúsculo
a todas as requisições que contêm dados de formulário.
"""

import json
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from RegistroOS.registrooficial.backend.utils.text_validators import limpar_texto, validar_texto

class TextValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida automaticamente campos de texto em requisições
    """
    
    # Campos que devem ser validados como texto
    CAMPOS_TEXTO = {
        'nome', 'nome_completo', 'descricao', 'observacao', 'resultado',
        'modelo', 'observacoes', 'titulo', 'comentario', 'detalhes',
        'motivo', 'justificativa', 'anotacoes'
    }
    
    # Endpoints que devem ter validação aplicada
    ENDPOINTS_VALIDACAO = {
        '/api/usuarios', '/api/setores', '/api/equipamentos',
        '/api/clientes', '/api/os', '/api/apontamentos'
    }
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição aplicando validação de texto quando necessário
        """
        if not self.enabled:
            return await call_next(request)
        
        # Verificar se é um endpoint que precisa de validação
        if not self._deve_validar_endpoint(request.url.path):
            return await call_next(request)
        
        # Verificar se é um método que modifica dados
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return await call_next(request)
        
        try:
            # Processar body da requisição
            body = await request.body()
            if not body:
                return await call_next(request)
            
            # Tentar decodificar JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Se não for JSON válido, prosseguir sem validação
                return await call_next(request)
            
            # Aplicar validação
            data_validada, erros = self._validar_dados(data)
            
            if erros:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Dados inválidos encontrados",
                        "errors": erros
                    }
                )
            
            # Criar nova requisição com dados validados
            if data_validada != data:
                novo_body = json.dumps(data_validada).encode('utf-8')
                request._body = novo_body
                
                # Atualizar headers se necessário
                request.headers.__dict__['_list'] = [
                    (k, v) for k, v in request.headers.items()
                    if k.lower() != 'content-length'
                ]
                request.headers.__dict__['_list'].append(
                    (b'content-length', str(len(novo_body)).encode())
                )
            
        except Exception as e:
            # Em caso de erro na validação, prosseguir sem validação
            print(f"Erro no middleware de validação: {e}")
        
        return await call_next(request)
    
    def _deve_validar_endpoint(self, path: str) -> bool:
        """
        Verifica se o endpoint deve ter validação aplicada
        """
        return any(endpoint in path for endpoint in self.ENDPOINTS_VALIDACAO)
    
    def _validar_dados(self, data: Any) -> tuple[Any, list]:
        """
        Valida dados recursivamente
        
        Returns:
            tuple: (dados_validados, lista_de_erros)
        """
        erros = []
        
        if isinstance(data, dict):
            return self._validar_dict(data, erros)
        elif isinstance(data, list):
            return self._validar_list(data, erros)
        else:
            return data, erros
    
    def _validar_dict(self, data: dict, erros: list) -> tuple[dict, list]:
        """
        Valida um dicionário
        """
        data_validada = {}
        
        for chave, valor in data.items():
            if isinstance(valor, str) and chave.lower() in self.CAMPOS_TEXTO:
                # Validar campo de texto
                valor_original = valor
                valor_limpo = limpar_texto(valor)
                
                if valor_original != valor_limpo:
                    erros.append({
                        "campo": chave,
                        "valor_original": valor_original,
                        "valor_esperado": valor_limpo,
                        "mensagem": f"Campo '{chave}' deve conter apenas letras maiúsculas, números e caracteres básicos"
                    })
                
                data_validada[chave] = valor_limpo
                
            elif isinstance(valor, (dict, list)):
                # Validar recursivamente
                valor_validado, erros_filho = self._validar_dados(valor)
                erros.extend(erros_filho)
                data_validada[chave] = valor_validado
                
            else:
                # Manter valor como está
                data_validada[chave] = valor
        
        return data_validada, erros
    
    def _validar_list(self, data: list, erros: list) -> tuple[list, list]:
        """
        Valida uma lista
        """
        data_validada = []
        
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                item_validado, erros_item = self._validar_dados(item)
                erros.extend(erros_item)
                data_validada.append(item_validado)
            else:
                data_validada.append(item)
        
        return data_validada, erros

# Função para adicionar o middleware à aplicação
def add_text_validation_middleware(app, enabled: bool = True):
    """
    Adiciona o middleware de validação de texto à aplicação FastAPI
    
    Args:
        app: Instância da aplicação FastAPI
        enabled: Se o middleware deve estar ativo
    """
    app.add_middleware(TextValidationMiddleware, enabled=enabled)

# Decorador para validação manual em endpoints específicos
def validate_text_fields(*campos):
    """
    Decorador para validar campos de texto específicos
    
    Args:
        *campos: Nomes dos campos a serem validados
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Procurar por dados nos argumentos
            for i, arg in enumerate(args):
                if hasattr(arg, '__dict__'):
                    # Validar atributos do objeto
                    for campo in campos:
                        if hasattr(arg, campo):
                            valor = getattr(arg, campo)
                            if isinstance(valor, str):
                                valor_limpo = limpar_texto(valor)
                                if valor != valor_limpo:
                                    from fastapi import HTTPException, status
                                    raise HTTPException(
                                        status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Campo '{campo}' deve conter apenas letras maiúsculas, números e caracteres básicos. "
                                               f"Recebido: '{valor}', Esperado: '{valor_limpo}'"
                                    )
                                setattr(arg, campo, valor_limpo)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Classe para validação de modelos Pydantic
class TextValidationMixin:
    """
    Mixin para adicionar validação de texto a modelos Pydantic
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_text_fields
    
    @classmethod
    def validate_text_fields(cls, v):
        """
        Valida campos de texto do modelo
        """
        if isinstance(v, dict):
            for campo, valor in v.items():
                if isinstance(valor, str) and campo.lower() in TextValidationMiddleware.CAMPOS_TEXTO:
                    valor_limpo = limpar_texto(valor)
                    if valor != valor_limpo:
                        from fastapi import HTTPException, status
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Campo '{campo}' deve conter apenas letras maiúsculas, números e caracteres básicos. "
                                   f"Recebido: '{valor}', Esperado: '{valor_limpo}'"
                        )
                    v[campo] = valor_limpo
        
        return v
