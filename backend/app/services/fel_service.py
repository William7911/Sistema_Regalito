import httpx
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException

from app.core.config import settings
from app.db.models import FacturaFel
from app.schemas import fel_schema

MAXIMO_CF_SIN_NIT = Decimal("2500.00")
ESTADO_CONTINGENCIA = "Contingencia"
ESTADO_PENDIENTE = "Pendiente DTE"
ESTADO_CERTIFICADA = "Certificada"


class FelRechazoError(Exception):
    """El certificador SAT rechazo la factura por reglas fiscales (HTTP 400/422)."""

    def __init__(self, detalle: str):
        self.detalle = detalle
        super().__init__(detalle)


class FelServicioNoDisponible(Exception):
    """El certificador no está disponible (timeout, 5xx o red caída)."""


class ConcreteFelService:
    """Lógica de negocio de la Facturación Electrónica en Línea (FEL).

    Responsabilidades:
      - Reglas locales: totales > 0 y bloqueo de NIT "CF" en ventas > Q2,500.00.
      - Comunicación asíncrona con el certificador SAT (httpx).
      - Manejo de contingencias: ante timeout/caída la venta NO se revierte y el
        registro queda en estado "Pendiente DTE"/"Contingencia" para reintento.
      - El rechazo fiscal (HTTP 400/422) NO guarda factura y, al integrarse con la
        venta vía UnitOfWork, la transacción completa se revierte (venta y stock).
    """

    def __init__(self, uow, client: Optional[httpx.AsyncClient] = None, app_settings=None):
        self.uow = uow
        self.db = uow.db
        self._client = client
        self.settings = app_settings or settings

    # ------------------------------------------------------------------
    # Reglas de negocio locales
    # ------------------------------------------------------------------
    def _validar_totales(self, total: Decimal, items: Optional[List[dict]] = None):
        if total is None or total <= 0:
            raise HTTPException(
                status_code=400,
                detail="Los totales de la factura deben ser mayores a cero y no pueden contener cantidades negativas.",
            )
        if items:
            for item in items:
                cantidad = Decimal(str(item.get("cantidad", 1)))
                if cantidad <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Los totales de la factura deben ser mayores a cero y no pueden contener cantidades negativas.",
                    )

    def _validar_cf(self, nit: str, total: Decimal):
        es_cf = nit == "" or nit.upper() == "CF"
        if es_cf and total > MAXIMO_CF_SIN_NIT:
            raise HTTPException(
                status_code=400,
                detail="Para compras mayores a Q2,500.00 es obligatorio ingresar el NIT y Nombre del cliente. No se permite CF.",
            )

    # ------------------------------------------------------------------
    # Comunicación con el certificador
    # ------------------------------------------------------------------
    async def _post(self, url: str, json: dict, headers: dict) -> httpx.Response:
        if self._client is not None:
            return await self._client.post(url, json=json, headers=headers)
        async with httpx.AsyncClient(timeout=self.settings.FEL_TIMEOUT) as client:
            return await client.post(url, json=json, headers=headers)

    async def _certificar(self, request: fel_schema.FelEmisionRequest) -> fel_schema.FelCertificacionRespuesta:
        url = self.settings.FEL_API_URL
        if not url and self._client is None:
            raise FelServicioNoDisponible(
                "Certificador FEL no configurado. La venta se guardará en contingencia."
            )
        url = url or "http://certificador-sat.local/api/factura"

        headers = {}
        if self.settings.FEL_API_KEY:
            headers["Authorization"] = f"Bearer {self.settings.FEL_API_KEY}"
        payload = request.model_dump(mode="json")

        try:
            response = await self._post(url, json=payload, headers=headers)
        except httpx.TimeoutException:
            raise FelServicioNoDisponible("Timeout del certificador FEL.")
        except httpx.HTTPError:
            raise FelServicioNoDisponible("Falla de red con el certificador FEL.")

        if response.status_code in (400, 422):
            detalle = self._extraer_error(response)
            raise FelRechazoError(detalle)
        if response.status_code >= 500:
            raise FelServicioNoDisponible(f"Certificador devolvió {response.status_code}.")
        if response.status_code >= 400:
            detalle = self._extraer_error(response)
            raise FelRechazoError(detalle or f"Respuesta inesperada {response.status_code}.")

        data = response.json()
        return fel_schema.FelCertificacionRespuesta.model_validate(data)

    @staticmethod
    def _extraer_error(response: httpx.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return (
                    data.get("detail")
                    or data.get("mensaje")
                    or data.get("error")
                    or "El certificador rechazó la factura."
                )
            return str(data)
        except Exception:
            return response.text or "El certificador rechazó la factura."

    # ------------------------------------------------------------------
    # Operaciones principales
    # ------------------------------------------------------------------
    async def emitir_factura(
        self,
        *,
        id_venta: int,
        total,
        nit_receptor: str,
        nombre_receptor: str = "",
        items: Optional[list] = None,
    ) -> FacturaFel:
        total = Decimal(str(total))
        nit = (nit_receptor or "").strip()
        nombre = (nombre_receptor or "").strip()

        self._validar_totales(total, items)
        self._validar_cf(nit, total)

        request = fel_schema.FelEmisionRequest(
            id_venta=id_venta,
            nit_receptor=nit or "CF",
            nombre_receptor=nombre,
            total=total,
            items=[
                fel_schema.FelItem(**item) if isinstance(item, dict) else item
                for item in (items or [])
            ],
        )

        try:
            respuesta = await self._certificar(request)
        except FelRechazoError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Rechazado: {exc.detalle}",
            )
        except FelServicioNoDisponible:
            return await self._registrar_contingencia(
                id_venta=id_venta,
                nit=nit,
                nombre=nombre,
                total=total,
            )

        factura = FacturaFel(
            id_venta=id_venta,
            numero_autorizacion_sat=respuesta.uuid,
            serie=respuesta.serie or self.settings.FEL_SERIE,
            numero_dte=f"{respuesta.serie or self.settings.FEL_SERIE}-{respuesta.numero}",
            fecha_certificacion=respuesta.fecha or datetime.now(),
            nit_receptor=nit or "CF",
            nombre_receptor=nombre or "Consumidor Final",
            total_facturado=total,
            estado=ESTADO_CERTIFICADA,
        )
        return await self.uow.fel.create(factura)

    async def _registrar_contingencia(
        self, *, id_venta: int, nit: str, nombre: str, total: Decimal
    ) -> FacturaFel:
        """Registra la factura en contingencia sin revertir la venta."""
        factura = FacturaFel(
            id_venta=id_venta,
            numero_autorizacion_sat=None,
            serie=None,
            numero_dte=None,
            fecha_certificacion=None,
            nit_receptor=nit or "CF",
            nombre_receptor=nombre or "Consumidor Final",
            total_facturado=total,
            estado=ESTADO_CONTINGENCIA,
        )
        return await self.uow.fel.create(factura)

    async def reintentar_certificacion(self, id_venta: int) -> FacturaFel:
        factura = await self.uow.fel.get_by_venta(id_venta)
        if not factura:
            raise HTTPException(status_code=404, detail="No existe factura FEL para la venta indicada.")
        if factura.estado not in (ESTADO_PENDIENTE, ESTADO_CONTINGENCIA):
            raise HTTPException(
                status_code=400,
                detail="La factura ya está certificada; no requiere reintento.",
            )

        request = fel_schema.FelEmisionRequest(
            id_venta=factura.id_venta,
            nit_receptor=factura.nit_receptor,
            nombre_receptor=factura.nombre_receptor,
            total=factura.total_facturado,
        )

        try:
            respuesta = await self._certificar(request)
        except FelRechazoError as exc:
            raise HTTPException(status_code=400, detail=f"Rechazado: {exc.detalle}")
        except FelServicioNoDisponible:
            factura.estado = ESTADO_PENDIENTE
            return await self.uow.fel.update(factura)

        factura.numero_autorizacion_sat = respuesta.uuid
        factura.serie = respuesta.serie or self.settings.FEL_SERIE
        factura.numero_dte = f"{respuesta.serie or self.settings.FEL_SERIE}-{respuesta.numero}"
        factura.fecha_certificacion = respuesta.fecha or datetime.now()
        factura.estado = ESTADO_CERTIFICADA
        return await self.uow.fel.update(factura)

    async def listar_pendientes(self, limit: int = 100) -> List[FacturaFel]:
        return await self.uow.fel.list_pendientes(limit)
