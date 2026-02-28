from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine — used by FastAPI at runtime
engine = create_async_engine(DATABASE_URL, echo=False)

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