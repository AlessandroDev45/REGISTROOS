from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import datetime

from app.database_models import Usuario, Setor, Departamento
from config.database_config import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.auth import create_access_token, verify_password, get_password_hash
from utils.user_utils import check_development_access

router = APIRouter()

# Modelos Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Endpoint para login de usuários
    """
    # Buscar usuário por nome de usuário ou email
    user = db.query(Usuario).filter(
        (Usuario.nome_usuario == login_data.username) |
        (Usuario.email == login_data.username)
    ).first()

    if not user or not verify_password(login_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não aprovado pelo administrador"
        )

    # Criar token de acesso
    access_token = create_access_token(data={"sub": user.nome_usuario})

    # Definir cookie httpOnly
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,  # 30 minutos
        expires=1800,
        samesite="lax",
        secure=False  # Para desenvolvimento local
    )

    # Extrair primeiro nome do usuário
    primeiro_nome = user.nome_completo.split(' ')[0] if user.nome_completo else 'Usuário'

    # Buscar nomes do setor e departamento com fallback para campos string
    setor_nome = user.setor  # Campo string como fallback
    departamento_nome = user.departamento  # Campo string como fallback

    try:
        if user.id_setor:
            setor_obj = db.query(Setor).filter(Setor.id == user.id_setor).first()
            if setor_obj:
                setor_nome = setor_obj.nome

        if user.id_departamento:
            departamento_obj = db.query(Departamento).filter(Departamento.id == user.id_departamento).first()
            if departamento_obj:
                departamento_nome = departamento_obj.nome_tipo
    except Exception as e:
        print(f"[WARNING] Erro ao buscar relacionamentos de setor/departamento: {e}")
        # Usar campos string como fallback

    return {
        "message": "Login realizado com sucesso",
        "user": {
            "id": user.id,
            "nome_completo": user.nome_completo,
            "primeiro_nome": primeiro_nome,
            "email": user.email,
            "privilege_level": user.privilege_level,
            "id_setor": user.id_setor,
            "id_departamento": user.id_departamento,
            "setor": setor_nome,
            "departamento": departamento_nome,
            "trabalha_producao": user.trabalha_producao,
            "primeiro_login": user.primeiro_login
        },
        "requires_password_change": user.primeiro_login
    }

class UserRegister(BaseModel):
    primeiro_nome: str
    sobrenome: str
    email: EmailStr
    password: str
    nome_usuario: str
    matricula: str = ""
    cargo: str = ""
    departamento: str  # This is not directly saved to Usuario table
    setor_de_trabalho: str
    trabalha_producao: bool = False

class ChangePasswordRequest(BaseModel):
    senha_atual: str
    nova_senha: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Endpoint para cadastro de novos usuários.
    Cria um novo usuário com is_approved=False e privilege_level='USER'.
    """
    # Verificar se email já existe
    db_user_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email já está em uso.")

    # Verificar se nome de usuário já existe
    db_user_username = db.query(Usuario).filter(Usuario.nome_usuario == user_data.nome_usuario).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Nome de usuário já está em uso.")

    # Hash da senha
    hashed_password = get_password_hash(user_data.password)

    # Preparar dados para o banco de dados
    novo_usuario_data = {
        "nome_completo": f"{user_data.primeiro_nome} {user_data.sobrenome}",
        "nome_usuario": user_data.nome_usuario,
        "email": user_data.email,
        "senha_hash": hashed_password,
        "matricula": user_data.matricula,
        "id_setor": 1,  # Padrão - ajustar conforme necessário
        "id_departamento": 1,  # Padrão - ajustar conforme necessário
        "cargo": user_data.cargo,
        "trabalha_producao": user_data.trabalha_producao,
        "privilege_level": "USER",  # Padrão
        "is_approved": False,       # Precisa de aprovação
        "data_criacao": datetime.datetime.utcnow(),
        "data_ultima_atualizacao": datetime.datetime.utcnow()
    }

    try:
        novo_usuario = Usuario(**novo_usuario_data)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return {"message": "Usuário criado com sucesso. Aguardando aprovação de um administrador."}
    except Exception as e:
        db.rollback()
        # Logar o erro e.g. print(f"Erro ao criar usuário: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao criar usuário: {str(e)}")

@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint for user authentication.
    Receives username (email) and password, sets HttpOnly cookie with JWT token if credentials are valid.
    """
    print(f"[DEBUG] login_for_access_token - Attempting login for: {form_data.username}")
    print(f"[DEBUG] login_for_access_token - Password length: {len(form_data.password) if form_data.password else 0}")

    # Debug adicional - verificar conexão do banco
    try:
        total_users = db.query(Usuario).count()
        print(f"[DEBUG] login_for_access_token - Total users in database: {total_users}")

        # Buscar todos os emails para debug
        all_emails = db.query(Usuario.email).limit(5).all()
        print(f"[DEBUG] login_for_access_token - Sample emails: {[email[0] for email in all_emails]}")

    except Exception as e:
        print(f"[ERROR] login_for_access_token - Database connection error: {e}")

    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    print(f"[DEBUG] login_for_access_token - User found: {user is not None}")

    # Debug adicional - buscar com LIKE para ver se há problema de encoding
    if not user:
        similar_users = db.query(Usuario).filter(Usuario.email.like(f"%{form_data.username.split('@')[0]}%")).all()
        print(f"[DEBUG] login_for_access_token - Similar users found: {len(similar_users)}")
        for similar in similar_users:
            print(f"[DEBUG] login_for_access_token - Similar email: '{similar.email}'")
    if user:
        print(f"[DEBUG] login_for_access_token - User ID: {user.id}, Email: {user.email}")
        print(f"[DEBUG] login_for_access_token - User approved: {user.is_approved}")
        print(f"[DEBUG] login_for_access_token - User privilege: {user.privilege_level}")

    if not user:
        print(f"[ERROR] login_for_access_token - User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valid = verify_password(form_data.password, user.senha_hash)
    print(f"[DEBUG] login_for_access_token - Password verification result: {password_valid}")

    if not password_valid:
        print(f"[ERROR] login_for_access_token - Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_approved is False:  # Correção: Comparar explicitamente com False
        print(f"[ERROR] login_for_access_token - User not approved: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário não aprovada. Por favor, aguarde a aprovação de um administrador.",
        )

    print(f"[DEBUG] login_for_access_token - Creating access token for user ID: {user.id}")
    access_token = create_access_token(data={"sub": str(user.id)}, db=db)
    print(f"[DEBUG] login_for_access_token - Token created successfully")

    # Set HttpOnly cookie with the JWT token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,  # 1 hour
        expires=None,
        path="/",
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )

    # Extrair primeiro nome do usuário
    primeiro_nome = user.nome_completo.split(' ')[0] if user.nome_completo else 'Usuário'

    # Buscar nomes do setor e departamento
    setor_nome = None
    departamento_nome = None

    if user.id_setor:
        setor_obj = db.query(Setor).filter(Setor.id == user.id_setor).first()
        if setor_obj:
            setor_nome = setor_obj.nome

    if user.id_departamento:
        departamento_obj = db.query(Departamento).filter(Departamento.id == user.id_departamento).first()
        if departamento_obj:
            departamento_nome = departamento_obj.nome_tipo

    result = {
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nome_completo": user.nome_completo,
            "primeiro_nome": primeiro_nome,
            "privilege_level": user.privilege_level,
            "id_setor": user.id_setor,
            "id_departamento": user.id_departamento,
            "setor": setor_nome,
            "departamento": departamento_nome,
            "trabalha_producao": user.trabalha_producao,
            "primeiro_login": user.primeiro_login
        },
        "requires_password_change": user.primeiro_login
    }
    print(f"[DEBUG] login_for_access_token - Login successful for: {form_data.username}")
    return result

@router.post("/logout")
async def logout(response: Response):
    """Endpoint to logout user by clearing the HttpOnly cookie"""
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    return {"message": "Logged out successfully"}

@router.get("/debug-users")
async def debug_users(db: Session = Depends(get_db)):
    """
    Endpoint temporário para debug de usuários
    """
    try:
        print(f"[DEBUG] debug_users - Iniciando debug...")

        # Contar usuários
        total = db.query(Usuario).count()
        print(f"[DEBUG] debug_users - Total usuarios: {total}")

        # Buscar todos os emails
        usuarios = db.query(Usuario.email, Usuario.nome_completo).all()
        emails = [{"email": u[0], "nome": u[1]} for u in usuarios]

        print(f"[DEBUG] debug_users - Emails encontrados: {len(emails)}")

        return {
            "total_usuarios": total,
            "usuarios": emails,
            "database_path": db.bind.url,
            "status": "success"
        }

    except Exception as e:
        print(f"[ERROR] debug_users - Erro: {e}")
        return {
            "error": str(e),
            "total_usuarios": 0,
            "usuarios": [],
            "status": "error"
        }

@router.post("/test-login/{user_email}")
async def test_login(user_email: str, response: Response, db: Session = Depends(get_db)):
    """
    Endpoint temporário para login automático durante testes
    """
    print(f"[DEBUG] test_login - Attempting auto-login for: {user_email}")

    user = db.query(Usuario).filter(Usuario.email == user_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário não encontrado: {user_email}"
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não aprovado"
        )

    print(f"[DEBUG] test_login - Creating access token for user: {user.nome_completo} (ID: {user.id})")
    access_token = create_access_token(data={"sub": str(user.id)}, db=db)

    # Set HttpOnly cookie with the JWT token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=3600  # 1 hour
    )

    return {
        "message": f"Login automático realizado com sucesso para {user.nome_completo}",
        "user": {
            "id": user.id,
            "nome_completo": user.nome_completo,
            "email": user.email,
            "privilege_level": user.privilege_level,
            "setor": user.setor,
            "departamento": user.departamento,
            "id_setor": user.id_setor,
            "id_departamento": user.id_departamento,
            "trabalha_producao": user.trabalha_producao,
            "primeiro_login": user.primeiro_login
        }
    }

@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para o usuário alterar sua própria senha
    """
    try:
        # Verificar se a senha atual está correta
        if not verify_password(password_data.senha_atual, current_user.senha_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")

        # Atualizar a senha
        current_user.senha_hash = get_password_hash(password_data.nova_senha)
        current_user.primeiro_login = False  # Marca que não é mais primeiro login
        current_user.data_ultima_atualizacao = datetime.datetime.utcnow()

        db.commit()

        return {"message": "Senha alterada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar senha: {str(e)}")

@router.get("/me")
async def read_me(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Endpoint para obter informações do usuário atual (para depuração)"""
    # Extrair primeiro nome do usuário
    primeiro_nome = current_user.nome_completo.split(' ')[0] if current_user.nome_completo else 'Usuário'

    # Buscar nomes do setor e departamento
    setor_nome = None
    departamento_nome = None

    if current_user.id_setor:
        setor_obj = db.query(Setor).filter(Setor.id == current_user.id_setor).first()
        if setor_obj:
            setor_nome = setor_obj.nome

    if current_user.id_departamento:
        departamento_obj = db.query(Departamento).filter(Departamento.id == current_user.id_departamento).first()
        if departamento_obj:
            departamento_nome = departamento_obj.nome_tipo

    user_data_to_return = {
        "id": current_user.id,
        "nome_completo": current_user.nome_completo,
        "primeiro_nome": primeiro_nome,
        "email": current_user.email,
        "privilege_level": current_user.privilege_level,
        "is_approved": current_user.is_approved,
        "id_setor": current_user.id_setor,
        "id_departamento": current_user.id_departamento,
        "setor": setor_nome,
        "departamento": departamento_nome,
        "trabalha_producao": current_user.trabalha_producao
    }
    print(f"[DEBUG /me] Endpoint /me foi chamado para user ID: {current_user.id} ({current_user.email})")
    print(f"[DEBUG /me] Dados do usuário do objeto current_user: {user_data_to_return}")
    return user_data_to_return

@router.get("/check-development-access/{sector}")
async def check_development_access_endpoint(
    sector: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Check if user can access development page for a specific sector"""
    print(f"[INFO] check_development_access_endpoint - Request received for sector: {sector}")
    print(f"[INFO] check_development_access_endpoint - User ID: {getattr(current_user, 'id', 'N/A')}")
    print(f"[INFO] check_development_access_endpoint - User email: {getattr(current_user, 'email', 'N/A')}")
    print(f"[INFO] check_development_access_endpoint - User privilege: {getattr(current_user, 'privilege_level', 'N/A')}")
    print(f"[INFO] check_development_access_endpoint - User setor: {getattr(current_user, 'setor', 'N/A')}")

    try:
        print(f"[DEBUG] check_development_access_endpoint - Step 1: Calling check_development_access function")
        has_access = check_development_access(current_user, sector)
        print(f"[DEBUG] check_development_access_endpoint - Step 2: check_development_access returned: {has_access}")

        result = {
            "has_access": has_access,
            "user_sector": getattr(current_user, 'setor', ''),
            "user_privilege": getattr(current_user, 'privilege_level', 'USER'),
            "requested_sector": sector
        }
        print(f"[DEBUG] check_development_access_endpoint - Step 3: Constructed result object")
        print(f"[INFO] check_development_access_endpoint - Success, returning result: {result}")
        return result
    except Exception as e:
        print(f"[ERROR] check_development_access_endpoint - An exception occurred: {str(e)}")
        print(f"[ERROR] check_development_access_endpoint - Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] check_development_access_endpoint - Traceback:")
        print(traceback.format_exc())
        error_msg = f"Erro ao verificar acesso: {str(e)}"
        print(f"[DEBUG] check_development_access_endpoint - About to raise HTTPException with message: {error_msg}")
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )
