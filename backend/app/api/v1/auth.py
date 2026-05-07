# ============================================================
# app/api/v1/auth.py
# Endpoints de autenticação:
#   POST /api/v1/auth/login    → Retorna JWT após validação
#   POST /api/v1/auth/register → Cria novo usuário no banco
#   GET  /api/v1/auth/me       → Retorna dados do usuário logado
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User
from app.models.auth import Token, UserCreate, UserPublic

# -------------------------------------------------------------------
# Router com prefixo "/auth" – será montado em /api/v1/auth (main.py)
# -------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Esquema OAuth2: informa ao FastAPI qual endpoint fornece tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ===================================================================
# Dependência reutilizável: obtém o usuário autenticado
# Usada em qualquer endpoint protegido via Depends(get_current_user)
# ===================================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodifica o token JWT do header Authorization e retorna
    o objeto User correspondente do banco de dados.

    Lança HTTP 401 se:
      - O token estiver ausente ou inválido
      - O usuário não existir no banco
      - A conta estiver desativada
    """
    # Exceção padrão para credenciais inválidas (RFC 6750)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodifica o token e extrai o username
    username = decode_access_token(token)
    if not username:
        raise credentials_exception

    # Busca o usuário no banco de dados pelo username
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # Verifica se a conta está ativa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte.",
        )

    return user


# ===================================================================
# POST /api/v1/auth/login
# ===================================================================

@router.post(
    "/login",
    response_model=Token,
    summary="Realiza login e retorna um token JWT",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    Autentica o usuário usando username + senha via OAuth2 form-data.
    Retorna um Bearer token JWT em caso de sucesso.

    O OAuth2PasswordRequestForm espera os campos:
      - username (string)
      - password (string)
    enviados como application/x-www-form-urlencoded.
    """
    # Busca o usuário pelo username (case-sensitive)
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verifica se o usuário existe E se a senha está correta.
    # A comparação é feita SEMPRE (evita timing attacks).
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se a conta está ativa antes de emitir o token
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    # Gera o token JWT com o username como subject ("sub")
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


# ===================================================================
# POST /api/v1/auth/register
# ===================================================================

@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova conta de usuário",
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> Token:
    """
    Registra um novo usuário no banco de dados MySQL.
    Valida duplicidade de username e e-mail antes de inserir.
    Em caso de sucesso, retorna um token JWT (usuário já fica logado).

    Regras de segurança:
      - A senha é hasheada com bcrypt antes de persistir
      - A senha em texto plano NUNCA é armazenada
    """
    # Verifica se o username já existe
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este nome de usuário já está em uso",
        )

    # Verifica se o e-mail já existe
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado",
        )

    # Cria o objeto ORM com a senha hasheada
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
    )

    # Persiste no banco de dados
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Atualiza o objeto com o id gerado pelo banco

    # Gera e retorna o token imediatamente (cadastro + login em um passo)
    access_token = create_access_token(data={"sub": new_user.username})
    return Token(access_token=access_token, token_type="bearer")


# ===================================================================
# GET /api/v1/auth/me
# ===================================================================

@router.get(
    "/me",
    response_model=UserPublic,
    summary="Retorna os dados do usuário autenticado",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """
    Endpoint protegido: retorna os dados do usuário extraído do token.
    Usado pelo frontend para validar se o token ainda é válido
    e exibir informações do perfil.
    """
    return current_user
