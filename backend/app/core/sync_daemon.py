import asyncio
import logging
from app.db.database import AsyncSessionLocal
from app.api.deps import UnitOfWork
from app.services.facturacion_offline_service import FacturacionOfflineService

logger = logging.getLogger(__name__)

class SyncDaemon:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self._task = None
        self._running = False

    async def start(self):
        """Inicia el bucle del daemon en segundo plano."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info(f"SyncEngine Daemon iniciado (intervalo: {self.interval_seconds}s)")

    async def stop(self):
        """Detiene el bucle de manera limpia."""
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("SyncEngine Daemon detenido limpiamente.")

    async def _run_loop(self):
        """Bucle infinito que procesa la cola cada X segundos."""
        while self._running:
            try:
                await self._process_queue()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Manejo de errores silencioso: no detenemos la app principal
                logger.error(f"Error inesperado en SyncEngine Daemon: {e}")
            
            # Esperar antes del siguiente ciclo
            await asyncio.sleep(self.interval_seconds)

    async def _process_queue(self):
        """Instancia la DB y ejecuta la sincronización."""
        # Se requiere un contexto nuevo de base de datos por cada ciclo
        async with AsyncSessionLocal() as session:
            try:
                uow = UnitOfWork(session)
                service = FacturacionOfflineService(uow)
                
                # El servicio ya tiene manejo para atrapar errores y marcarlos localmente,
                # pero aseguramos atrapar errores de red a la SAT de forma segura.
                await service.sync_pending_transactions()
                
            except Exception as e:
                logger.error(f"Fallo durante la sincronización de la cola: {e}")
                # Realizar rollback explícito si falló la transacción completa
                await session.rollback()

sync_daemon = SyncDaemon(interval_seconds=30)
