import csv
import io
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from app.db.models import Usuario
from app.core import security
from app.interfaces.services import UserService
from app.schemas import schemas


class ConcreteUserService(UserService):
    """Lógica de negocio de Usuarios (modelo Usuario). El rol siempre se valida contra la BD."""

    def __init__(self, uow):
        self.uow = uow

    async def _validate_role(self, role_id: int):
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=400, detail="El rol especificado no existe")
        if role.estado != "Activo":
            raise HTTPException(status_code=400, detail="El rol especificado está inactivo")

    async def list_users(self, filters: schemas.UserFilter) -> List[schemas.UserResponse]:
        users = await self.uow.users.search(
            name=filters.name,
            is_active=filters.is_active,
            role_id=filters.role_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            sort_by=filters.sort_by,
            sort_dir=filters.sort_dir or "asc",
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.UserResponse.model_validate(u) for u in users]

    async def count_users(self, filters: schemas.UserFilter) -> int:
        return await self.uow.users.count_search(
            name=filters.name,
            is_active=filters.is_active,
            role_id=filters.role_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    async def get_user(self, user_id: int) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return schemas.UserResponse.model_validate(user)

    async def create_user(self, data: schemas.UserCreate) -> schemas.UserResponse:
        await self._validate_role(data.id_rol)
        if await self.uow.users.get_by_username(data.username.strip()):
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese nombre de usuario")

        user = Usuario(
            id_rol=data.id_rol,
            nombre_completo=data.nombre_completo.strip(),
            username=data.username.strip(),
            password_hash=security.get_password_hash(data.password),
            estado="Activo",
        )
        try:
            created = await self.uow.users.create(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(created.id_usuario)
        return schemas.UserResponse.model_validate(fresh)

    async def update_user(
        self, user_id: int, data: schemas.UserUpdate
    ) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if data.id_rol is not None:
            await self._validate_role(data.id_rol)
            user.id_rol = data.id_rol

        if data.username is not None:
            username = data.username.strip()
            duplicate = await self.uow.users.get_by_username(username)
            if duplicate and duplicate.id_usuario != user_id:
                raise HTTPException(
                    status_code=400, detail="Ya existe un usuario con ese nombre de usuario"
                )
            user.username = username
        if data.nombre_completo is not None:
            user.nombre_completo = data.nombre_completo.strip()
        if data.password:
            user.password_hash = security.get_password_hash(data.password)
        if data.estado is not None:
            user.estado = data.estado.strip()

        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id_usuario)
        return schemas.UserResponse.model_validate(fresh)

    async def deactivate_user(self, user_id: int) -> schemas.UserResponse:
        """Eliminación lógica (soft delete)."""
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.estado = "Inactivo"
        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id_usuario)
        return schemas.UserResponse.model_validate(fresh)

    # ------------------------------------------------------------------
    # Reporte exportable (Excel / CSV)
    # ------------------------------------------------------------------

    _REPORT_HEADERS = ["ID", "Nombre Completo", "Usuario", "Rol", "Estado", "Fecha Registro"]

    def _user_row(self, u: schemas.UserResponse) -> list:
        """Convierte un UserResponse en una fila del reporte."""
        fecha = (
            u.fecha_creacion.strftime("%Y-%m-%d %H:%M") if u.fecha_creacion else ""
        )
        rol = u.rol.nombre if u.rol else str(u.id_rol)
        return [u.id_usuario, u.nombre_completo, u.username, rol, u.estado, fecha]

    async def export_users(self, filters: schemas.UserFilter, fmt: str) -> StreamingResponse:
        """Genera el reporte de usuarios en Excel (.xlsx) o CSV (.csv).

        Reutiliza la capa de repositorio existente sin duplicar lógica;
        ignora la paginación del filtro para exportar el conjunto completo.
        """
        users = await self.uow.users.search(
            name=filters.name,
            is_active=filters.is_active,
            role_id=filters.role_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            sort_by=filters.sort_by,
            sort_dir=filters.sort_dir or "asc",
            limit=10_000,
            offset=0,
        )
        rows = [self._user_row(schemas.UserResponse.model_validate(u)) for u in users]
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        if fmt == "csv":
            return self._build_csv(rows, fecha_hoy)
        return self._build_excel(rows, fecha_hoy)

    def _build_csv(self, rows: list, fecha: str) -> StreamingResponse:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self._REPORT_HEADERS)
        writer.writerows(rows)
        output.seek(0)
        content = output.getvalue().encode("utf-8-sig")  # BOM para Excel en Windows
        return StreamingResponse(
            iter([content]),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="reporte_usuarios_{fecha}.csv"'
            },
        )

    def _build_excel(self, rows: list, fecha: str) -> StreamingResponse:
        wb = Workbook()
        ws = wb.active
        ws.title = "Usuarios"

        # Cabecera con estilo corporativo
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(fill_type="solid", fgColor="0F172A")  # RNF24 dark
        header_align = Alignment(horizontal="center", vertical="center")

        for col_idx, header in enumerate(self._REPORT_HEADERS, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align

        # Datos
        for row in rows:
            ws.append(row)

        # Anchos automáticos
        col_widths = [8, 35, 20, 20, 12, 20]
        for col_idx, width in enumerate(col_widths, start=1):
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = width

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return StreamingResponse(
            iter([output.read()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="reporte_usuarios_{fecha}.xlsx"'
            },
        )