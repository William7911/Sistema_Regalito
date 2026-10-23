from fastapi import APIRouter, Depends, HTTPException, status
from app.interfaces.services import HealthService
from app.api.deps import get_health_service

router = APIRouter()

@router.get("")
async def check_health(health_service: HealthService = Depends(get_health_service)):
    result = await health_service.check_health()
    if result["status"] != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )
    return result
