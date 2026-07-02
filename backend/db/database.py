from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = "sqlite+aiosqlite:///database.db"

engine = create_async_engine( DATABASE_URL)

SessionLocal = async_sessionmaker(
   engine,
   expire_on_commit=False,
)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()