from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_fel_service, get_current_user
from app.db.models import Usuario
from app.services.fel_service import ConcreteFelService
from app.schemas import fel_schema

router = APIRouter()


@router.get("/pendientes", response_model=List[fel_schema.FelEmisionResponse])
async def listar_pendientes(
    service: ConcreteFelService = Depends(get_fel_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las facturas FEL en estado Pendiente DTE / Contingencia para reintento."""
    facturas = await service.listar_pendientes()
    return [fel_schema.FelEmisionResponse.model_validate(f) for f in facturas]


@router.post(
    "/reintentar/{id_venta}",
    response_model=fel_schema.FelEmisionResponse,
)
async def reintentar_certificacion(
    id_venta: int,
    service: ConcreteFelService = Depends(get_fel_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reintenta la certificación FEL de una venta en contingencia."""
    factura = await service.reintentar_certificacion(id_venta)
    return fel_schema.FelEmisionResponse.model_validate(factura)
