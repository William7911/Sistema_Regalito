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

from app.api.deps import get_facturacion_offline_service
from app.services.facturacion_offline_service import FacturacionOfflineService
from fastapi import Request

@router.post("/offline", status_code=status.HTTP_201_CREATED)
async def process_offline_sale(
    request: Request,
    is_online: bool = True,
    current_user: Usuario = Depends(require_permission("VENTA_COBRAR")),
    current_shift: TurnoCaja = Depends(get_current_active_shift),
    service: FacturacionOfflineService = Depends(get_facturacion_offline_service)
):
    """Procesa una venta con el motor de facturación offline."""
    sale_data = await request.json()
    sale_data["id_usuario"] = current_user.id_usuario
    sale_data["id_turno"] = current_shift.id_turno
    venta = await service.procesar_venta(sale_data, is_online=is_online)
    return {"status": "success", "id_venta": venta.id_venta}

@router.get("/sync-queue/status")
async def check_sync_queue(
    current_user: Usuario = Depends(require_permission("VENTA_COBRAR")),
    service: FacturacionOfflineService = Depends(get_facturacion_offline_service)
):
    """Consulta el estado de la cola de sincronización de ventas."""
    # Como los controladores deben ser delgados, delegamos la consulta al servicio.
    # Asumo que crearé un método rápido para contar pendientes en el servicio.
    pendientes = await service.contar_pendientes()
    return {"pendientes": pendientes}

