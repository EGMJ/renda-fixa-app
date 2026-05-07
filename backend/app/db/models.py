# ============================================================
# app/db/models.py
# Define os modelos ORM (tabelas) do banco de dados MySQL.
# Cada classe representa uma tabela; cada atributo representa
# uma coluna.
# ============================================================

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.database import Base


class User(Base):
    """
    Tabela `users` – armazena os usuários da aplicação.

    Colunas:
        id           – Chave primária auto-incremental.
        username     – Nome de usuário único (usado no login).
        email        – E-mail único do usuário.
        hashed_password – Hash bcrypt da senha (NUNCA armazene senha em texto claro).
        is_active    – Se False, a conta está desativada (soft-delete / banimento).
        created_at   – Timestamp de criação do registro (preenchido automaticamente).
    """

    __tablename__ = "users"

    # --- Chave primária ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # --- Identificadores únicos ---
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome de usuário único para login",
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="E-mail único do usuário",
    )

    # --- Segurança ---
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Hash bcrypt da senha — nunca armazene senha em texto plano",
    )

    # --- Status da conta ---
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="False = conta desativada",
    )

    # --- Auditoria ---
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Data/hora UTC de criação do usuário",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"
