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

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None

class Role(RoleBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Departamentos
# ---------------------------------------------------------------------------

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None

class Department(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30)
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    role_id: int
    department_id: int

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(default=None, min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, min_length=1, max_length=30)
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    name: str
    lastname: str
    code: str
    username: str
    role_id: int
    department_id: int
    is_active: bool
    created_at: datetime
    role: Optional[Role] = None
    department: Optional[Department] = None

    model_config = ConfigDict(from_attributes=True)

class UserFilter(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    created_from: Optional[str] = None
    created_to: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class UserList(BaseModel):
    total: int
    items: List[UserResponse]

# ---------------------------------------------------------------------------
# Categorías
# ---------------------------------------------------------------------------

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None

class Category(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: Optional[str] = Field(default=None, max_length=50)
    barcode: str = Field(..., max_length=100)
    category_id: int
    price: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    current_stock: int = Field(default=0, ge=0)
    min_stock: int = Field(default=5, ge=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    sku: Optional[str] = Field(default=None, max_length=50)
    barcode: Optional[str] = Field(default=None, max_length=100)
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, gt=0)
    current_stock: Optional[int] = Field(default=None, ge=0)
    min_stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

class ProductFilter(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    created_from: Optional[str] = None
    created_to: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    category: Optional[Category] = None

    model_config = ConfigDict(from_attributes=True)

class ProductList(BaseModel):
    total: int
    items: List[Product]

# ---------------------------------------------------------------------------
# Caja registradora
# ---------------------------------------------------------------------------

class CashRegisterOpen(BaseModel):
    opening_amount: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)
    petty_cash: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)

class CashRegisterClose(BaseModel):
    blind_closing_amount: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

class CashRegisterResponse(BaseModel):
    id: int
    user_id: int
    opening_time: datetime
    opening_amount: Decimal
    petty_cash: Decimal
    status: str
    closing_time: Optional[datetime] = None
    blind_closing_amount: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)