from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Union, Callable, get_type_hints, cast, Generic, overload
import datetime
from fast_bitrix24 import Bitrix

T = TypeVar('T', bound='BaseEntity')
V = TypeVar('V')  # Тип значения поля


class Field(Generic[V]):
    """Базовое поле для ORM"""
    
    def __init__(self, field_name: str, nullable: bool = True):
        self.field_name: str = field_name
        self.nullable: bool = nullable
        self._value: Optional[V] = None
        
    def __set_name__(self, owner: Type, name: str) -> None:
        self.name = name
        
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[V, 'Field[V]']:
        if instance is None:
            return self
        return cast(V, instance._data.get(self.field_name))
        
    def __set__(self, instance: 'BaseEntity', value: V) -> None:
        instance._data[self.field_name] = value
        instance._dirty_fields.add(self.field_name)


class IntegerField(Field[int]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[int], 'IntegerField']:
        value = super().__get__(instance, owner)
        if isinstance(value, Field):
            return self
        if value is not None:
            return int(value)
        return value


class StringField(Field[str]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[str], 'StringField']:
        value = super().__get__(instance, owner)
        if isinstance(value, Field):
            return self
        if value is not None:
            return str(value)
        return value


class FloatField(Field[float]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[float], 'FloatField']:
        value = super().__get__(instance, owner)
        if isinstance(value, Field):
            return self
        if value is not None:
            return float(value)
        return value


class DateTimeField(Field[datetime.datetime]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[datetime.datetime], 'DateTimeField']:
        value = super().__get__(instance, owner)
        if isinstance(value, Field):
            return self
        if value and isinstance(value, str):
            # Обрабатываем формат даты Bitrix24
            try:
                return datetime.datetime.fromisoformat(value)
            except ValueError:
                return cast(datetime.datetime, value)
        return value


class BooleanField(Field[bool]):
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[bool, 'BooleanField']:
        value = super().__get__(instance, owner)
        if isinstance(value, Field):
            return self
        if value is not None:
            return value == 'Y'
        return False


class RelatedEntityField(Field[T]):
    def __init__(self, field_name: str, related_entity: Type[T], nullable: bool = True):
        super().__init__(field_name, nullable)
        self.related_entity: Type[T] = related_entity
        
    async def _load_related(self, instance: 'BaseEntity', entity_id: Union[str, int]) -> Optional[T]:
        """Загружает связанный объект и сохраняет его в кеше"""
        try:
            related_entity = await self.related_entity.get_by_id(instance._bitrix, entity_id)
            # Сохраняем результат в кеше
            instance._related[self.name] = related_entity
            return related_entity
        except Exception as e:
            print(f"Ошибка загрузки связанного объекта: {e}")
            instance._related[self.name] = None
            return None
        
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Optional[T], 'RelatedEntityField[T]']:
        if instance is None:
            return self
        
        entity_id = instance._data.get(self.field_name)
        if not entity_id:
            return None
        
        # Проверяем, загружен ли уже связанный объект
        if self.name in instance._related:
            # Если объект уже загружен, возвращаем его
            return instance._related[self.name]
        
        # Создаем корутину для загрузки объекта
        return self._load_related(instance, entity_id)


class ListField(Field[List[Any]]):
    def __init__(self, field_name: str, nullable: bool = True):
        super().__init__(field_name, nullable)
        
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[List[Any], 'ListField']:
        if instance is None:
            return self
        
        value = instance._data.get(self.field_name, [])
        if not isinstance(value, list):
            value = [value] if value else []
            instance._data[self.field_name] = value
        
        return value


class CustomField(Field[Any]):
    """Базовый класс для пользовательских полей"""
    
    def __init__(self, field_title: str, isMultiple: bool = False):
        super().__init__("", True)  # Передаем пустое поле, оно будет установлено в __set_name__
        self.field_title: str = field_title
        self.isMultiple: bool = isMultiple
        
    def __set_name__(self, owner: Type, name: str) -> None:
        self.name = name
        # Если название уже содержит UF_, используем его как есть
        if self.field_title.startswith("UF_"):
            self.field_name = self.field_title
        else:
            self.field_name = f"UF_{name.upper()}"
            
    def __get__(self, instance: Optional['BaseEntity'], owner: Type) -> Union[Any, 'CustomField']:
        if instance is None:
            return self
        return instance._data.get(self.field_name)
    
    def __set__(self, instance: 'BaseEntity', value: Any) -> None:
        instance._data[self.field_name] = value
        instance._dirty_fields.add(self.field_name)


class TextCustomField(CustomField):
    pass


class SelectCustomField(CustomField):
    pass


class UrlCustomField(CustomField):
    pass


class EntityManager(Generic[T]):
    """Менеджер для работы с сущностями"""
    
    def __init__(self, bitrix: Bitrix, entity_class: Type[T]):
        self._bitrix: Bitrix = bitrix
        self._entity_class: Type[T] = entity_class
        
    async def filter(self, **kwargs) -> List[T]:
        """Поиск сущностей по фильтру"""
        filter_params: Dict[str, Any] = {}
        for key, value in kwargs.items():
            filter_params[key.upper()] = value
        
        result = await self._bitrix.get_all(
            f"{self._entity_class.ENTITY_METHOD}.list",
            {"filter": filter_params}
        )
        
        return [self._entity_class(self._bitrix, item) for item in result]
    
    async def get_all(self) -> List[T]:
        """Получение всех сущностей"""
        result = await self._bitrix.get_all(f"{self._entity_class.ENTITY_METHOD}.list")
        entities: List[T] = [self._entity_class(self._bitrix, item) for item in result]
        return entities
    
    async def create(self, **kwargs) -> T:
        """Создание новой сущности"""
        entity = self._entity_class(self._bitrix)
        for key, value in kwargs.items():
            setattr(entity, key, value)
        await entity.save()
        return entity


class RelatedManager(Generic[T]):
    """Менеджер для работы со связанными сущностями"""
    
    def __init__(self, bitrix: Bitrix, parent_entity: 'BaseEntity', related_entity_class: Type[T]):
        self._bitrix: Bitrix = bitrix
        self._parent_entity: 'BaseEntity' = parent_entity
        self._related_entity_class: Type[T] = related_entity_class
        
    async def create(self, **kwargs) -> T:
        """Создание связанной сущности"""
        entity = self._related_entity_class(self._bitrix)
        # Устанавливаем связь с родительской сущностью
        setattr(entity, f"{self._parent_entity.ENTITY_NAME.lower()}_id", self._parent_entity.id)
        
        for key, value in kwargs.items():
            setattr(entity, key, value)
        await entity.save()
        return entity
    
    async def filter(self, **kwargs) -> List[T]:
        """Поиск связанных сущностей"""
        kwargs[f"{self._parent_entity.ENTITY_NAME.lower()}_id"] = self._parent_entity.id
        return await self._related_entity_class.objects.filter(**kwargs)


class BaseEntity:
    """Базовый класс для всех сущностей"""
    
    ENTITY_NAME: Optional[str] = None
    ENTITY_METHOD: Optional[str] = None
    objects: EntityManager
    
    # Словарь для хранения пользовательских полей
    _custom_fields: Dict[str, Any] = {}
    
    def __init__(self, bitrix: Bitrix, data: Optional[Dict[str, Any]] = None):
        self._bitrix: Bitrix = bitrix
        
        # Проверяем и обрабатываем вложенную структуру данных
        if data and len(data) == 1 and isinstance(next(iter(data.values())), dict):
            # Если есть один ключ и его значение - словарь, извлекаем этот словарь
            data = next(iter(data.values()))
        
        self._data: Dict[str, Any] = {} if data is None else data
        self._dirty_fields: set = set()
        self._related: Dict[str, Any] = {}
    
    @property
    def id(self) -> Optional[Union[str, int]]:
        return self._data.get("ID")
        
    @classmethod
    def add_custom_field(cls, name: str, field: CustomField) -> None:
        """
        Добавляет пользовательское поле в класс
        
        Пример:
        Deal.add_custom_field('utm_source', CustomField("UTM Source"))
        Deal.add_custom_field('delivery_address', TextCustomField("Адрес доставки"))
        """
        setattr(cls, name, field)
        cls._custom_fields[name] = field
    
    @classmethod
    def get_entity_manager(cls, bitrix: Bitrix) -> EntityManager[T]:
        return EntityManager[T](bitrix, cls)
    
    async def save(self) -> None:
        """Создание или обновление сущности"""
        if self.id:  # Обновление существующей
            fields = {k: self._data[k] for k in self._dirty_fields}
            if fields:
                await self._bitrix.call(
                    f"{self.ENTITY_METHOD}.update",
                    {
                        'id': self.id,
                        'fields': fields
                    }
                )
                self._dirty_fields.clear()
        else:  # Создание новой
            result = await self._bitrix.call(
                f"{self.ENTITY_METHOD}.add",
                {'fields': self._data}
            )
            self._data["ID"] = result
            self._dirty_fields.clear()
    
    @classmethod
    async def get_by_id(cls: Type[T], bitrix: Bitrix, entity_id: Union[str, int]) -> Optional[T]:
        """Получение сущности по ID"""
        result = await bitrix.call(
            f"{cls.ENTITY_METHOD}.get",
            {'id': entity_id}
        )
        if result:
            return cls(bitrix, result)
        return None 