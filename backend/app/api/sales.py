from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user, get_sale_service, get_current_active_shift, require_permission
from app.db.models import Usuario, TurnoCaja
from app.services.sale_service import ConcreteSaleService
from app.schemas import sale_schema

router = APIRouter()


@router.post("", response_model=sale_schema.SaleResponse, status_code=status.HTTP_201_CREATED)
async def process_sale(
    sale_data: sale_schema.SaleCreate,
    current_user: Usuario = Depends(require_permission("VENTA_COBRAR")),
    current_shift: TurnoCaja = Depends(get_current_active_shift),
    service: ConcreteSaleService = Depends(get_sale_service),
):
    """Procesa una transacción de venta en el POS (RF01, RF05).
    Exige un turno de caja abierto (403 Forbidden si no hay fondo inicial),
    aplica regla de mayoreo automática y descuenta inventario de forma atómica."""
    return await service.registrar_venta(sale_data, current_user.id_usuario, current_shift, current_user=current_user)


@router.get("", response_model=sale_schema.SaleList)
async def list_sales(
    filters: sale_schema.SaleFilter = Depends(),
    service: ConcreteSaleService = Depends(get_sale_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Consulta el historial de ventas con filtros de fecha, turno y cliente."""
    items = await service.list_sales(filters)
    total = await service.count_sales(filters)
    return sale_schema.SaleList(total=total, items=items)


@router.get("/{sale_id}", response_model=sale_schema.SaleResponse)
async def get_sale_detail(
    sale_id: int,
    service: ConcreteSaleService = Depends(get_sale_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene el detalle completo de una venta con sus líneas y formas de pago."""
    return await service.get_sale(sale_id)

