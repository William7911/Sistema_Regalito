from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Usuario, Rol
from app.interfaces.repositories import UserRepository

_USER_LOADS = (
    selectinload(Usuario.rol),
)


class UserRepositoryImpl(UserRepository):
    """Repositorio de Usuarios (modelo Usuario). Carga ansiosa de `rol`
    para evitar el error MissingGreenlet. No hace commit: el Unit of Work
    controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).options(*_USER_LOADS).where(Usuario.id_usuario == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        result = await self.db.execute(select(Usuario).where(Usuario.username == username))
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        name: Optional[str],
        is_active: Optional[bool],
        role_id: Optional[int],
        created_from=None,
        created_to=None,
    ):
        conditions = []
        if name:
            conditions.append(Usuario.nombre_completo.ilike(f"%{name}%"))
        if is_active is not None:
            estado = "Activo" if is_active else "Inactivo"
            conditions.append(Usuario.estado == estado)
        if role_id is not None:
            conditions.append(Usuario.id_rol == role_id)
        if created_from is not None:
            conditions.append(Usuario.fecha_creacion >= created_from)
        if created_to is not None:
            conditions.append(Usuario.fecha_creacion <= created_to)
        return conditions

    _SORTABLE = {
        "id_usuario": Usuario.id_usuario,
        "nombre_completo": Usuario.nombre_completo,
        "username": Usuario.username,
        "rol": Rol.nombre,
        "estado": Usuario.estado,
        "fecha_creacion": Usuario.fecha_creacion,
    }

    async def search(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        created_from=None,
        created_to=None,
        sort_by: Optional[str] = None,
        sort_dir: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Usuario]:
        conditions = self._build_filters(name, is_active, role_id, created_from, created_to)
        stmt = select(Usuario).options(*_USER_LOADS)
        if conditions:
            stmt = stmt.where(*conditions)
        if sort_by == "rol":
            stmt = stmt.join(Usuario.rol)
        column = self._SORTABLE.get(sort_by, Usuario.nombre_completo)
        if sort_dir == "desc":
            column = column.desc()
        stmt = stmt.order_by(column).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        created_from=None,
        created_to=None,
    ) -> int:
        conditions = self._build_filters(name, is_active, role_id, created_from, created_to)
        stmt = select(func.count()).select_from(Usuario)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, user: Usuario) -> Usuario:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: Usuario) -> Usuario:
        await self.db.flush()
        await self.db.refresh(user)
        return user