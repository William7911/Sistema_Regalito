from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.db.models import Usuario
from app.core import security
from app.core.config import settings
from app.schemas import schemas

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.estado != "Activo":
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "role": user.rol.nombre if user.rol else None},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}