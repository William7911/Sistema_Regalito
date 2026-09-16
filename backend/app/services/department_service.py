from typing import Optional, List
from fastapi import HTTPException
from app.db.models import DepartamentoGeografico
from app.interfaces.services import DepartmentService
from app.schemas import schemas


class ConcreteDepartmentService(DepartmentService):
    """Lógica de negocio de Departamentos (modelo DepartamentoGeografico).
    Usa Unit of Work para la transacción."""

    def __init__(self, uow):
        self.uow = uow

    async def list_departments(self, include_inactive: bool = False) -> List[schemas.Department]:
        departments = await self.uow.departments.list_all()
        return [schemas.Department.model_validate(d) for d in departments]

    async def get_department(self, department_id: int) -> schemas.Department:
        department = await self.uow.departments.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        return schemas.Department.model_validate(department)

    async def create_department(self, data: schemas.DepartmentCreate) -> schemas.Department:
        existing = await self.uow.departments.get_by_name(data.nombre.strip())
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un departamento con ese nombre")
        department = DepartamentoGeografico(nombre=data.nombre.strip())
        created = await self.uow.departments.create(department)
        await self.uow.commit()
        return schemas.Department.model_validate(created)

    async def update_department(
        self, department_id: int, data: schemas.DepartmentUpdate
    ) -> schemas.Department:
        department = await self.uow.departments.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")

        if data.nombre is not None:
            nombre = data.nombre.strip()
            duplicate = await self.uow.departments.get_by_name(nombre)
            if duplicate and duplicate.id_departamento != department_id:
                raise HTTPException(
                    status_code=400, detail="Ya existe un departamento con ese nombre"
                )
            department.nombre = nombre

        updated = await self.uow.departments.update(department)
        await self.uow.commit()
        return schemas.Department.model_validate(updated)

    async def deactivate_department(self, department_id: int) -> schemas.Department:
        """Eliminación lógica (soft delete).

        Nota: el modelo `DepartamentoGeografico` no posee campo de estado,
        por lo que la desactivación es un no-op que devuelve el registro.
        """
        department = await self.uow.departments.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        return schemas.Department.model_validate(department)