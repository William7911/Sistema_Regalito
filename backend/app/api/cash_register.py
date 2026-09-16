from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Caja, TurnoCaja, Usuario
from app.api.deps import get_current_user
from app.schemas import schemas
from datetime import datetime

router = APIRouter()


@router.post("/apertura", response_model=schemas.TurnoResponse)
async def open_cash_register(
    turno_data: schemas.TurnoApertura,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(TurnoCaja).where(
            TurnoCaja.id_usuario == current_user.id_usuario,
            TurnoCaja.estado == "Abierta",
        )
    )
    open_turno = result.scalar_one_or_none()

    if open_turno:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un turno de caja abierto")

    caja = await db.execute(select(Caja).where(Caja.id_caja == turno_data.id_caja))
    if caja.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail="La caja especificada no existe")

    try:
        new_turno = TurnoCaja(
            id_caja=turno_data.id_caja,
            id_usuario=current_user.id_usuario,
            monto_apertura=turno_data.monto_apertura,
            fecha_apertura=datetime.utcnow(),
            estado="Abierta",
        )
        db.add(new_turno)
        await db.commit()
        await db.refresh(new_turno)
        return new_turno
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al abrir la caja: {str(e)}")


@router.post("/cierre-ciegas", response_model=schemas.TurnoResponse)
async def close_cash_register(
    turno_data: schemas.TurnoCierre,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(TurnoCaja).where(
            TurnoCaja.id_usuario == current_user.id_usuario,
            TurnoCaja.estado == "Abierta",
        )
    )
    open_turno = result.scalar_one_or_none()

    if not open_turno:
        raise HTTPException(status_code=400, detail="El usuario no tiene un turno de caja abierto")

    try:
        open_turno.fecha_cierre = datetime.utcnow()
        open_turno.estado = "Cerrada"
        await db.commit()
        await db.refresh(open_turno)
        return open_turno
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cerrar la caja: {str(e)}")