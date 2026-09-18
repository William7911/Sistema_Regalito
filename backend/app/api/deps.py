from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.db.models import Usuario, TurnoCaja, RolPermiso, Permiso
from app.core.config import settings
from app.repositories.category_repository import CategoryRepositoryImpl
from app.repositories.product_repository import ProductRepositoryImpl
from app.repositories.role_repository import RoleRepositoryImpl
from app.repositories.department_repository import DepartmentRepositoryImpl
from app.repositories.user_repository import UserRepositoryImpl
from app.repositories.cash_repository import CajaRepositoryImpl, TurnoCajaRepositoryImpl
from app.repositories.merma_repository import MermaRepositoryImpl
from app.repositories.sale_repository import SaleRepositoryImpl
from app.services.category_service import ConcreteCategoryService
from app.services.product_service import ConcreteProductService
from app.services.catalogo_service import ConcreteCatalogoService
from app.services.role_service import ConcreteRoleService
from app.services.department_service import ConcreteDepartmentService
from app.services.user_service import ConcreteUserService
from app.services.cash_service import ConcreteCashService
from app.services.merma_service import ConcreteMermaService
from app.services.sale_service import ConcreteSaleService

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

    @property
    def cajas(self):
        return CajaRepositoryImpl(self.db)

    @property
    def turnos(self):
        return TurnoCajaRepositoryImpl(self.db)

    @property
    def mermas(self):
        return MermaRepositoryImpl(self.db)

    @property
    def sales(self):
        return SaleRepositoryImpl(self.db)


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

    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.username == username)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


from app.core.permissions import check_user_permission


def require_permission(permission_code: str):
    """Dependencia de FastAPI que valida si el usuario autenticado tiene el permiso especificado."""
    async def permission_dependency(
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Usuario:
        allowed = await check_user_permission(db, current_user, permission_code)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para realizar esta acción ({permission_code})",
            )
        return current_user

    return permission_dependency


async def require_admin(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """Dependencia para módulos administrativos sin permiso granular (Usuarios, Roles, Departamentos)."""
    if not current_user.rol or current_user.rol.nombre != "Administradora":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido: requiere rol de Administradora",
        )
    return current_user


async def get_current_active_shift(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TurnoCaja:
    """Valida que el usuario tenga un turno de caja abierto (RF01 - Bloqueo de POS sin turno).
    Si no tiene fondo inicial registrado, rechaza la operación con 403 Forbidden."""
    uow = UnitOfWork(db)
    active = await uow.turnos.get_active_by_user(current_user.id_usuario)
    if not active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe registrar el fondo inicial antes de vender",
        )
    return active


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


def get_cash_service(db: AsyncSession = Depends(get_db)) -> ConcreteCashService:
    return ConcreteCashService(UnitOfWork(db))


def get_merma_service(db: AsyncSession = Depends(get_db)) -> ConcreteMermaService:
    return ConcreteMermaService(UnitOfWork(db))


def get_sale_service(db: AsyncSession = Depends(get_db)) -> ConcreteSaleService:
    return ConcreteSaleService(UnitOfWork(db))