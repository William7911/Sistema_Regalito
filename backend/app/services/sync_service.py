from typing import Dict, Any
from app.interfaces.repositories import SyncRepository
from app.interfaces.services import SyncService


class ConcreteSyncService(SyncService):
    """Servicio de sincronización offline: orquesta la réplica de datos maestros a SQLite local."""

    def __init__(self, repository: SyncRepository):
        self.repository = repository

    async def pull_and_replicate_to_local(self) -> Dict[str, Any]:
        """Extrae el catálogo, precios, usuarios y auxiliares de la nube y los vuelca en SQLite local."""
        snapshot = await self.repository.fetch_cloud_snapshot()
        result = await self.repository.replicate_to_sqlite(snapshot)
        return result

    async def get_sync_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la base de datos SQLite local."""
        return await self.repository.get_sqlite_status()

    async def get_local_preview(self) -> Dict[str, Any]:
        """Obtiene la vista previa de productos con precios y usuarios leídos desde la copia local."""
        return await self.repository.get_sqlite_preview()

