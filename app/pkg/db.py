from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_config, Config


def build_dsn(cfg: Config) -> str:
    return (
        f"mysql+pymysql://{cfg.db_user}:{cfg.db_password}"
        f"@{cfg.db_host}:{cfg.db_port}/{cfg.db_name}"
    )


configs = get_config()

engine = create_engine(
    build_dsn(configs),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    return SessionLocal()