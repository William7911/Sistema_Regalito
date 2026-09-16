from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.db.database import get_db
from app.db.models import Usuario
from app.core.config import settings
from app.repositories.category_repository import CategoryRepositoryImpl
from app.repositories.product_repository import ProductRepositoryImpl
from app.repositories.role_repository import RoleRepositoryImpl
from app.repositories.department_repository import DepartmentRepositoryImpl
from app.repositories.user_repository import UserRepositoryImpl
from app.services.category_service import ConcreteCategoryService
from app.services.product_service import ConcreteProductService
from app.services.catalogo_service import ConcreteCatalogoService
from app.services.role_service import ConcreteRoleService
from app.services.department_service import ConcreteDepartmentService
from app.services.user_service import ConcreteUserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class UnitOfWork:
    """Agrupa la transacción y expone los repositorios del módulo de Usuarios.

    Los repositorios NO hacen commit: el UoW decide cuándo persistir
    (`commit()`) o descartar (`rollback()`) la transacción completa.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()

    @property
    def roles(self):
        return RoleRepositoryImpl(self.db)

    @property
    def departments(self):
        return DepartmentRepositoryImpl(self.db)

    @property
    def users(self):
        return UserRepositoryImpl(self.db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Usuario).where(Usuario.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


def get_category_service(db: AsyncSession = Depends(get_db)) -> ConcreteCategoryService:
    repository = CategoryRepositoryImpl(db)
    return ConcreteCategoryService(repository)


def get_product_service(db: AsyncSession = Depends(get_db)) -> ConcreteProductService:
    product_repository = ProductRepositoryImpl(db)
    return ConcreteProductService(product_repository)


def get_catalogo_service(db: AsyncSession = Depends(get_db)) -> ConcreteCatalogoService:
    product_repository = ProductRepositoryImpl(db)
    return ConcreteCatalogoService(db, product_repository)


def get_role_service(db: AsyncSession = Depends(get_db)) -> ConcreteRoleService:
    return ConcreteRoleService(UnitOfWork(db))


def get_department_service(db: AsyncSession = Depends(get_db)) -> ConcreteDepartmentService:
    return ConcreteDepartmentService(UnitOfWork(db))


def get_user_service(db: AsyncSession = Depends(get_db)) -> ConcreteUserService:
    return ConcreteUserService(UnitOfWork(db))