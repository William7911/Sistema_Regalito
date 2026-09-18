from fastapi import APIRouter, Depends, status
from typing import Optional, List
from app.api.deps import get_cash_service, get_current_user
from app.db.models import Usuario
from app.services.cash_service import ConcreteCashService
from app.schemas import schemas

router = APIRouter()


@router.post("/apertura", response_model=schemas.TurnoResponse, status_code=status.HTTP_201_CREATED)
async def open_cash_register(
    turno_data: schemas.TurnoApertura,
    service: ConcreteCashService = Depends(get_cash_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.abrir_caja(turno_data, current_user.id_usuario)


@router.post("/cierre", response_model=schemas.TurnoResponse)
async def close_cash_register(
    turno_data: schemas.TurnoCierre,
    service: ConcreteCashService = Depends(get_cash_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.cerrar_caja(turno_data, current_user.id_usuario)


@router.get("/estado-actual", response_model=Optional[schemas.TurnoResponse])
async def get_current_cash_status(
    service: ConcreteCashService = Depends(get_cash_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_estado_actual(current_user.id_usuario)


@router.get("/turnos", response_model=schemas.TurnoList)
async def list_cash_turnos(
    filters: schemas.TurnoFilter = Depends(),
    service: ConcreteCashService = Depends(get_cash_service),
    current_user: Usuario = Depends(get_current_user),
):
    items = await service.list_turnos(filters)
    total = await service.count_turnos(filters)
    return schemas.TurnoList(total=total, items=items)


@router.get("/cajas", response_model=List[schemas.CajaOut])
async def list_cash_registers(
    include_inactive: bool = False,
    service: ConcreteCashService = Depends(get_cash_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_cajas(include_inactive=include_inactive)