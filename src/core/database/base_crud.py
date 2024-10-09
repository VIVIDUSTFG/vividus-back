from __future__ import annotations

import inspect
from functools import wraps
from typing import (Any, Callable, Dict, List, Literal, Type, TypeVar)

from sqlalchemy import func
from sqlalchemy.orm import Query, noload, raiseload, selectinload, subqueryload
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import SQLModel, exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

Self = TypeVar("Self", bound="Base")
LoadStrategy = Literal["subquery", "selectin",
                       "raise", "raise_on_sql", "noload"]
load_strategy_map: Dict[LoadStrategy, Callable[..., Any]] = {
    "subquery": subqueryload,
    "selectin": selectinload,
    "raise": raiseload,
    "raise_on_sql": raiseload,
    "noload": noload,
}


class InvalidTable(RuntimeError):
    """Raised when calling a method coupled to SQLAlchemy operations.

    It should be called only by SQLModel objects that are tables.
    """


def is_table(cls: Type[Self]) -> bool:
    if hasattr(cls, '__tablename__'):
        return True
    return False


def validate_table(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cls = self if inspect.isclass(self) else self.__class__
        if not is_table(cls):
            raise InvalidTable(
                f'"{cls.__name__}" is not a table. '
                "Add the class parameter `table=True` or don't use with this object."
            )
        return func(self, *args, **kwargs)

    return wrapper


def _prepare_query(
    cls: Type[Self], load_strategy: Dict[str, LoadStrategy] | None
) -> Query:
    load_strategy = load_strategy or {}
    query = select(cls)

    for attr_name, strategy in load_strategy.items():
        attribute = getattr(cls, attr_name)
        query = query.options(load_strategy_map[strategy](attribute))

    return query


class Base(SQLModel):
    @classmethod
    @validate_table
    async def get(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        load_strategy: Dict[str, LoadStrategy] | None = None,
        **kwargs: Any,
    ) -> Self:
        query = _prepare_query(cls, load_strategy)
        result = await session.exec(query.filter(*args).filter_by(**kwargs))
        return result.first()

    @classmethod
    @validate_table
    async def get_multi(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        load_strategy: Dict[str, LoadStrategy] | None = None,
        offset: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> List[Self]:
        query = _prepare_query(cls, load_strategy)
        result = await session.exec(
            query.filter(*args).filter_by(**kwargs).offset(offset).limit(limit)
        )
        return result.all()

    @classmethod
    @validate_table
    async def create(cls: Type[Self], session: AsyncSession, **kwargs: Any) -> Self:
        db_obj = cls(**kwargs)
        session.add(db_obj)
        await session.commit()
        return db_obj

    @validate_table
    async def update(self: Self, session: AsyncSession, **kwargs: Any) -> Self:
        obj_data = dict(self)
        for field in obj_data:
            if field in kwargs:
                setattr(self, field, kwargs[field])
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    @classmethod
    @validate_table
    async def delete(
        cls: Type[Self], session: AsyncSession, *args: BinaryExpression, **kwargs: Any
    ) -> Self:
        db_obj = await cls.get(session, *args, **kwargs)
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    @classmethod
    @validate_table
    async def delete_multi(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        **kwargs: Any,
    ) -> List[Self]:
        statement = select(cls).filter(*args).filter_by(**kwargs)
        result = await session.exec(statement)
        db_objs = result.scalars().all()

        for obj in db_objs:
            await session.delete(obj)

        await session.commit()
        return db_objs

    @classmethod
    @validate_table
    async def exists(cls: Type[Self], session: AsyncSession, **kwargs: Any) -> bool:
        if not kwargs:
            raise ValueError("Attributes for existence check cannot be empty.")

        query = select(exists().where(
            *[getattr(cls, key) == value for key, value in kwargs.items()]))
        result = await session.exec(query)
        return result.one()

    @classmethod
    @validate_table
    async def count(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        **kwargs: Any
    ) -> int:
        query = select(func.count()).select_from(
            cls).filter(*args).filter_by(**kwargs)
        result = await session.exec(query)
        return result.first()

    @classmethod
    @validate_table
    async def get_column_value(
        cls: Type[Self],
        session: AsyncSession,
        column: str,
        *args: BinaryExpression,
        **kwargs: Any
    ) -> Any:
        if not hasattr(cls, column):
            raise AttributeError(
                f"Column '{column}' does not exist on {cls.__name__}")
        column_attr = getattr(cls, column)
        query = select(column_attr).filter(*args).filter_by(**kwargs)
        result = await session.exec(query)
        return result.first()

    @classmethod
    @validate_table
    async def get_grouped_aggregates(
        cls: Type[Self],
        session: AsyncSession,
        group_by: str,
        aggregates: Dict[str, Callable],
        load_strategy: Dict[str, LoadStrategy] | None = None,
        limit: int | None = None,
        **filters: Any
    ) -> List[Dict[str, Any]]:
        query = _prepare_query(cls, load_strategy)

        group_by_field = getattr(cls, group_by)

        group_query = select(
            group_by_field,
            *[
                func.coalesce(aggregator(getattr(cls, field)), 0).label(field)
                for field, aggregator in aggregates.items()
            ]
        ).group_by(group_by_field)

        valid_filters = {k: v for k, v in filters.items() if v is not None}
        if valid_filters:
            group_query = group_query.filter_by(**valid_filters)

        if limit:
            group_query = group_query.limit(limit)

        result = await session.exec(group_query)
        return result.all()
