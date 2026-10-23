from pydantic import BaseModel, Field
from typing import Optional

class ConfiguracionUpdate(BaseModel):
    nit: str = Field(..., alias="NIT", description="NIT de la empresa")
    razon_social: str = Field(..., alias="Razón Social", description="Razón Social de la empresa")
    direccion: Optional[str] = Field(None, alias="Dirección", description="Dirección de la empresa")
    token_fel: str = Field(..., alias="Token FEL", description="Token para facturación electrónica")

    class Config:
        populate_by_name = True

class ConfiguracionResponse(BaseModel):
    nit: str = Field(..., alias="NIT")
    razon_social: str = Field(..., alias="Razón Social")
    direccion: Optional[str] = Field(None, alias="Dirección")
    token_fel: str = Field(..., alias="Token FEL")
    
    class Config:
        populate_by_name = True
