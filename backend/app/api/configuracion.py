from fastapi import APIRouter, Depends
from app.api.deps import get_configuracion_service, require_admin
from app.schemas.configuracion_schema import ConfiguracionUpdate
from app.services.configuracion_service import ConfiguracionService
from app.db.models import Usuario

router = APIRouter(prefix="/api/configuracion", tags=["Configuración"])

@router.get("/", response_model=dict)
async def obtener_configuracion(
    current_user: Usuario = Depends(require_admin),
    service: ConfiguracionService = Depends(get_configuracion_service)
):
    return await service.obtener_configuracion(usuario_actual=current_user)

@router.put("/")
async def actualizar_configuracion(
    payload: ConfiguracionUpdate,
    current_user: Usuario = Depends(require_admin),
    service: ConfiguracionService = Depends(get_configuracion_service)
):
    update_data = payload.dict(by_alias=True)
    await service.actualizar_configuracion(parametros=update_data, usuario_actual=current_user)
    return {"message": "Configuración actualizada exitosamente"}
