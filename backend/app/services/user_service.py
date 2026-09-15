from typing import Optional, List
from fastapi import HTTPException
from app.db.models import User
from app.core import security
from app.interfaces.services import UserService
from app.schemas import schemas


class ConcreteUserService(UserService):
    """Lógica de negocio de Usuarios. Roles y departamentos siempre se validan contra la BD."""

    def __init__(self, uow):
        self.uow = uow

    async def _validate_role_department(self, role_id: int, department_id: int):
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=400, detail="El rol especificado no existe")
        if not role.is_active:
            raise HTTPException(status_code=400, detail="El rol especificado está inactivo")

        department = await self.uow.departments.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=400, detail="El departamento especificado no existe")
        if not department.is_active:
            raise HTTPException(
                status_code=400, detail="El departamento especificado está inactivo"
            )

    async def list_users(self, filters: schemas.UserFilter) -> List[schemas.UserResponse]:
        users = await self.uow.users.search(
            name=filters.name,
            lastname=filters.lastname,
            code=filters.code,
            is_active=filters.is_active,
            role_id=filters.role_id,
            department_id=filters.department_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.UserResponse.model_validate(u) for u in users]

    async def count_users(self, filters: schemas.UserFilter) -> int:
        return await self.uow.users.count_search(
            name=filters.name,
            lastname=filters.lastname,
            code=filters.code,
            is_active=filters.is_active,
            role_id=filters.role_id,
            department_id=filters.department_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    async def get_user(self, user_id: int) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return schemas.UserResponse.model_validate(user)

    async def create_user(self, data: schemas.UserCreate) -> schemas.UserResponse:
        await self._validate_role_department(data.role_id, data.department_id)
        if await self.uow.users.get_by_username(data.username.strip()):
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese nombre de usuario")
        if await self.uow.users.get_by_code(data.code.strip()):
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese código")

        user = User(
            name=data.name.strip(),
            lastname=data.lastname.strip(),
            code=data.code.strip(),
            username=data.username.strip(),
            password_hash=security.get_password_hash(data.password),
            role_id=data.role_id,
            department_id=data.department_id,
        )
        try:
            created = await self.uow.users.create(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(created.id)
        return schemas.UserResponse.model_validate(fresh)

    async def update_user(
        self, user_id: int, data: schemas.UserUpdate
    ) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        role_id = data.role_id if data.role_id is not None else user.role_id
        department_id = (
            data.department_id if data.department_id is not None else user.department_id
        )
        await self._validate_role_department(role_id, department_id)

        if data.role_id is not None:
            user.role_id = data.role_id
        if data.department_id is not None:
            user.department_id = data.department_id

        if data.username is not None:
            username = data.username.strip()
            duplicate = await self.uow.users.get_by_username(username)
            if duplicate and duplicate.id != user_id:
                raise HTTPException(
                    status_code=400, detail="Ya existe un usuario con ese nombre de usuario"
                )
            user.username = username
        if data.code is not None:
            code = data.code.strip()
            duplicate = await self.uow.users.get_by_code(code)
            if duplicate and duplicate.id != user_id:
                raise HTTPException(status_code=400, detail="Ya existe un usuario con ese código")
            user.code = code
        if data.name is not None:
            user.name = data.name.strip()
        if data.lastname is not None:
            user.lastname = data.lastname.strip()
        if data.password:
            user.password_hash = security.get_password_hash(data.password)
        if data.is_active is not None:
            user.is_active = data.is_active

        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id)
        return schemas.UserResponse.model_validate(fresh)

    async def deactivate_user(self, user_id: int) -> schemas.UserResponse:
        """Eliminación lógica (soft delete)."""
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.is_active = False
        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id)
        return schemas.UserResponse.model_validate(fresh)