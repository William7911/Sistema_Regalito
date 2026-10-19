import uuid
import json
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select

from app.api.deps import UnitOfWork
from app.db.models import Venta, DetalleVenta, InventarioSucursal, SyncQueue

class FacturacionOfflineService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.db = uow.db

    async def procesar_venta(self, venta_data: dict, is_online: bool = True):
        # 1. Validar y descontar inventario con bloqueo pesimista
        detalles = venta_data.get("detalles", [])
        nuevos_detalles = []
        
        for d in detalles:
            # BLOQUEO PESIMISTA: SELECT FOR UPDATE
            result = await self.db.execute(
                select(InventarioSucursal)
                .where(InventarioSucursal.id_variante == d["id_variante"])
                .with_for_update()
            )
            inv = result.scalar_one_or_none()
            
            if not inv:
                raise HTTPException(status_code=400, detail="Inventario no encontrado.")
            
            if inv.stock_actual < d["cantidad"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock insuficiente para variante {d['id_variante']}. Requerido: {d['cantidad']}, Actual: {inv.stock_actual}"
                )
            
            # Descontar
            inv.stock_actual -= d["cantidad"]
            self.db.add(inv)
            
            nuevos_detalles.append(
                DetalleVenta(
                    id_variante=d["id_variante"],
                    cantidad=d["cantidad"],
                    precio_unitario=d["precio_unitario"],
                    descuento_item=d.get("descuento_item", Decimal("0.00")),
                    subtotal=d["subtotal"]
                )
            )
            
        # 2. Crear Venta local
        nueva_venta = Venta(
            id_turno=venta_data["id_turno"],
            id_usuario=venta_data["id_usuario"],
            fecha_venta=datetime.utcnow(),
            subtotal=venta_data["subtotal"],
            descuento_total=venta_data["descuento_total"],
            total_venta=venta_data["total_venta"],
            estado="Completada",
            detalles=nuevos_detalles
        )
        self.db.add(nueva_venta)
        await self.db.flush() # Para obtener el id_venta
        
        # 3. Manejo de conexión y SyncQueue
        if is_online:
            # Aquí se llamaría al certificador FEL
            # await certificador_fel(nueva_venta)
            pass
        else:
            # Generar Idempotency Key (UUIDv4)
            idempotency_key = str(uuid.uuid4())
            
            payload = {
                "id_venta": nueva_venta.id_venta,
                "total": str(nueva_venta.total_venta)
            }
            
            sync_item = SyncQueue(
                idempotency_key=idempotency_key,
                entidad="venta",
                entidad_id=nueva_venta.id_venta,
                operacion="INSERT",
                payload=json.dumps(payload),
                estado="PENDIENTE"
            )
            self.db.add(sync_item)
            
        await self.db.commit()
        return nueva_venta

    async def contar_pendientes(self):
        """Cuenta la cantidad de transacciones pendientes en la cola."""
        result = await self.db.execute(
            select(SyncQueue).where(SyncQueue.estado == "PENDIENTE")
        )
        return len(result.scalars().all())

    async def sync_pending_transactions(self):
        """Simula la acción del SyncEngine de recuperar red y sincronizar."""
        result = await self.db.execute(
            select(SyncQueue).where(SyncQueue.estado == "PENDIENTE")
        )
        pendientes = result.scalars().all()
        
        for item in pendientes:
            # Simular envío a la nube y certificación
            # payload = json.loads(item.payload)
            # await procesar_en_nube(payload, idempotency_key=item.idempotency_key)
            
            item.estado = "SINCRONIZADO"
            item.actualizado_en = datetime.utcnow()
            self.db.add(item)
            
        await self.db.commit()
