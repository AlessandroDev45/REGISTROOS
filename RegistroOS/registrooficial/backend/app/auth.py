import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from sqlalchemy.orm import Session
try:
    from .database_models import Usuario # Importa o modelo Usuario
except ImportError:
    from backend.app.database_models import Usuario # CORRECTED # Importa o modelo Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key-if-none-is-set") # Fornece um default explícito
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Níveis de privilegio em ordem decrescente
PRIVILEGE_LEVELS = ["ADMIN", "GESTAO", "PCP", "SUPERVISOR", "USER"]

def verify_password(plain_password, hashed_password):
    print(f"[DEBUG] verify_password - Plain password length: {len(plain_password) if plain_password else 0}")
    print(f"[DEBUG] verify_password - Hashed password preview: {hashed_password[:20] if hashed_password else 'None'}...")
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"[DEBUG] verify_password - Verification result: {result}")
        return result
    except Exception as e:
        print(f"[ERROR] verify_password - Exception during verification: {str(e)}")
        print(f"[ERROR] verify_password - Exception type: {type(e).__name__}")
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, db: Session):
    to_encode = data.copy()

    # Busca o usuário no banco para adicionar privilege_level ao token
    # 'sub' é o user ID
    user_id_str = to_encode.get("sub")
    if not user_id_str:
        raise ValueError("User ID (sub) not found in token data")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise ValueError("Invalid user ID in token data")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user:
        to_encode.update({"privilege_level": user.privilege_level})
    else:
        raise ValueError("User not found for token creation")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # SECRET_KEY é do tipo str, o que é compatível com jwt.encode
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        # SECRET_KEY é do tipo str, o que é compatível com jwt.decode
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Pylance reclamava do tipo de 'key' aqui, mas SECRET_KEY é str.
        # O erro pode ser devido à tipagem estrita do Pylance para a biblioteca 'jose'.
        # Como passamos uma string válira (SECRET_KEY), a chamada é segura.
        return None

def get_current_user_id(token: str):
    payload = decode_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None: # Pylance: Type "Any | None" is not assignable to declared type "str"
        return None
    try:
        return int(user_id) # Garante que o user_id seja um inteiro
    except ValueError:
        return None # Se 'sub' não for um inteiro ou string convertível

def get_current_user_privilege_level(token: str):
    payload = decode_token(token)
    if payload is None:
        return None
    privilege_level = payload.get("privilege_level")
    if privilege_level is None: # Pylance: Type "Any | None" is not assignable to declared type "str"
        return "USER" # Default caso não venha no token, embora deva vir
    return privilege_level

def has_privilege(user_level: str, required_level: str) -> bool:
    """
    Verifica se o nível de privilegio do usuário é suficiente.
    ADMIN > GESTAO > PCP > SUPERVISOR > USER
    """
    if user_level not in PRIVILEGE_LEVELS or required_level not in PRIVILEGE_LEVELS:
        return False # Ou levantar um erro de nível inválido
    return PRIVILEGE_LEVELS.index(user_level) <= PRIVILEGE_LEVELS.index(required_level)

# Funções para obter o usuário completo do banco de dados usando o token
def get_current_user(db: Session, token: str) -> Usuario | None:
    user_id = get_current_user_id(token)
    if user_id is None:
        return None
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_current_active_user(db: Session, token: str) -> Usuario | None:
    current_user = get_current_user(db, token)
    if current_user is None:
        return None
    # A lógica de "ativo" pode ser expandida aqui, por exemplo, verificar um campo is_active
    return current_user
