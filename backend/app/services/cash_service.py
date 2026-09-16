from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
from app.db.models import TurnoCaja
from app.interfaces.services import CashRegisterService
from app.schemas import schemas


class ConcreteCashService(CashRegisterService):
    """Lógica de negocio del Módulo de Caja (modelos Caja y TurnoCaja).
    Usa el Unit of Work para coordinar transacciones."""

    def __init__(self, uow):
        self.uow = uow

    async def abrir_caja(self, data: schemas.TurnoApertura, user_id: int) -> schemas.TurnoResponse:
        # 1. Validar que el usuario no tenga ya un turno abierto
        user_active = await self.uow.turnos.get_active_by_user(user_id)
        if user_active:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya tiene un turno de caja abierto",
            )

        # 2. Validar que la caja exista
        caja = await self.uow.cajas.get_by_id(data.id_caja)
        if not caja:
            raise HTTPException(
                status_code=404,
                detail="La caja especificada no existe",
            )

        # 3. Validar que la caja esté activa
        if caja.estado in ("Inactiva", "Inactivo"):
            raise HTTPException(
                status_code=400,
                detail="La caja especificada no está activa",
            )

        # 4. Validar que la caja no esté ocupada por otro usuario
        caja_active = await self.uow.turnos.get_active_by_caja(data.id_caja)
        if caja_active:
            raise HTTPException(
                status_code=400,
                detail="La caja seleccionada ya cuenta con un turno abierto",
            )

        new_turno = TurnoCaja(
            id_caja=data.id_caja,
            id_usuario=user_id,
            monto_apertura=data.monto_apertura,
            fecha_apertura=datetime.now(),
            estado="Abierto",
        )

        try:
            created = await self.uow.turnos.create(new_turno)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        fresh = await self.uow.turnos.get_by_id(created.id_turno)
        return schemas.TurnoResponse.model_validate(fresh)

    async def cerrar_caja(self, data: schemas.TurnoCierre, user_id: int) -> schemas.TurnoResponse:
        # 1. Validar turno activo del usuario
        active_turno = await self.uow.turnos.get_active_by_user(user_id)
        if not active_turno:
            raise HTTPException(
                status_code=400,
                detail="El usuario no tiene un turno de caja abierto",
            )

        # 2. Actualizar datos de cierre
        active_turno.fecha_cierre = datetime.now()
        active_turno.monto_cierre = data.monto_cierre
        if data.notas is not None:
            active_turno.notas = data.notas.strip() if data.notas.strip() else None
        active_turno.estado = "Cerrado"

        try:
            await self.uow.turnos.update(active_turno)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        fresh = await self.uow.turnos.get_by_id(active_turno.id_turno)
        return schemas.TurnoResponse.model_validate(fresh)

    async def get_estado_actual(self, user_id: int) -> Optional[schemas.TurnoResponse]:
        active = await self.uow.turnos.get_active_by_user(user_id)
        if not active:
            return None
        return schemas.TurnoResponse.model_validate(active)

    async def list_turnos(self, filters: schemas.TurnoFilter) -> List[schemas.TurnoResponse]:
        turnos = await self.uow.turnos.search(
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            estado=filters.estado,
            id_caja=filters.id_caja,
            sort_by=filters.sort_by,
            sort_dir=filters.sort_dir or "desc",
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.TurnoResponse.model_validate(t) for t in turnos]

    async def count_turnos(self, filters: schemas.TurnoFilter) -> int:
        return await self.uow.turnos.count_search(
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            estado=filters.estado,
            id_caja=filters.id_caja,
        )

    async def list_cajas(self, include_inactive: bool = False) -> List[schemas.CajaOut]:
        cajas = await self.uow.cajas.list_all(include_inactive=include_inactive)
        return [schemas.CajaOut.model_validate(c) for c in cajas]
