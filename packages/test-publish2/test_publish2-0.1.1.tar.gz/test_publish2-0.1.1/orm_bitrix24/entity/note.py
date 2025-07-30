from typing import ClassVar, Optional, List, Dict, Any, Type

from .base import BaseEntity, StringField, IntegerField, DateTimeField


class Note(BaseEntity):
    """Класс для работы с примечаниями в Bitrix24"""
    
    ENTITY_NAME: ClassVar[str] = "NOTE"
    ENTITY_METHOD: ClassVar[str] = "crm.livefeedmessage"
    
    # Системные поля
    id = IntegerField("ID")
    text = StringField("POST_MESSAGE")
    created_at = DateTimeField("DATE_CREATE")
    author_id = IntegerField("AUTHOR_ID")
    entity_id = IntegerField("ENTITY_ID")
    entity_type = StringField("ENTITY_TYPE")
    
    def __str__(self) -> str:
        return f"Note: {self.text[:30]}... (ID: {self.id})" 