from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.api.cash_register import get_current_user

router = APIRouter()

@router.get("/barcode/{barcode}", response_model=schemas.Product)
def get_product_by_barcode(
    barcode: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not product.is_active:
        raise HTTPException(status_code=400, detail="El producto está inactivo")
    return product
