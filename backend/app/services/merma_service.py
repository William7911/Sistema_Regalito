from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.db.models import Merma, DetalleMerma
from app.schemas import merma_schema


class ConcreteMermaService:
    """Lógica de negocio del Módulo de Mermas (RF10, Proceso 2).
    Aplica el descargo atómico de existencias en inventario_sucursal
    sin alterar registros de ventas ni reportes de caja."""

    def __init__(self, uow):
        self.uow = uow

    async def get_motivos(self) -> List[merma_schema.MotivoMermaOut]:
        motivos = await self.uow.mermas.get_motivos()
        return [merma_schema.MotivoMermaOut.model_validate(m) for m in motivos]

    async def registrar_merma(self, data: merma_schema.MermaCreate, user_id: int) -> merma_schema.MermaOut:
        detalles_model: List[DetalleMerma] = []
        costo_total = Decimal("0.00")

        # 1. Validar cada ítem de merma y realizar el descargo de inventario
        for item in data.detalles:
            # Validar motivo
            motivo = await self.uow.mermas.get_motivo_by_id(item.id_motivo)
            if not motivo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El motivo de merma con ID {item.id_motivo} no existe.",
                )

            # Validar variante
            variante = await self.uow.mermas.get_variante(item.id_variante)
            if not variante:
                raise HTTPException(
                    status_code=404,
                    detail=f"La variante de producto con ID {item.id_variante} no existe.",
                )

            # Validar existencias en la sucursal
            inventario = await self.uow.mermas.get_inventario(item.id_variante, data.id_sucursal)
            if not inventario:
                raise HTTPException(
                    status_code=400,
                    detail=f"No hay inventario registrado para la variante ID {item.id_variante} en la sucursal {data.id_sucursal}.",
                )

            if inventario.stock_actual < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para la variante ID {item.id_variante}. Disponible: {inventario.stock_actual}, Solicitado: {item.cantidad}.",
                )

            # Descargo atómico de inventario
            inventario.stock_actual -= item.cantidad

            # Cálculo de costo de pérdida según costo_promedio
            costo_unitario = Decimal(str(variante.costo_promedio or "0.00"))
            costo_perdida = Decimal(item.cantidad) * costo_unitario
            costo_total += costo_perdida

            detalles_model.append(
                DetalleMerma(
                    id_variante=item.id_variante,
                    id_motivo=item.id_motivo,
                    cantidad=item.cantidad,
                    costo_perdida=costo_perdida,
                )
            )

        # 2. Crear registro de merma
        merma = Merma(
            id_sucursal=data.id_sucursal,
            id_usuario=user_id,
            fecha_merma=datetime.now(),
            observaciones=data.observaciones.strip() if data.observaciones else None,
        )

        try:
            created = await self.uow.mermas.create_merma(merma, detalles_model)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        fresh = await self.uow.mermas.get_merma_by_id(created.id_merma)
        resp = merma_schema.MermaOut.model_validate(fresh)
        resp.costo_total_perdida = costo_total
        return resp

    async def list_mermas(self, filters: merma_schema.MermaFilter) -> List[merma_schema.MermaOut]:
        items = await self.uow.mermas.search(
            id_sucursal=filters.id_sucursal,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [merma_schema.MermaOut.model_validate(m) for m in items]

    async def count_mermas(self, filters: merma_schema.MermaFilter) -> int:
        return await self.uow.mermas.count_search(
            id_sucursal=filters.id_sucursal,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
        )

