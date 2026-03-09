from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine — used by FastAPI at runtime
# pool_size: persistent connections kept open
# max_overflow: extra connections allowed under burst load
# pool_timeout: seconds to wait for a free connection before raising
# pool_pre_ping: checks connection health before using it
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)

# Session factory — creates individual DB sessions per request
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class that all models will inherit from
class Base(DeclarativeBase):
    pass

# Dependency — FastAPI routes will call this to get a DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()