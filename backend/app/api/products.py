from fastapi import APIRouter, Depends, status
from app.api.deps import get_product_service, get_current_user
from app.db.models import Usuario
from app.services.product_service import ConcreteProductService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=schemas.ProductoList)
async def list_products(
    filters: schemas.ProductoFilter = Depends(),
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    items = await service.list_products(filters)
    total = await service.count_products(filters)
    return schemas.ProductoList(total=total, items=items)


@router.get("/barcode/{barcode}", response_model=schemas.ProductoOut)
async def get_product_by_barcode(
    barcode: str,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_by_barcode(barcode)


@router.get("/{product_id}", response_model=schemas.ProductoOut)
async def get_product(
    product_id: int,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_product(product_id)


@router.post("", response_model=schemas.ProductoOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: schemas.ProductoCreate,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Inserta de forma atómica Producto + VarianteProducto + InventarioSucursal."""
    return await service.create_product(payload)


@router.put("/{product_id}", response_model=schemas.ProductoOut)
async def update_product(
    product_id: int,
    payload: schemas.ProductoUpdate,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_product(product_id, payload)


@router.delete("/{product_id}", response_model=schemas.ProductoOut)
async def deactivate_product(
    product_id: int,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca el producto como inactivo."""
    return await service.deactivate_product(product_id)