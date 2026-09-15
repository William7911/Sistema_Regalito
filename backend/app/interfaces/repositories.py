from abc import ABC, abstractmethod
from typing import Optional, List
from app.db.models import Category, Product, Role, Department, User


class RoleRepository(ABC):
    """Contrato de acceso a datos para Roles."""

    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Role]:
        ...

    @abstractmethod
    async def create(self, role: Role) -> Role:
        ...

    @abstractmethod
    async def update(self, role: Role) -> Role:
        ...


class DepartmentRepository(ABC):
    """Contrato de acceso a datos para Departamentos."""

    @abstractmethod
    async def get_by_id(self, department_id: int) -> Optional[Department]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Department]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Department]:
        ...

    @abstractmethod
    async def create(self, department: Department) -> Department:
        ...

    @abstractmethod
    async def update(self, department: Department) -> Department:
        ...


class UserRepository(ABC):
    """Contrato de acceso a datos para Usuarios."""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[User]:
        ...

    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        department_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        ...

    @abstractmethod
    async def count_search(
        self,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[int] = None,
        department_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
    ) -> int:
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...


class CategoryRepository(ABC):
    """Contrato de acceso a datos para Categorías."""

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Category]:
        ...

    @abstractmethod
    async def create(self, category: Category) -> Category:
        ...

    @abstractmethod
    async def update(self, category: Category) -> Category:
        ...


class ProductRepository(ABC):
    """Contrato de acceso a datos para Productos."""

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        ...

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        ...

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        ...

    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        ...

    @abstractmethod
    async def count_search(
        self,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
    ) -> int:
        ...

    @abstractmethod
    async def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def update(self, product: Product) -> Product:
        ...