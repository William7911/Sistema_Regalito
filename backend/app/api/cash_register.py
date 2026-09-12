from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.database import get_db
from app.db import models
from app.core.config import settings
from app.schemas import schemas
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/apertura", response_model=schemas.CashRegisterResponse)
def open_cash_register(
    cash_data: schemas.CashRegisterOpen, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verificar si el usuario ya tiene una caja abierta
    open_register = db.query(models.CashRegister).filter(
        models.CashRegister.user_id == current_user.id,
        models.CashRegister.status == "Abierta"
    ).first()
    
    if open_register:
        raise HTTPException(status_code=400, detail="El usuario ya tiene una caja abierta")
        
    try:
        new_register = models.CashRegister(
            user_id=current_user.id,
            opening_amount=cash_data.opening_amount,
            petty_cash=cash_data.petty_cash,
            status="Abierta"
        )
        db.add(new_register)
        db.commit()
        db.refresh(new_register)
        return new_register
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al abrir la caja: {str(e)}")

@router.post("/cierre-ciegas", response_model=schemas.CashRegisterResponse)
def close_cash_register(
    cash_data: schemas.CashRegisterClose, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Buscar caja abierta del usuario
    open_register = db.query(models.CashRegister).filter(
        models.CashRegister.user_id == current_user.id,
        models.CashRegister.status == "Abierta"
    ).first()
    
    if not open_register:
        raise HTTPException(status_code=400, detail="El usuario no tiene una caja abierta")
        
    try:
        open_register.blind_closing_amount = cash_data.blind_closing_amount
        open_register.closing_time = datetime.utcnow()
        open_register.status = "Cerrada"
        db.commit()
        db.refresh(open_register)
        return open_register
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cerrar la caja: {str(e)}")
