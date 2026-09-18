import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.db.database import Base
from app.db import models  # noqa: F401  (registra las tablas en Base)
from app.repositories.role_repository import RoleRepositoryImpl
from app.repositories.department_repository import DepartmentRepositoryImpl
from app.repositories.user_repository import UserRepositoryImpl
from app.repositories.cash_repository import CajaRepositoryImpl, TurnoCajaRepositoryImpl


class TestUnitOfWork:
    """UoW ligero para las pruebas (mismo contrato que app.api.deps.UnitOfWork)."""

    def __init__(self, db):
        self.db = db
        self.roles = RoleRepositoryImpl(db)
        self.departments = DepartmentRepositoryImpl(db)
        self.users = UserRepositoryImpl(db)
        self.cajas = CajaRepositoryImpl(db)
        self.turnos = TurnoCajaRepositoryImpl(db)

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()


@pytest_asyncio.fixture
async def db_session():
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await test_engine.dispose()


@pytest_asyncio.fixture
async def uow(db_session):
    return TestUnitOfWork(db_session)