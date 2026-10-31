import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.deps import get_product_service, get_current_user
from app.db.models import Usuario
from app.services.product_service import ConcreteProductService
from app.schemas import schemas

router = APIRouter()

MAX_IMAGE_BYTES = 5 * 1024 * 1024
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "productos")


def _detect_image_extension(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
        return ".gif"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"
    return None


@router.post("/upload-imagen", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    """Sube una imagen opcional para un producto y devuelve su URL pública."""
    content = await file.read(MAX_IMAGE_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el límite de 5 MB")

    extension = _detect_image_extension(content)
    if not extension:
        raise HTTPException(
            status_code=415,
            detail="Formato no permitido. Usa JPG, PNG, WEBP o GIF",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as destination:
        destination.write(content)

    return {"imagen_url": f"/api/uploads/productos/{filename}"}


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


@router.get("/generar-codigo")
async def generate_new_barcode(
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Genera un código de barras EAN-13 guatemalteco único para el formulario."""
    code = await service.generate_unique_barcode()
    return {"codigo_barras": code}


@router.post("/generar-codigos-faltantes")
async def generate_missing_barcodes(
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Asigna códigos EAN-13 válidos a todos los productos y variantes que no tengan uno."""
    return await service.generate_missing_barcodes()


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
    return await service.create_product(payload, actor_id=current_user.id_usuario)


@router.put("/{product_id}", response_model=schemas.ProductoOut)
async def update_product(
    product_id: int,
    payload: schemas.ProductoUpdate,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_product(product_id, payload, actor_id=current_user.id_usuario)


@router.patch("/{product_id}/imagen", response_model=schemas.ProductoOut)
async def update_product_image(
    product_id: int,
    payload: schemas.ProductoUpdate,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza la URL de la imagen del producto."""
    return await service.update_product(product_id, payload, actor_id=current_user.id_usuario)


@router.delete("/{product_id}", response_model=schemas.ProductoOut)
async def deactivate_product(
    product_id: int,
    service: ConcreteProductService = Depends(get_product_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca el producto como inactivo."""
    return await service.deactivate_product(product_id, actor_id=current_user.id_usuario)