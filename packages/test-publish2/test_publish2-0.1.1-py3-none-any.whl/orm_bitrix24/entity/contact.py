from typing import ClassVar, Optional, List, Dict, Any, Type

from .base import BaseEntity, StringField, IntegerField, DateTimeField, BooleanField


class Contact(BaseEntity):
    """Класс для работы с контактом в Bitrix24"""
    
    ENTITY_NAME: ClassVar[str] = "CONTACT"
    ENTITY_METHOD: ClassVar[str] = "crm.contact"
    
    # Системные поля
    id = IntegerField("ID")
    name = StringField("NAME")
    last_name = StringField("LAST_NAME")
    second_name = StringField("SECOND_NAME")
    email = StringField("EMAIL")
    phone = StringField("PHONE")
    created_at = DateTimeField("DATE_CREATE")
    updated_at = DateTimeField("DATE_MODIFY")
    
    @property
    def full_name(self) -> str:
        parts = [self.name or "", self.last_name or ""]
        return " ".join(p for p in parts if p)
    
    def __str__(self) -> str:
        return f"Contact: {self.full_name} (ID: {self.id})"
    
    @classmethod
    def get_manager(cls, bitrix) -> 'EntityManager[Contact]':
        manager = cls.get_entity_manager(bitrix)
        cls.objects = manager
        return manager 