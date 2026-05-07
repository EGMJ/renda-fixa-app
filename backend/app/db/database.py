# ============================================================
# app/db/database.py
# Responsável por:
#   - Criar o engine SQLAlchemy apontando para o MySQL
#   - Fornecer SessionLocal (fábrica de sessões)
#   - Exportar Base (classe base para os modelos ORM)
#   - Expor get_db() como dependência injetável no FastAPI
# ============================================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

# Carrega as variáveis definidas no arquivo .env (se existir)
load_dotenv()

# -----------------------------------------------------------------
# Montagem da URL de conexão MySQL
# Formato: mysql+mysqlconnector://usuario:senha@host:porta/banco
# -----------------------------------------------------------------
MYSQL_USER     = os.getenv("MYSQL_USER",     "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_HOST     = os.getenv("MYSQL_HOST",     "localhost")
MYSQL_PORT     = os.getenv("MYSQL_PORT",     "3306")
MYSQL_DB       = os.getenv("MYSQL_DB",       "renda_fixa")

DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# -----------------------------------------------------------------
# Engine SQLAlchemy
#   pool_pre_ping=True → testa a conexão antes de reutilizá-la
#   pool_recycle=3600  → recicla conexões a cada 1h (evita timeout)
# -----------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Altere para True durante desenvolvimento para ver os SQLs
)

# Fábrica de sessões: cada requisição HTTP cria uma sessão independente
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -----------------------------------------------------------------
# Classe base para todos os modelos ORM do projeto.
# Todos os modelos herdam desta classe para serem reconhecidos
# pelo SQLAlchemy ao criar as tabelas.
# -----------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------------------------------------------
# Dependência injetável via FastAPI (Depends)
# Garante que a sessão seja sempre fechada após cada requisição,
# mesmo em caso de erro (bloco finally).
# -----------------------------------------------------------------
def get_db():
    """
    Gerador que abre uma sessão de banco de dados para a requisição
    e a fecha automaticamente ao final, mesmo em caso de exceção.

    Uso no FastAPI:
        @router.get("/exemplo")
        def exemplo(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------------------
# Utilitário: inicializa o banco de dados criando todas as tabelas
# definidas nos modelos que herdam de Base.
# Chamado no lifespan do app (main.py).
# -----------------------------------------------------------------
def init_db() -> None:
    """
    Cria todas as tabelas no banco MySQL caso ainda não existam.
    Importa os modelos aqui para que o Base os "conheça" antes
    do create_all ser executado.
    """
    # Importação local para evitar importação circular
    from app.db import models  # noqa: F401 – garante registro no metadata

    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        # Log de erro sem interromper o startup (banco pode estar offline)
        import logging
        logging.error(f"[DB] Falha ao criar tabelas: {exc}")
