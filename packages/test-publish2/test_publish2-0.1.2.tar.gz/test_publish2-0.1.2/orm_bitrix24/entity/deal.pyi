from typing import List, Dict, Any, Optional, ClassVar, Type, Union, Awaitable, Coroutine, TypeVar
import datetime
from fast_bitrix24 import Bitrix

from .base import BaseEntity, EntityManager, RelatedManager, CustomField, TextCustomField, SelectCustomField

T = TypeVar('T', bound=BaseEntity)

class Product:
    _data: Dict[str, Any]
    
    def __init__(self, product_data: Dict[str, Any] = None) -> None: ...
    
    @property
    def id(self) -> Optional[str]: ...
    
    @property
    def price(self) -> float: ...
    
    @price.setter
    def price(self, value: float) -> None: ...
    
    @property
    def quantity(self) -> float: ...
    
    @quantity.setter
    def quantity(self, value: float) -> None: ...
    
    @property
    def discount_rate(self) -> float: ...
    
    @discount_rate.setter
    def discount_rate(self, value: float) -> None: ...
    
    @property
    def discount_sum(self) -> float: ...
    
    @discount_sum.setter
    def discount_sum(self, value: float) -> None: ...
    
    def to_dict(self) -> Dict[str, Any]: ...


class DealNote:
    id: Optional[str]
    text: str
    created_at: datetime.datetime
    author_id: Optional[int]
    entity_id: Optional[str]
    entity_type: str
    
    def __init__(self, bitrix: Bitrix, deal: Optional['Deal'] = None, data: Optional[Dict[str, Any]] = None) -> None: ...
    
    def __str__(self) -> str: ...


class DealNoteManager:
    async def create(self, **kwargs) -> DealNote: ...
    async def filter(self, **kwargs) -> List[DealNote]: ...


class ProductsManager:
    def __init__(self, bitrix: Bitrix, deal: 'Deal') -> None: ...
    
    async def get_all(self) -> List[Product]: ...
    
    def add(self, product_id: str, price: float, quantity: float = 1, 
            tax_rate: float = 0, tax_included: bool = True, 
            discount_sum: float = 0, discount_rate: float = 0) -> Product: ...
    
    def clear(self) -> None: ...
    
    async def save(self) -> None: ...


class Company:
    id: Optional[int]
    title: str
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    # Добавляем objects для автодополнения
    objects: ClassVar[EntityManager['Company']]
    
    @classmethod
    def get_manager(cls, bitrix: Bitrix) -> EntityManager['Company']: ...
    
    @classmethod
    async def get_by_id(cls, bitrix: Bitrix, entity_id: Union[str, int]) -> Optional['Company']: ...


class Contact:
    id: Optional[int]
    name: str
    last_name: str
    second_name: str
    email: str
    phone: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class DealEntityManager(EntityManager['Deal']):
    """Кастомный менеджер сделок для правильной типизации"""
    async def get_all(self) -> List['Deal']: ...
    async def filter(self, **kwargs) -> List['Deal']: ...
    async def create(self, **kwargs) -> 'Deal': ...
    async def get_by_id(self, deal_id: Union[str, int]) -> Optional['Deal']: ...
    


class Deal(BaseEntity):
    ENTITY_NAME: ClassVar[str]
    ENTITY_METHOD: ClassVar[str]
    objects: ClassVar[DealEntityManager]
    
    # Публичные поля
    id: Optional[int]
    title: str
    opportunity: float
    currency_id: str
    stage_id: str
    probability: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed: bool
    comments: str
    type_id: str
    
    # Связанные сущности
    company_id: Optional[int]
    contact_id: Optional[int]
    assigned_by_id: Optional[int]
    
    # Связанные объекты - могут возвращать корутины или готовые объекты
    company: Union[Awaitable[Optional[Company]], Optional[Company]]
    contact: Union[Awaitable[Optional[Contact]], Optional[Contact]]
    
    tags: List[str]
    
    # Менеджеры
    notes: DealNoteManager
    products: ProductsManager
    
    # Пользовательские поля добавляются через наследование
    # см. пример в main.py:
    # class Deal(_Deal):
    #     utm_source = CustomField("UTM_SOURCE")
    #     delivery_address = TextCustomField("UF_CRM_DELIVERY_ADDRESS")
    
    def __init__(self, bitrix: Bitrix, data: Optional[Dict[str, Any]] = None) -> None: ...
    
    def __str__(self) -> str: ...
    
    @classmethod
    def get_manager(cls, bitrix: Bitrix) -> EntityManager['Deal']: ...
    
    @classmethod
    def add_custom_field(cls, name: str, field: Any) -> None: ...
    
    async def save(self) -> 'Deal': ...
    
    @classmethod
    async def get_by_id(cls, bitrix: Bitrix, entity_id: Union[str, int]) -> Optional['Deal']: ... 
    async def delete(self) -> bool: ...