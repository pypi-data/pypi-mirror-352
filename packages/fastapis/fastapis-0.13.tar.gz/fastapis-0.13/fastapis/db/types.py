import datetime
import math
import time

import sqlalchemy.types as sqltypes

from pathlib import Path
from typing import (Annotated, Any, Coroutine, Dict, Generic, List, Sequence,
                    Tuple, Type, TypeVar, Union, Optional, TYPE_CHECKING, Mapping, OrderedDict)
from sqlalchemy import exc
from sqlalchemy import (BinaryExpression, BooleanClauseList, ClauseList,
                        ForeignKey, Integer, Column, ColumnClause, Cast,Row, Select, String,
                        TypeDecorator, UnaryExpression, Enum as SQLEnum,)
from sqlalchemy import BigInteger, Integer, DateTime, Cast, Uuid, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, AsyncSession
from sqlalchemy.orm import (ColumnProperty, DeclarativeBase,
                            InstrumentedAttribute, Mapped)
from sqlalchemy.orm.relationships import Relationship
from sqlalchemy.exc import IllegalStateChangeError, AmbiguousForeignKeysError, ArgumentError, AwaitRequired, SQLAlchemyError, StatementError, SAWarning, NotSupportedError, DatabaseError, DBAPIError, IntegrityError, UnboundExecutionError
ClausesType = TypeVar(
    "ClausesType",
    ClauseList,
    BinaryExpression,
    BooleanClauseList,
    UnaryExpression,
    bool,
)

DBModel = TypeVar("DBModel", bound="Base")


class TimeStamp(TypeDecorator):
    """Prefixes Unicode values with "PREFIX:" on the way in and
    strips it off on the way out.
    """

    impl = Integer
    cache_ok = True
    _current_timestamp_length: int = math.ceil(math.log10(int(time.time())))

    def process_bind_param(self, value, dialect):
        # print("process bind param", value, dialect)
        _value  = None
        if isinstance(value, datetime.datetime):
            _value = int(value.timestamp())
        elif isinstance(value, float):
            _value = int(value)
        elif isinstance(value, str):
            _value = int(value)
        ts = _value
        while True:
            a = math.ceil(math.log10(_value))
            if a > self._current_timestamp_length:
                _value //= 10
                continue
            elif a < self._current_timestamp_length:
                _value *= 10
                continue
            break
        return _value

    def process_result_value(self, value, dialect):
        # print("process result value", value, dialect)
        _value = None
        if isinstance(value, datetime.datetime):
            _value = int(value.timestamp())
        elif isinstance(value, float):
            _value = int(value)
        elif isinstance(value, str):
            _value = int(
                datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").timestamp()
            )
        while True:
            a = math.ceil(math.log10(_value))
            if a > self._current_timestamp_length:
                _value //= 10
                continue
            elif a < self._current_timestamp_length:
                _value *= 10
                continue
            break
        return _value


class DictType(TypeDecorator):
    import json as _json

    # convert unix timestamp to datetime object
    impl = String

    # convert datetime object to unix timestamp when inserting data to database
    def process_bind_param(self, value, dialect) -> str:
        if value is not None:
            return self._json.dumps(value)
        else:
            return value

    def process_result_value(self, value, dialect) -> dict:
        if value is not None:
            value = self._json.loads(value)
        return value


class FilterParams:
    limit: int = None
    offset: int = None
    order_by: Union[str, InstrumentedAttribute] = None
    group_by: Union[str, InstrumentedAttribute] = None
    search: str = None

    def __init__(
            self,
            order_by: str = None,
            group_by: str = None,
            limit: int = None,
            offset: int = None,
            search: str = None,
    ):
        self.limit = limit
        self.offset = offset
        self._order_by = order_by
        self._group_by = group_by
        self._search = search

    def __call__(self, model: DBModel):
        """hack to be able to use getattr on the model"""
        if self._order_by:
            self.order_by: InstrumentedAttribute = getattr(model, self._order_by)
        if self._group_by:
            self.group_by: InstrumentedAttribute = getattr(model, self._group_by)
        return self


class ResultWithStatsType(Generic[DBModel]):
    data: Union[List[DBModel], DBModel]
    offset: int
    limit: int
    total_pages: int
    num_pages: int
    cur_page: int
    count: int
    range: Tuple[int, int]
    stats: Dict[str, int]


