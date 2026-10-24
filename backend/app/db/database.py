import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Cargar variables de entorno
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("La variable DATABASE_URL no está configurada.")

# Normalizar el prefijo a asyncpg (el motor asíncrono no acepta psycopg2)
for prefijo in ("postgresql+psycopg2://", "postgresql://", "postgres://"):
    if SQLALCHEMY_DATABASE_URL.startswith(prefijo):
        SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://" + SQLALCHEMY_DATABASE_URL[len(prefijo):]
        break

# Usamos create_async_engine en lugar de create_engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Usamos AsyncSession para el manejo asíncrono
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Alias que usa app/core/sync_daemon.py
AsyncSessionLocal = SessionLocal

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()