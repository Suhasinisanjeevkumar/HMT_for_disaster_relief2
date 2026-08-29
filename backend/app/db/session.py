from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# check_same_thread=False is needed for SQLite specifically, since FastAPI
# can hand a request to a different thread than the one that opened the
# connection -- harmless for our single-process dev setup. Not needed (and
# not applied) for a Postgres DATABASE_URL.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
