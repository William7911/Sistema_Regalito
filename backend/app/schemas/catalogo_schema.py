"""
Schemas Pydantic v2 para los módulos de catálogos CRUD:
  - TipoCliente
  - Cliente + ClienteContacto
  - Sucursal
  - AreaBodega
  - Subcategoria
  - UnidadMedida
  - MotivoMerma
  - MetodoPago
  - Proveedor
  - DepartamentoGeografico
  - Municipio
  - Permiso / RolPermiso
  - BitacoraAuditoria (solo lectura)
  - HistorialPrecio (solo lectura)
  - VisitaSeguimiento + VisitaModuloEvaluacion
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ESTADO_OPTS = {"Activo", "Inactivo"}


def _validate_estado(v: str) -> str:
    if v not in ESTADO_OPTS:
        raise ValueError("estado debe ser 'Activo' o 'Inactivo'")
    return v


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
        if v is not None:
            return _validate_estado(v)
        return v


class TipoClienteOut(BaseModel):
    id_tipo_cliente: int
    nombre: str
    descuento_predeterminado: Optional[Decimal] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)


class TipoClienteList(BaseModel):
    total: int
    items: List[TipoClienteOut]


# ---------------------------------------------------------------------------
# ClienteContacto
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

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
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

    model_config = ConfigDict(from_attributes=True)


class ClienteFilter(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    id_tipo_cliente: Optional[int] = None
    is_active: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ClienteList(BaseModel):
    total: int
    items: List[ClienteOut]


# ---------------------------------------------------------------------------
# Sucursal
# ---------------------------------------------------------------------------

class SucursalCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    direccion: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=20)


class SucursalUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    direccion: Optional[str] = Field(default=None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=20)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class SucursalFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    sort_by: Optional[str] = "nombre"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class SucursalOut(BaseModel):
    id_sucursal: int
    nombre: str
    direccion: str
    telefono: Optional[str] = None
    estado: str
    fecha_creacion: Optional[datetime] = None
    total_areas: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SucursalList(BaseModel):
    total: int
    items: List[SucursalOut]


# ---------------------------------------------------------------------------
# AreaBodega
# ---------------------------------------------------------------------------

class AreaBodegaFilter(BaseModel):
    search: Optional[str] = None
    id_sucursal: Optional[int] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "nombre_area"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class AreaBodegaCreate(BaseModel):
    id_sucursal: int
    nombre_area: str = Field(..., min_length=1, max_length=50)


class AreaBodegaUpdate(BaseModel):
    nombre_area: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class AreaBodegaOut(BaseModel):
    id_area: int
    id_sucursal: int
    nombre_area: str
    estado: str
    sucursal_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AreaBodegaList(BaseModel):
    total: int
    items: List[AreaBodegaOut]


# ---------------------------------------------------------------------------
# Subcategoria
# ---------------------------------------------------------------------------

class SubcategoriaFilter(BaseModel):
    search: Optional[str] = None
    id_categoria: Optional[int] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "nombre"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class SubcategoriaCreate(BaseModel):
    id_categoria: int
    nombre: str = Field(..., min_length=1, max_length=50)


class SubcategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class SubcategoriaOut(BaseModel):
    id_subcategoria: int
    id_categoria: int
    nombre: str
    estado: str
    categoria_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SubcategoriaList(BaseModel):
    total: int
    items: List[SubcategoriaOut]


# ---------------------------------------------------------------------------
# UnidadMedida
# ---------------------------------------------------------------------------

class UnidadMedidaFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "descripcion"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class UnidadMedidaCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=10)
    descripcion: str = Field(..., min_length=1, max_length=50)


class UnidadMedidaUpdate(BaseModel):
    codigo: Optional[str] = Field(default=None, min_length=1, max_length=10)
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class UnidadMedidaOut(BaseModel):
    id_unidad: int
    codigo: str
    descripcion: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class UnidadMedidaList(BaseModel):
    total: int
    items: List[UnidadMedidaOut]


# ---------------------------------------------------------------------------
# MotivoMerma
# ---------------------------------------------------------------------------

class MotivoMermaCreate(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=100)


class MotivoMermaUpdate(BaseModel):
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=100)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class MotivoMermaOut(BaseModel):
    id_motivo: int
    descripcion: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class MotivoMermaList(BaseModel):
    total: int
    items: List[MotivoMermaOut]


class MotivoMermaFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "descripcion"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# MetodoPago
# ---------------------------------------------------------------------------

class MetodoPagoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=30)


class MetodoPagoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=30)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class MetodoPagoOut(BaseModel):
    id_metodo_pago: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class MetodoPagoList(BaseModel):
    total: int
    items: List[MetodoPagoOut]


class MetodoPagoFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "nombre"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Proveedor
# ---------------------------------------------------------------------------

class ProveedorCreate(BaseModel):
    nombre_contacto: str = Field(..., min_length=1, max_length=100)
    distribuidora: str = Field(..., min_length=1, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)
    cuenta_bancaria: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=150)


class ProveedorUpdate(BaseModel):
    nombre_contacto: Optional[str] = Field(default=None, min_length=1, max_length=100)
    distribuidora: Optional[str] = Field(default=None, min_length=1, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)
    cuenta_bancaria: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=150)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class ProveedorOut(BaseModel):
    id_proveedor: int
    nombre_contacto: str
    distribuidora: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    cuenta_bancaria: Optional[str] = None
    direccion: Optional[str] = None
    estado: str
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProveedorFilter(BaseModel):
    search: Optional[str] = None
    nombre: Optional[str] = None
    distribuidora: Optional[str] = None
    is_active: Optional[bool] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    sort_by: Optional[str] = "distribuidora"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ProveedorList(BaseModel):
    total: int
    items: List[ProveedorOut]


# ---------------------------------------------------------------------------
# DepartamentoGeografico
# ---------------------------------------------------------------------------

class DepartamentoOut(BaseModel):
    id_departamento: int
    nombre: str
    estado: str
    total_municipios: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DepartamentoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)


class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class DepartamentoFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "nombre"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class DepartamentoList(BaseModel):
    total: int
    items: List[DepartamentoOut]


# ---------------------------------------------------------------------------
# Municipio
# ---------------------------------------------------------------------------

class MunicipioCreate(BaseModel):
    id_departamento: int
    nombre: str = Field(..., min_length=1, max_length=50)


class MunicipioUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None:
            return _validate_estado(v)
        return v


class MunicipioOut(BaseModel):
    id_municipio: int
    id_departamento: int
    nombre: str
    estado: str
    departamento_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MunicipioFilter(BaseModel):
    search: Optional[str] = None
    id_departamento: Optional[int] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = "nombre"
    sort_order: Optional[str] = "asc"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class MunicipioList(BaseModel):
    total: int
    items: List[MunicipioOut]


# ---------------------------------------------------------------------------
# Permiso
# ---------------------------------------------------------------------------

class PermisoCreate(BaseModel):
    modulo: str = Field(..., min_length=1, max_length=50)
    codigo: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=150)


class PermisoUpdate(BaseModel):
    modulo: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=150)


class PermisoOut(BaseModel):
    id_permiso: int
    modulo: str
    codigo: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RolPermisoAssign(BaseModel):
    id_permiso: int


class RolePermisosUpdate(BaseModel):
    """Cuerpo para reemplazar los permisos asignados a un rol."""
    codigos: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# BitacoraAuditoria (solo lectura)
# ---------------------------------------------------------------------------

class BitacoraOut(BaseModel):
    id_bitacora: int
    id_usuario: int
    tabla_afectada: str
    accion: str
    descripcion: str
    fecha_hora: datetime
    usuario_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BitacoraFilter(BaseModel):
    id_usuario: Optional[int] = None
    tabla: Optional[str] = None
    accion: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class BitacoraList(BaseModel):
    total: int
    items: List[BitacoraOut]


# ---------------------------------------------------------------------------
# HistorialPrecio (solo lectura)
# ---------------------------------------------------------------------------

class HistorialPrecioOut(BaseModel):
    id_historial: int
    id_variante: int
    id_usuario: int
    precio_anterior: Decimal
    precio_nuevo: Decimal
    fecha_modificacion: datetime
    producto_id: Optional[int] = None
    producto_nombre: Optional[str] = None
    variante_codigo_barras: Optional[str] = None
    usuario_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HistorialPrecioFilter(BaseModel):
    id_producto: Optional[int] = None
    id_variante: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class HistorialPrecioList(BaseModel):
    total: int
    items: List[HistorialPrecioOut]


# ---------------------------------------------------------------------------
# VisitaSeguimiento + VisitaModuloEvaluacion
# ---------------------------------------------------------------------------

class VisitaModuloCreate(BaseModel):
    nombre_modulo: str = Field(..., min_length=1, max_length=100)
    calificacion: Optional[int] = Field(default=None, ge=1, le=10)
    comentario: Optional[str] = None


class VisitaModuloOut(BaseModel):
    id_modulo_eval: int
    id_visita: int
    nombre_modulo: str
    calificacion: Optional[int] = None
    comentario: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VisitaCreate(BaseModel):
    id_cliente: int
    fecha_visita: date
    observaciones: Optional[str] = None
    modulos: Optional[List[VisitaModuloCreate]] = None


class VisitaUpdate(BaseModel):
    fecha_visita: Optional[date] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def check_estado(cls, v):
        if v is not None and v not in {"Pendiente", "Completada", "Cancelada"}:
            raise ValueError("estado debe ser Pendiente, Completada o Cancelada")
        return v


class VisitaOut(BaseModel):
    id_visita: int
    id_cliente: int
    id_usuario: int
    fecha_visita: date
    observaciones: Optional[str] = None
    estado: str
    fecha_creacion: datetime
    modulos: List[VisitaModuloOut] = []

    model_config = ConfigDict(from_attributes=True)


class VisitaFilter(BaseModel):
    id_cliente: Optional[int] = None
    id_usuario: Optional[int] = None
    estado: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class VisitaList(BaseModel):
    total: int
    items: List[VisitaOut]

