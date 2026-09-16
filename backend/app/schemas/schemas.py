from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Roles (modelo relacional: Rol)
# ---------------------------------------------------------------------------

class RoleCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=150)

class RoleUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=150)
    estado: Optional[str] = Field(default=None, max_length=20)

class Role(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Departamentos (modelo relacional: DepartamentoGeografico)
# ---------------------------------------------------------------------------

class DepartmentCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)

class DepartmentUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)

class Department(BaseModel):
    id_departamento: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Usuarios (modelo relacional: Usuario)
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    id_rol: int

class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    id_rol: Optional[int] = None
    estado: Optional[str] = Field(default=None, max_length=20)

class UserResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombre_completo: str
    username: str
    estado: str
    rol: Optional[Role] = None

    model_config = ConfigDict(from_attributes=True)

class UserFilter(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class UserList(BaseModel):
    total: int
    items: List[UserResponse]

# ---------------------------------------------------------------------------
# Catálogos de apoyo: Categorías / Subcategorías / Unidades / Sucursales / Áreas
# ---------------------------------------------------------------------------

class CategoriaOut(BaseModel):
    id_categoria: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)

class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    estado: Optional[str] = Field(default=None, max_length=20)

class SubcategoriaOut(BaseModel):
    id_subcategoria: int
    id_categoria: int
    nombre: str
    categoria: Optional[CategoriaOut] = None

    model_config = ConfigDict(from_attributes=True)

class UnidadMedidaOut(BaseModel):
    id_unidad: int
    codigo: str
    descripcion: str

    model_config = ConfigDict(from_attributes=True)

class SucursalOut(BaseModel):
    id_sucursal: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)

class AreaBodegaOut(BaseModel):
    id_area: int
    id_sucursal: int
    nombre_area: str

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Productos (estructura relacional: Producto -> VarianteProducto -> Inventario)
# ---------------------------------------------------------------------------

class VarianteCreate(BaseModel):
    codigo_barras: Optional[str] = Field(default=None, max_length=50)
    talla: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default=None, max_length=30)
    precio_detalle: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    precio_mayoreo: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    costo_promedio: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)

class InventarioCreate(BaseModel):
    id_sucursal: int
    id_area: Optional[int] = None
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=0, ge=0)

class ProductoCreate(BaseModel):
    id_subcategoria: int
    id_unidad: int
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    variante: VarianteCreate
    inventario: InventarioCreate

class VarianteUpdate(BaseModel):
    codigo_barras: Optional[str] = Field(default=None, max_length=50)
    talla: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default=None, max_length=30)
    precio_detalle: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, gt=0)
    precio_mayoreo: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, gt=0)
    costo_promedio: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, ge=0)

class InventarioUpdate(BaseModel):
    id_sucursal: Optional[int] = None
    id_area: Optional[int] = None
    stock_actual: Optional[int] = Field(default=None, ge=0)
    stock_minimo: Optional[int] = Field(default=None, ge=0)

class ProductoUpdate(BaseModel):
    id_subcategoria: Optional[int] = None
    id_unidad: Optional[int] = None
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    estado: Optional[str] = Field(default=None, max_length=20)
    variante: Optional[VarianteUpdate] = None
    inventario: Optional[InventarioUpdate] = None

class InventarioOut(BaseModel):
    id_inventario: int
    id_variante: int
    id_sucursal: int
    id_area: Optional[int] = None
    stock_actual: int
    stock_minimo: int

    model_config = ConfigDict(from_attributes=True)

class VarianteOut(BaseModel):
    id_variante: int
    codigo_barras: Optional[str] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    precio_detalle: Decimal
    precio_mayoreo: Decimal
    costo_promedio: Decimal
    inventarios: List[InventarioOut] = []

    model_config = ConfigDict(from_attributes=True)

class ProductoOut(BaseModel):
    id_producto: int
    id_subcategoria: int
    id_unidad: int
    nombre: str
    descripcion: Optional[str] = None
    estado: str
    subcategoria: Optional[SubcategoriaOut] = None
    unidad: Optional[UnidadMedidaOut] = None
    variantes: List[VarianteOut] = []

    model_config = ConfigDict(from_attributes=True)

class ProductoFilter(BaseModel):
    name: Optional[str] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None
    subcategoria_id: Optional[int] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class ProductoList(BaseModel):
    total: int
    items: List[ProductoOut]

# ---------------------------------------------------------------------------
# Caja / Turno de caja (modelos relacionales: Caja, TurnoCaja)
# ---------------------------------------------------------------------------

class TurnoApertura(BaseModel):
    id_caja: int
    monto_apertura: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

class TurnoCierre(BaseModel):
    monto_cierre: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

class TurnoResponse(BaseModel):
    id_turno: int
    id_caja: int
    id_usuario: int
    monto_apertura: Decimal
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)