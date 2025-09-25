from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database_models import Usuario
from app.auth import SECRET_KEY, ALGORITHM, get_current_user as get_authenticated_user
from config.database_config import get_db

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Try to get authentication token from cookies
    token = request.cookies.get("access_token")

    if token:
        try:
            # Remove "Bearer " prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Decode the token and get user from database
            user = get_authenticated_user(db, token)
            if user:
                print(f"[DEBUG] get_current_user - Returning authenticated user: {user.nome_completo} (ID: {user.id}, Privilege: {user.privilege_level}, Trabalha Produção: {user.trabalha_producao})")
                return user
        except Exception as e:
            print(f"[DEBUG] get_current_user - Token validation failed: {str(e)}")

    # Se não há token válido, retornar erro de autenticação
    print(f"[DEBUG] get_current_user - No valid token found, authentication required")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_admin_user(current_user: Usuario = Depends(get_current_user)):
    if current_user.privilege_level != 'ADMIN':  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this resource",
        )
    return current_user