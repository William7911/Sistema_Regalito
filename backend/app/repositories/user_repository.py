from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import User
from app.interfaces.repositories import UserRepository

_USER_LOADS = (
    selectinload(User.role),
    selectinload(User.department),
)


class UserRepositoryImpl(UserRepository):
    """Repositorio de Usuarios. No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).options(*_USER_LOADS).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.code == code))
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        name: Optional[str],
        lastname: Optional[str],
        code: Optional[str],
        is_active: Optional[bool],
        role_id: Optional[int],
        department_id: Optional[int],
        created_from: Optional[str],
        created_to: Optional[str],
    ):
        conditions = []
        if name:
            conditions.append(
                or_(User.name.ilike(f"%{name}%"), User.lastname.ilike(f"%{name}%"))
            )
        if lastname:
            conditions.append(User.lastname.ilike(f"%{lastname}%"))
        if code:
            conditions.append(User.code.ilike(f"%{code}%"))
        if is_active is not None:
            conditions.append(User.is_active.is_(is_active))
        if role_id is not None:
            conditions.append(User.role_id == role_id)
        if department_id is not None:
            conditions.append(User.department_id == department_id)
        if created_from:
            conditions.append(User.created_at >= created_from)
        if created_to:
            conditions.append(User.created_at <= created_to)
        return conditions

    async def search(
        self,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        department_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        conditions = self._build_filters(
            name, lastname, code, is_active, role_id, department_id, created_from, created_to
        )
        stmt = select(User).options(*_USER_LOADS)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(User.name).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        department_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
    ) -> int:
        conditions = self._build_filters(
            name, lastname, code, is_active, role_id, department_id, created_from, created_to
        )
        stmt = select(func.count()).select_from(User)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.flush()
        await self.db.refresh(user)
        return user