from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import CashRegister, User
from app.api.deps import get_current_user
from app.schemas import schemas
from datetime import datetime

router = APIRouter()


@router.post("/apertura", response_model=schemas.CashRegisterResponse)
async def open_cash_register(
    cash_data: schemas.CashRegisterOpen,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CashRegister).where(
            CashRegister.user_id == current_user.id,
            CashRegister.status == "Abierta",
        )
    )
    open_register = result.scalar_one_or_none()

    if open_register:
        raise HTTPException(status_code=400, detail="El usuario ya tiene una caja abierta")

    try:
        new_register = CashRegister(
            user_id=current_user.id,
            opening_amount=cash_data.opening_amount,
            petty_cash=cash_data.petty_cash,
            status="Abierta",
        )
        db.add(new_register)
        await db.commit()
        await db.refresh(new_register)
        return new_register
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al abrir la caja: {str(e)}")


@router.post("/cierre-ciegas", response_model=schemas.CashRegisterResponse)
async def close_cash_register(
    cash_data: schemas.CashRegisterClose,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CashRegister).where(
            CashRegister.user_id == current_user.id,
            CashRegister.status == "Abierta",
        )
    )
    open_register = result.scalar_one_or_none()

    if not open_register:
        raise HTTPException(status_code=400, detail="El usuario no tiene una caja abierta")

    try:
        open_register.blind_closing_amount = cash_data.blind_closing_amount
        open_register.closing_time = datetime.utcnow()
        open_register.status = "Cerrada"
        await db.commit()
        await db.refresh(open_register)
        return open_register
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cerrar la caja: {str(e)}")