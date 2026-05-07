# ============================================================
# app/models/auth.py
# Schemas Pydantic para validação e serialização de dados
# relacionados à autenticação e usuários.
# Esses schemas NÃO são modelos de banco de dados — para isso
# veja app/db/models.py.
# ============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator


# -----------------------------------------------------------------
# Schemas de entrada (request body)
# -----------------------------------------------------------------

class UserCreate(BaseModel):
    """
    Dados necessários para criar uma nova conta (cadastro).
    Todos os campos são obrigatórios e passam por validação.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",  # Apenas letras, números e underscore
        description="Nome de usuário único (3–50 chars, sem espaços)",
    )
    email: EmailStr = Field(
        ...,
        description="E-mail válido — usado para recuperação de senha futura",
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Senha com no mínimo 6 caracteres",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Validação básica de força de senha:
        - Pelo menos 6 caracteres (já garantido pelo min_length)
        - Deve conter pelo menos um dígito
        """
        if not any(char.isdigit() for char in v):
            raise ValueError("A senha deve conter pelo menos um número")
        return v


class UserLogin(BaseModel):
    """
    Dados para autenticação via JSON body.
    O endpoint OAuth2 padrão usa form-data, mas este schema
    é usado em outras integrações.
    """
    username: str
    password: str


# -----------------------------------------------------------------
# Schemas de saída (response body)
# -----------------------------------------------------------------

class Token(BaseModel):
    """
    Resposta retornada ao cliente após login bem-sucedido.
    O access_token deve ser enviado em requisições protegidas
    no header: Authorization: Bearer <token>
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Dados extraídos do payload do JWT após decodificação.
    Usado internamente para identificar o usuário autenticado.
    """
    username: str | None = None


class UserPublic(BaseModel):
    """
    Dados públicos do usuário — retornados na API.
    NUNCA inclua hashed_password ou dados sensíveis aqui.
    """
    id: int
    username: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}  # Permite criar a partir de objetos ORM
