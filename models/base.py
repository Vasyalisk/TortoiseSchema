from tortoise.models import MODEL

from pydantic import BaseModel

from typing import Type, Awaitable, List, Iterable


class TortoiseSchema(BaseModel):
    """
    Pydantic-based schema class which can be used with Tortoise ORM. Unlike
    Tortoise PydanticModel class does not fetch all relational fields in
    async methods but only those specified in Config subclass.
    
    >>> class UserGet(TortoiseSchema):
    >>>     id: int
    >>>     related_field_name: UserRelatedGet
    >>>
    >>>     class Config:
    >>>         orm_mode = True
    >>>         fetch_fields = ["related_field_name"]
    """
    
    @classmethod
    async def from_tortoise(cls, model: Type[MODEL]) -> "TortoiseSchema":
        """
        Create schema from Tortoise model instance. Automatically fetches 
        fetch_fields specified in Config class.
        
        >>> model = await TortoiseModel.get(pk=1)
        >>> schema = await TortoiseSchema.from_tortoise(model)
        """
        return cls.from_orm(
            await model.fetch_related(
                *cls.get_prefetch_fields()
                )
            )
    
    @classmethod
    async def from_queryset(cls, queryset: Awaitable) -> List["TortoiseSchema"]:
        """
        Create list schema from Tortoise queryset. Automatically pre-fetches 
        fetch_fields specified in Config class.
        
        >>> queryset = TortoiseModel.all()
        >>> schema_list = await TortoiseSchema.from_queryset(queryset)
        """
        return [
            cls.from_orm(model)
            for model in await queryset.prefetch_related(
                *cls.get_prefetch_fields()
                )
            ]
    
    @classmethod
    async def from_queryset_single(cls, queryset: Awaitable) -> "TortoiseSchema":
        """
        Create schema from Tortoise queryset with one record. Automatically 
        pre-fetches fetch_fields specified in Config class.
        
        >>> queryset_single = TortoiseModel.get(pk=1)
        >>> schema = await TortoiseSchema.from_queryset_single(model)
        """
        return cls.from_orm(
            await queryset.prefetch_related(
                *cls.get_prefetch_fields()
                )
            )
            
    @classmethod
    def get_prefetch_fields(cls) -> Iterable[str]:
        """
        Returns sequence of prefetch field names from Config subclass. Supports
        nested field names, e.g. field__subfield.
        """
        return getattr(cls.__config__, "fetch_fields", [])
    
    
class TortoiseListSchema(BaseModel):
    """
    Pydantic-based schema class which can be used with Tortoise ORM. Unlike
    Tortoise PydanticModel class does not fetch all relational fields in
    async methods but only those specified in Config subclass.
    
    >>> class UserList(TortoiseSchema):
    >>>     __root__: UserGet
    >>>
    >>>     class Config:
    >>>         orm_mode = True
    >>>         fetch_fields = ["user_field", "user_field__subfield"]
    """
    
    @classmethod
    async def from_queryset(cls, queryset: Awaitable) -> "TortoiseListSchema":
        """
        Create schema from Tortoise queryset. Automatically pre-fetches 
        fetch_fields specified in Config class.
        
        >>> queryset = TortoiseModel.all()
        >>> schema = await TortoiseSchema.from_queryset(queryset)
        """
        return cls.from_orm(
            await queryset.prefetch_related(
                *cls.get_prefetch_fields()
                )
            )
        
    @classmethod
    def get_prefetch_fields(cls) -> Iterable[str]:
        """
        Returns sequence of prefetch field names from Config subclass. Supports
        nested field names, e.g. field__subfield.
        """
        return getattr(cls.__config__, "fetch_fields", [])
    
    
class Config:
    """
    Config class which should be used in TortoiseSchema. Also supports all
    standard pydantic fields.
    
    >>> class UserGet(TortoiseSchema):
    >>>     id: int
    >>>     related_field_name: UserRelatedGet
    >>>
    >>>     class Config:
    >>>         orm_mode = True
    >>>         fetch_fields = ["related_field_name"]
    """
    fetch_fields: Iterable[str]
