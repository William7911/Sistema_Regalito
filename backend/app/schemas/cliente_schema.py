from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# ---------------------------------------------------------------------------
# TipoCliente
# ---------------------------------------------------------------------------

class TipoClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descuento_predeterminado: Optional[Decimal] = Field(default=None, ge=0, le=100)


class TipoClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descuento_predeterminado: Optional[Decimal] = Field(default=None, ge=0, le=100)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None and v not in ("Activo", "Inactivo"):
            raise ValueError("estado debe ser 'Activo' o 'Inactivo'")
        return v


class TipoClienteOut(BaseModel):
    id_tipo_cliente: int
    nombre: str
    descuento_predeterminado: Optional[Decimal] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)


class MunicipioOut(BaseModel):
    id_municipio: int
    id_departamento: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Contacto de Cliente
# ---------------------------------------------------------------------------

class ClienteContactoCreate(BaseModel):
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)


class ClienteContactoOut(BaseModel):
    id_contacto: int
    id_cliente: int
    telefono: Optional[str] = None
    correo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

class ClienteCreate(BaseModel):
    id_tipo_cliente: int
    id_municipio: Optional[int] = None
    nit: str = Field(..., min_length=1, max_length=15)
    nombre_comercial: str = Field(..., min_length=1, max_length=120)
    direccion: Optional[str] = Field(default=None, max_length=200)
    contactos: Optional[List[ClienteContactoCreate]] = None


class ClienteUpdate(BaseModel):
    id_tipo_cliente: Optional[int] = None
    id_municipio: Optional[int] = None
    nit: Optional[str] = Field(default=None, min_length=1, max_length=15)
    nombre_comercial: Optional[str] = Field(default=None, min_length=1, max_length=120)
    direccion: Optional[str] = Field(default=None, max_length=200)
    estado: Optional[str] = None
    contactos: Optional[List[ClienteContactoCreate]] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None and v not in ("Activo", "Inactivo"):
            raise ValueError("estado debe ser 'Activo' o 'Inactivo'")
        return v


class ClienteOut(BaseModel):
    id_cliente: int
    id_tipo_cliente: int
    id_municipio: Optional[int] = None
    nit: str
    nombre_comercial: str
    direccion: Optional[str] = None
    estado: str
    fecha_creacion: Optional[datetime] = None
    contactos: List[ClienteContactoOut] = []
    tipo_cliente: Optional[TipoClienteOut] = None
    municipio_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClienteFilter(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    id_tipo_cliente: Optional[int] = None
    is_active: Optional[bool] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    sort_by: Optional[str] = "id_cliente"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ClienteList(BaseModel):
    total: int
    items: List[ClienteOut]
