# Pacote db – expõe os símbolos mais usados para facilitar imports
from app.db.database import Base, SessionLocal, engine, get_db, init_db
from app.db import models  # noqa: F401 – garante que os modelos estejam registrados

__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_db", "models"]
