from abc import ABC, abstractmethod
from typing import Optional, List
from app.db.models import (
    Categoria, Subcategoria, UnidadMedida, Sucursal, AreaBodega,
    Producto, VarianteProducto, InventarioSucursal,
    Rol, DepartamentoGeografico, Usuario,
    Caja, TurnoCaja,
)


class RoleRepository(ABC):
    """Contrato de acceso a datos para Roles (modelo relacional Rol)."""

    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[Rol]:
        ...

    @abstractmethod
    async def get_by_name(self, nombre: str) -> Optional[Rol]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Rol]:
        ...

    @abstractmethod
    async def create(self, rol: Rol) -> Rol:
        ...

    @abstractmethod
    async def update(self, rol: Rol) -> Rol:
        ...


class DepartmentRepository(ABC):
    """Contrato de acceso a datos para Departamentos (modelo relacional DepartamentoGeografico)."""

    @abstractmethod
    async def get_by_id(self, department_id: int) -> Optional[DepartamentoGeografico]:
        ...

    @abstractmethod
    async def get_by_name(self, nombre: str) -> Optional[DepartamentoGeografico]:
        ...

    @abstractmethod
    async def list_all(self) -> List[DepartamentoGeografico]:
        ...

    @abstractmethod
    async def create(self, department: DepartamentoGeografico) -> DepartamentoGeografico:
        ...

    @abstractmethod
    async def update(self, department: DepartamentoGeografico) -> DepartamentoGeografico:
        ...


class UserRepository(ABC):
    """Contrato de acceso a datos para Usuarios (modelo relacional Usuario)."""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Usuario]:
        ...

    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        created_from=None,
        created_to=None,
        sort_by: Optional[str] = None,
        sort_dir: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Usuario]:
        ...

    @abstractmethod
    async def count_search(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        created_from=None,
        created_to=None,
    ) -> int:
        ...

    @abstractmethod
    async def create(self, user: Usuario) -> Usuario:
        ...

    @abstractmethod
    async def update(self, user: Usuario) -> Usuario:
        ...


class CategoryRepository(ABC):
    """Contrato de acceso a datos para Categorías (modelo relacional)."""

    @abstractmethod
    async def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        ...

    @abstractmethod
    async def get_by_name(self, nombre: str) -> Optional[Categoria]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Categoria]:
        ...

    @abstractmethod
    async def create(self, categoria: Categoria) -> Categoria:
        ...

    @abstractmethod
    async def update(self, categoria: Categoria) -> Categoria:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...


class ProductRepository(ABC):
    """Contrato de acceso a datos para Productos (estructura relacional)."""

    @abstractmethod
    async def get_producto_by_id(self, producto_id: int) -> Optional[Producto]:
        ...

    @abstractmethod
    async def get_variante_by_barcode(self, codigo_barras: str) -> Optional[VarianteProducto]:
        ...

    @abstractmethod
    async def get_variante_by_id(self, variante_id: int) -> Optional[VarianteProducto]:
        ...

    @abstractmethod
    async def get_inventario_by_id(self, inventario_id: int) -> Optional[InventarioSucursal]:
        ...

    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        subcategoria_id: Optional[int] = None,
        created_from=None,
        created_to=None,
        sort_by: Optional[str] = None,
        sort_dir: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Producto]:
        ...

    @abstractmethod
    async def count_search(
        self,
        name: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        subcategoria_id: Optional[int] = None,
        created_from=None,
        created_to=None,
    ) -> int:
        ...

    @abstractmethod
    async def add_producto(self, producto: Producto) -> Producto:
        ...

    @abstractmethod
    async def add_variante(self, variante: VarianteProducto) -> VarianteProducto:
        ...

    @abstractmethod
    async def add_inventario(self, inventario: InventarioSucursal) -> InventarioSucursal:
        ...

    @abstractmethod
    async def get_subcategoria_by_id(self, subcategoria_id: int) -> Optional[Subcategoria]:
        ...

    @abstractmethod
    async def get_unidad_by_id(self, unidad_id: int) -> Optional[UnidadMedida]:
        ...

    @abstractmethod
    async def get_sucursal_by_id(self, sucursal_id: int) -> Optional[Sucursal]:
        ...

    @abstractmethod
    async def get_area_by_id(self, area_id: int) -> Optional[AreaBodega]:
        ...

    @abstractmethod
    async def list_subcategorias(self, include_inactive: bool = False) -> List[Subcategoria]:
        ...

    @abstractmethod
    async def list_unidades(self) -> List[UnidadMedida]:
        ...

    @abstractmethod
    async def list_sucursales(self, include_inactive: bool = False) -> List[Sucursal]:
        ...

    @abstractmethod
    async def list_areas(self, sucursal_id: Optional[int] = None) -> List[AreaBodega]:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...


class CajaRepository(ABC):
    """Contrato de acceso a datos para Cajas (modelo relacional Caja)."""

    @abstractmethod
    async def get_by_id(self, caja_id: int) -> Optional[Caja]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Caja]:
        ...

    @abstractmethod
    async def create(self, caja: Caja) -> Caja:
        ...

    @abstractmethod
    async def update(self, caja: Caja) -> Caja:
        ...


class TurnoCajaRepository(ABC):
    """Contrato de acceso a datos para Turnos de Caja (modelo relacional TurnoCaja)."""

    @abstractmethod
    async def get_by_id(self, turno_id: int) -> Optional[TurnoCaja]:
        ...

    @abstractmethod
    async def get_active_by_user(self, user_id: int) -> Optional[TurnoCaja]:
        ...

    @abstractmethod
    async def get_active_by_caja(self, caja_id: int) -> Optional[TurnoCaja]:
        ...

    @abstractmethod
    async def search(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        estado: Optional[str] = None,
        id_caja: Optional[int] = None,
        id_usuario: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_dir: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> List[TurnoCaja]:
        ...

    @abstractmethod
    async def count_search(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        estado: Optional[str] = None,
        id_caja: Optional[int] = None,
        id_usuario: Optional[int] = None,
    ) -> int:
        ...

    @abstractmethod
    async def create(self, turno: TurnoCaja) -> TurnoCaja:
        ...

    @abstractmethod
    async def update(self, turno: TurnoCaja) -> TurnoCaja:
        ...