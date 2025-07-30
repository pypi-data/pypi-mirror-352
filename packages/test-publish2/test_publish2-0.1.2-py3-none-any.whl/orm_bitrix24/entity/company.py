from typing import ClassVar, Optional, List, Dict, Any, Type

from .base import BaseEntity, StringField, IntegerField, DateTimeField, BooleanField


class Company(BaseEntity):
    """Класс для работы с компанией в Bitrix24"""
    
    ENTITY_NAME: ClassVar[str] = "COMPANY"
    ENTITY_METHOD: ClassVar[str] = "crm.company"
    
    # Системные поля
    id = IntegerField("ID")
    title = StringField("TITLE")
    name = StringField("NAME")  # Алиас для удобства
    created_at = DateTimeField("DATE_CREATE")
    updated_at = DateTimeField("DATE_MODIFY")
    
    def __str__(self) -> str:
        return f"Company: {self.title} (ID: {self.id})"
    
    @classmethod
    def get_manager(cls, bitrix) -> 'EntityManager[Company]':
        manager = cls.get_entity_manager(bitrix)
        cls.objects = manager
        return manager 