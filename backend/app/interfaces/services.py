from abc import ABC, abstractmethod
from typing import Optional, List
from app.schemas import schemas


class RoleService(ABC):
    """Contrato de la lógica de negocio de Roles."""

    @abstractmethod
    async def list_roles(self, include_inactive: bool = False) -> List[schemas.Role]:
        ...

    @abstractmethod
    async def get_role(self, role_id: int) -> schemas.Role:
        ...

    @abstractmethod
    async def create_role(self, data: schemas.RoleCreate) -> schemas.Role:
        ...

    @abstractmethod
    async def update_role(self, role_id: int, data: schemas.RoleUpdate) -> schemas.Role:
        ...

    @abstractmethod
    async def deactivate_role(self, role_id: int) -> schemas.Role:
        ...


class DepartmentService(ABC):
    """Contrato de la lógica de negocio de Departamentos."""

    @abstractmethod
    async def list_departments(self, include_inactive: bool = False) -> List[schemas.Department]:
        ...

    @abstractmethod
    async def get_department(self, department_id: int) -> schemas.Department:
        ...

    @abstractmethod
    async def create_department(self, data: schemas.DepartmentCreate) -> schemas.Department:
        ...

    @abstractmethod
    async def update_department(
        self, department_id: int, data: schemas.DepartmentUpdate
    ) -> schemas.Department:
        ...

    @abstractmethod
    async def deactivate_department(self, department_id: int) -> schemas.Department:
        ...


class UserService(ABC):
    """Contrato de la lógica de negocio de Usuarios."""

    @abstractmethod
    async def list_users(self, filters: schemas.UserFilter) -> List[schemas.UserResponse]:
        ...

    @abstractmethod
    async def count_users(self, filters: schemas.UserFilter) -> int:
        ...

    @abstractmethod
    async def get_user(self, user_id: int) -> schemas.UserResponse:
        ...

    @abstractmethod
    async def create_user(self, data: schemas.UserCreate) -> schemas.UserResponse:
        ...

    @abstractmethod
    async def update_user(
        self, user_id: int, data: schemas.UserUpdate
    ) -> schemas.UserResponse:
        ...

    @abstractmethod
    async def deactivate_user(self, user_id: int) -> schemas.UserResponse:
        ...


class CategoryService(ABC):
    """Contrato de la lógica de negocio de Categorías."""

    @abstractmethod
    async def list_categories(self, include_inactive: bool = False) -> List[schemas.CategoriaOut]:
        ...

    @abstractmethod
    async def get_category(self, category_id: int) -> schemas.CategoriaOut:
        ...

    @abstractmethod
    async def create_category(self, data: schemas.CategoriaCreate) -> schemas.CategoriaOut:
        ...

    @abstractmethod
    async def update_category(
        self, category_id: int, data: schemas.CategoriaUpdate
    ) -> schemas.CategoriaOut:
        ...

    @abstractmethod
    async def deactivate_category(self, category_id: int) -> schemas.CategoriaOut:
        ...


class ProductService(ABC):
    """Contrato de la lógica de negocio de Productos (inserción anidada)."""

    @abstractmethod
    async def list_products(self, filters: schemas.ProductoFilter) -> List[schemas.ProductoOut]:
        ...

    @abstractmethod
    async def count_products(self, filters: schemas.ProductoFilter) -> int:
        ...

    @abstractmethod
    async def get_product(self, product_id: int) -> schemas.ProductoOut:
        ...

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> schemas.ProductoOut:
        ...

    @abstractmethod
    async def create_product(self, data: schemas.ProductoCreate) -> schemas.ProductoOut:
        ...

    @abstractmethod
    async def update_product(
        self, product_id: int, data: schemas.ProductoUpdate
    ) -> schemas.ProductoOut:
        ...

    @abstractmethod
    async def deactivate_product(self, product_id: int) -> schemas.ProductoOut:
        ...


class CatalogoService(ABC):
    """Contrato de la lógica de negocio de catálogos de apoyo (dropdowns)."""

    @abstractmethod
    async def list_subcategorias(self, include_inactive: bool = False) -> List[schemas.SubcategoriaOut]:
        ...

    @abstractmethod
    async def list_unidades(self) -> List[schemas.UnidadMedidaOut]:
        ...

    @abstractmethod
    async def list_sucursales(self, include_inactive: bool = False) -> List[schemas.SucursalOut]:
        ...

    @abstractmethod
    async def list_areas(self, sucursal_id: Optional[int] = None) -> List[schemas.AreaBodegaOut]:
        ...