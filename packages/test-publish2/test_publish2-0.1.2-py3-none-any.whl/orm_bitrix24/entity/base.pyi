from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Union, Callable, Protocol
import datetime
from fast_bitrix24 import Bitrix

T = TypeVar('T', bound='BaseEntity')

V = TypeVar('V')

class Field(Generic[V]):
    field_name: str
    nullable: bool
    name: str

    def __init__(self, field_name: str, nullable: bool = True) -> None: ...
    def __set_name__(self, owner: Type, name: str) -> None: ...
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[V, 'Field[V]']: ...
    def __set__(self, instance: 'BaseEntity', value: V) -> None: ...


class IntegerField(Field[int]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[int], 'IntegerField']: ...


class StringField(Field[str]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[str], 'StringField']: ...


class FloatField(Field[float]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[float], 'FloatField']: ...


class DateTimeField(Field[datetime.datetime]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[datetime.datetime], 'DateTimeField']: ...


class BooleanField(Field[bool]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[bool, 'BooleanField']: ...


class RelatedEntityField(Field[T]):
    related_entity: Type[T]
    
    def __init__(self, field_name: str, related_entity: Type[T], nullable: bool = True) -> None: ...
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[T], 'RelatedEntityField[T]']: ...


class ListField(Field[List[Any]]):
    def __init__(self, field_name: str, nullable: bool = True) -> None: ...
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[List[Any], 'ListField']: ...


class CustomField(Field[Any]):
    field_title: str
    isMultiple: bool
    field_name: str
    
    def __init__(self, field_title: str, isMultiple: bool = False) -> None: ...
    def __set_name__(self, owner: Type, name: str) -> None: ...


class TextCustomField(CustomField): ...


class SelectCustomField(CustomField): ...


class UrlCustomField(CustomField): ...


class EntityManager(Generic[T]):
    _bitrix: Bitrix
    _entity_class: Type[T]
    
    def __init__(self, bitrix: Bitrix, entity_class: Type[T]) -> None: ...
    async def filter(self, **kwargs) -> List[T]: ...
    async def get_all(self) -> List[T]: ...
    async def create(self, **kwargs) -> T: ...


class RelatedManager(Generic[T]):
    _bitrix: Bitrix
    _parent_entity: 'BaseEntity'
    _related_entity_class: Type[T]
    
    def __init__(self, bitrix: Bitrix, parent_entity: 'BaseEntity', related_entity_class: Type[T]) -> None: ...
    async def create(self, **kwargs) -> T: ...
    async def filter(self, **kwargs) -> List[T]: ...


class BaseEntity:
    ENTITY_NAME: Optional[str]
    ENTITY_METHOD: Optional[str]
    objects: EntityManager[Any]
    
    _bitrix: Bitrix
    _data: Dict[str, Any]
    _dirty_fields: set
    _related: Dict[str, Any]
    
    id: Optional[Union[str, int]]
    
    def __init__(self, bitrix: Bitrix, data: Optional[Dict[str, Any]] = None) -> None: ...
    
    @classmethod
    def get_entity_manager(cls, bitrix: Bitrix) -> EntityManager[T]: ...
    
    async def save(self) -> None: ...
    
    @classmethod
    async def get_by_id(cls: Type[T], bitrix: Bitrix, entity_id: Union[str, int]) -> Optional[T]: ... 