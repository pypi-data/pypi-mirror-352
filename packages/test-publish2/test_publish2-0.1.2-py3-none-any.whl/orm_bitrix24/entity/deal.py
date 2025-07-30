from typing import ClassVar, Optional, List, Dict, Any, Type, cast, Union, AsyncIterator, TYPE_CHECKING
import datetime

from .base import (
    BaseEntity, StringField, IntegerField, FloatField, DateTimeField, BooleanField,
    RelatedEntityField, ListField, RelatedManager, CustomField, EntityManager
)
from .company import Company
from .contact import Contact
from .note import Note


class Product:
    """Класс для товарных позиций сделки"""
    
    def __init__(self, product_data: Dict[str, Any] = None):
        self._data: Dict[str, Any] = product_data or {}
    
    @property
    def id(self) -> Optional[str]:
        return self._data.get('PRODUCT_ID')
    
    @property
    def price(self) -> float:
        return float(self._data.get('PRICE', 0))
    
    @price.setter
    def price(self, value: float) -> None:
        self._data['PRICE'] = value
    
    @property
    def quantity(self) -> float:
        return float(self._data.get('QUANTITY', 0))
    
    @quantity.setter
    def quantity(self, value: float) -> None:
        self._data['QUANTITY'] = value
    
    @property
    def discount_rate(self) -> float:
        return float(self._data.get('DISCOUNT_RATE', 0))
    
    @discount_rate.setter
    def discount_rate(self, value: float) -> None:
        self._data['DISCOUNT_RATE'] = value
        self._data['DISCOUNT_TYPE_ID'] = 2  # процентный тип скидки
    
    @property
    def discount_sum(self) -> float:
        return float(self._data.get('DISCOUNT_SUM', 0))
    
    @discount_sum.setter
    def discount_sum(self, value: float) -> None:
        self._data['DISCOUNT_SUM'] = value
        self._data['DISCOUNT_TYPE_ID'] = 1  # суммовой тип скидки
    
    def to_dict(self) -> Dict[str, Any]:
        return self._data


class ProductsManager:
    """Менеджер для работы с товарами сделки"""
    
    def __init__(self, bitrix, deal: 'Deal'):
        self._bitrix = bitrix
        self._deal: 'Deal' = deal
        self._products: Optional[List[Product]] = None
        
    async def get_all(self) -> List[Product]:
        """Получение всех товаров сделки"""
        if self._products is None:
            if not self._deal.id:
                self._products = []
            else:
                result = await self._bitrix.call(
                    'crm.deal.productrows.get',
                    {'id': self._deal.id}
                )
                self._products = [Product(item) for item in result]
        return self._products or []
    
    def add(self, product_id: str, price: float, quantity: float = 1, 
            tax_rate: float = 0, tax_included: bool = True, 
            discount_sum: float = 0, discount_rate: float = 0) -> Product:
        """Добавление товара к сделке"""
        if self._products is None:
            self._products = []
        
        product = Product({
            'PRODUCT_ID': product_id,
            'PRICE': price,
            'QUANTITY': quantity,
            'TAX_RATE': tax_rate,
            'TAX_INCLUDED': 'Y' if tax_included else 'N'
        })
        
        if discount_sum > 0:
            product.discount_sum = discount_sum
        elif discount_rate > 0:
            product.discount_rate = discount_rate
            
        self._products.append(product)
        return product
    
    def clear(self) -> None:
        """Очистка списка товаров"""
        self._products = []
        
    async def save(self) -> None:
        """Сохранение товаров сделки"""
        if not self._deal.id:
            raise ValueError("Сделка должна быть сохранена перед сохранением товаров")
            
        if self._products is not None:
            rows = [product.to_dict() for product in self._products]
            await self._bitrix.call(
                'crm.deal.productrows.set',
                {
                    'id': self._deal.id,
                    'rows': rows
                }
            )


class DealNote(Note):
    """Специализированный класс для примечаний к сделке"""
    
    def __init__(self, bitrix, deal: Optional['Deal'] = None, data: Optional[Dict[str, Any]] = None):
        super().__init__(bitrix, data)
        self._deal: Optional['Deal'] = deal
        if deal and not data:
            self._data["ENTITY_TYPE"] = "deal"
            self._data["ENTITY_ID"] = deal.id


class DealNoteManager(RelatedManager[DealNote]):
    """Менеджер для работы с примечаниями сделки"""
    
    async def create(self, **kwargs) -> DealNote:
        """Создание нового примечания для сделки"""
        note = DealNote(self._bitrix, cast('Deal', self._parent_entity))
        for key, value in kwargs.items():
            setattr(note, key, value)
        
        # Добавляем примечание через метод crm.timeline.comment.add 
        result = await self._bitrix.call(
            "crm.timeline.comment.add",
            {
                'fields': {
                    'ENTITY_ID': self._parent_entity.id,
                    'ENTITY_TYPE': 'deal',
                    'COMMENT': note.text
                }
            }
        )
        
        note._data["ID"] = result
        return note


class DealEntityManager(EntityManager['Deal']):
    """Кастомный менеджер сделок для правильной типизации"""
    
    async def get_by_id(self, deal_id: Union[str, int]) -> Optional['Deal']:
        """Получение сделки по ID"""
        result = await self._bitrix.call(
            'crm.deal.get',
            {'id': deal_id}
        )
        if result:
            return self._entity_class(self._bitrix, result)
        return None
    
    pass


class Deal(BaseEntity):
    """Класс для работы с сделкой в Bitrix24"""
    
    ENTITY_NAME: ClassVar[str] = "DEAL"
    ENTITY_METHOD: ClassVar[str] = "crm.deal"
    
    # Аннотации для IDE подсказок и автокомплита
    # Они не влияют на реальное поведение, но необходимы для IDE
    id: Optional[int]
    title: Optional[str]
    opportunity: Optional[float]
    currency_id: Optional[str]
    stage_id: Optional[str]
    probability: Optional[float]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    closed: Optional[bool]
    comments: Optional[str]
    type_id: Optional[str]
    
    company_id: Optional[int]
    contact_id: Optional[int]
    assigned_by_id: Optional[int]
    
    company: Optional[Company]
    contact: Optional[Contact]
    
    # Дескрипторы, которые действительно выполняют работу
    id = IntegerField("ID")
    title = StringField("TITLE")
    opportunity = FloatField("OPPORTUNITY")
    currency_id = StringField("CURRENCY_ID")
    stage_id = StringField("STAGE_ID")
    probability = FloatField("PROBABILITY")
    created_at = DateTimeField("DATE_CREATE")
    updated_at = DateTimeField("DATE_MODIFY")
    closed = BooleanField("CLOSED")
    comments = StringField("COMMENTS")
    type_id = StringField("TYPE_ID")
    
    # Связанные сущности
    company_id = IntegerField("COMPANY_ID")
    contact_id = IntegerField("CONTACT_ID")
    assigned_by_id = IntegerField("ASSIGNED_BY_ID")
    
    # Связанные объекты (lazy loading)
    company = RelatedEntityField("COMPANY_ID", Company)
    contact = RelatedEntityField("CONTACT_ID", Contact)
    
    # Списки
    _tags = ListField("TAGS")
    
    # Словарь для хранения пользовательских полей, которые будут добавляться динамически
    _custom_fields: ClassVar[Dict[str, Any]] = {}
    
    # Объекты для подсказок типов IDE
    notes: DealNoteManager
    products: ProductsManager
    objects: ClassVar[DealEntityManager]
    
    @property
    def tags(self) -> List[str]:
        return self._tags
    
    def __init__(self, bitrix, data: Optional[Dict[str, Any]] = None):
        super().__init__(bitrix, data)
        # Инициализация менеджера примечаний
        self.notes = DealNoteManager(bitrix, self, DealNote)
        # Инициализация менеджера товаров
        self.products = ProductsManager(bitrix, self)
    
    def __str__(self) -> str:
        return f"Deal: {self.title} (ID: {self.id})"
    
    @classmethod
    def get_manager(cls, bitrix) -> DealEntityManager:
        manager = DealEntityManager(bitrix, cls)
        cls.objects = manager
        return manager
    
    # @classmethod
    # def add_custom_field(cls, name: str, field: CustomField) -> None:
    #     """
    #     Добавляет пользовательское поле в класс Deal
        
    #     Пример:
    #     Deal.add_custom_field('utm_source', CustomField("UTM Source"))
    #     Deal.add_custom_field('delivery_address', TextCustomField("Адрес доставки"))
    #     """
    #     setattr(cls, name, field)
    #     cls._custom_fields[name] = field
    
    async def save(self) -> 'Deal':
        """Сохранение сделки и связанных данных"""
        # Сначала сохраняем основные данные сделки
        await super().save()
        
        # Затем сохраняем товары, если они были изменены
        await self.products.save()
        
        return self

    async def delete(self) -> bool:
        """Удаление сделки"""
        if not self.id:
            raise ValueError("Невозможно удалить несохраненную сделку")
        
        result = await self._bitrix.call(
            'crm.deal.delete',
            {'id': self.id}
        )
        
        return bool(result)


# Пример добавления пользовательских полей
# Deal.add_custom_field('utm', CustomField("UTM метка", isMultiple=True))
# Deal.add_custom_field('delivery_type', CustomField("Способ доставки"))
# Deal.add_custom_field('address', CustomField("Адрес"))
