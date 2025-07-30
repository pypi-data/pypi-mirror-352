from __future__ import annotations

import asyncio
import logging
import uuid
import warnings
from asyncio import Task
from typing import Any, Coroutine, Dict, Generic, List, Sequence, Type

import sqlalchemy.exc
import sqlalchemy.ext
import sqlalchemy.orm.collections
from sqlalchemy import Select, all_, and_, any_, func, or_, select
from sqlalchemy.orm import mapped_column, relationship, Mapped, MappedColumn, ColumnProperty
from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine, create_async_pool_from_url, async_engine_from_config, async_scoped_session, async_session, async_scoped_session, async_object_session, async_engine_from_config, close_all_sessions, create_async_pool_from_url

from .types import (Annotated, AsyncAttrs, AsyncEngine, AsyncSession,
                    DBModel, BinaryExpression, BooleanClauseList, ClauseList,
                    ClausesType, ColumnProperty, Coroutine, DeclarativeBase,
                    Dict, ForeignKey,
                    InstrumentedAttribute, Integer, List, Mapped,
                    Relationship, ResultWithStatsType, Row, Select, Sequence,
                    String, TimeStamp, Tuple, Type, TypeDecorator, TypeVar,
                    UnaryExpression)
from .types import IllegalStateChangeError, AmbiguousForeignKeysError, ArgumentError, AwaitRequired, SQLAlchemyError, StatementError, SAWarning, NotSupportedError, DatabaseError, DBAPIError, IntegrityError, UnboundExecutionError
from .types import DictType, TimeStamp
logger = logging.getLogger(__name__)


class Factory:
    """
    Factory for database related stuff
    holder of the engine (AsyncEngine), session_maker[AsyncSession]
    can be used as async contextmanager to yield a sqlalchemy AsyncSession
    also responsible for creating the db schema (create_schema())
    """

    _engine: AsyncEngine = None
    _session_maker: async_sessionmaker[AsyncSession] = None
    _session: AsyncSession | None = None
    _scheme_created = False
    connection_string: str = None
    echo_queries: bool = None

    @classmethod
    def engine(cls):
        if not cls._engine:
            cls._engine = create_async_engine(
                cls.connection_string,
                echo=cls.echo_queries
            )
        return cls._engine

    @classmethod
    def session(cls) -> AsyncSession:
        if not cls._session_maker:
            cls._session_maker = async_sessionmaker[AsyncSession](
                bind=cls.engine(), expire_on_commit=False,  # close_resets_only=False
            )
        if not cls._session:
            cls._session = cls._session_maker()
        return cls._session

    @classmethod
    def create_schema(cls) -> Coroutine | Task | None:
        """
        creates the database and/or schema
        this can be awaited (async) or called (sync)

        :return:
        """
        logger.debug("creating schema")

        async def wrapped():
            engine = cls.engine()
            # async with cls() as s:
            #     connection = await s.connection()
            #     engine = connection.engine
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # cls.engine().begin() as conn:

        try:
            # check if we're in an async context or not
            loop = asyncio.get_running_loop()
            return loop.create_task(wrapped())
        except RuntimeError:
            # we're in a sync context, call in help from asyncio.run
            return asyncio.run(wrapped())
        finally:
            cls._scheme_created = True

    @classmethod
    async def __aenter__(cls) -> AsyncSession:
        if not cls._scheme_created:
            await cls.create_schema()
        cls._current_session = cls.session()
        return cls._current_session

    @classmethod
    async def __aexit__(cls, exc_type, exc_val, exc_tb) -> None:
        try:
            if cls._current_session.new or cls._current_session.dirty or cls._current_session.deleted:
                await cls._current_session.commit()
                return await cls._current_session.close()
        except sqlalchemy.exc.InvalidRequestError as e:
            logger.warning("invalidrequesterror when on commit:\n%s" % e.args)
            raise
        except:  # noqa
            await asyncio.shield(cls._current_session.rollback())

            raise
        finally:
            try:
                # None
                await asyncio.shield(cls._current_session.close())
                # await cls._session.close()
                pass
            except IllegalStateChangeError as e:
                logger.warning("illegalstate error while closing db in context manager:\n%s" % e.args)
                pass
            finally:
                cls._session = None


def factory(*, connection_string: str = "sqlite+aiosqlite:///database.db", echo_queries: bool = False) -> Factory:
    if Factory.connection_string is None:
        warnings.warn(f"""\n
                    connection_string is not set on Factory.
                    using default value now: '{connection_string}'
                    to set your own values, run factory() for the first time using keywords,
                    eg: factory(connection_string="some conn string", echo_queries=True )  
                    """, category=UserWarning)
        Factory.connection_string = connection_string
        # raise RuntimeError("connection_string is not set on Factory. run configure_factory first")
    if Factory.echo_queries is None:
        warnings.warn(f"""\n
                            echo_queries is not set on Factory.
                            using default value now: '{echo_queries}'
                            to set your own values, run factory() for the first time using keywords,
                            eg: factory(connection_string="some conn string", echo_queries=True )  
                            """, category=UserWarning)
        Factory.echo_queries = echo_queries
        # raise RuntimeError("echo_queries is not set on Factory.  run configure_factory first")
    return Factory()


def configure_factory(connection_string: str = "sqlite+aiosqlite:///database.db",
                      echo_queries: bool = False):
    Factory.connection_string = connection_string
    Factory.echo_queries = echo_queries
    return Factory()


class Base(AsyncAttrs, DeclarativeBase):
    id_: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    id: Mapped[str] = mapped_column(default=lambda: str(uuid.uuid4()))

    updated_at: Mapped[int] = mapped_column(
        TimeStamp, default=func.now(), onupdate=func.now()
    )

    created_at: Mapped[int] = mapped_column(TimeStamp, server_default=func.now())


    def __init__(self, *args, **kwargs):
        super().__init__()
        for k, v in dict(*args, **kwargs).items():
            if not hasattr(self, k):
                logger.warning(
                    f"trying to assign %s to %s, but %s has no attribute %s"
                    % (k, self, self, k)
                )
            setattr(self, k, v)

    @property
    def dict(self) -> Dict[str, Any]:
        attrs = dict(self.__mapper__.attrs)  # noqa
        ret = {}
        for k, v in attrs.items():
            if hasattr(v, "columns"):
                # we have regular column
                value = getattr(self, k)
                match type(value).__name__:
                    case "str":
                        ret[k] = value
                    case "int":
                        ret[k] = value
                    case "float":
                        ret[k] = value
                    case _:
                        ret[k] = str(value)
            elif hasattr(v, "argument"):
                # we have a relation
                try:
                    val = getattr(self, k)
                    if isinstance(
                            val,
                            (
                                    sqlalchemy.orm.collections.InstrumentedList,
                                    sqlalchemy.orm.collections.InstrumentedSet,
                            ),
                    ):
                        val = [v.as_dict() for v in val]
                    elif isinstance(val, Base):
                        val = val.dict
                    ret[k] = val
                except:  # noqa
                    raise
        return ret

    @staticmethod
    def __make_string_search_query__(
            cls: Type[DBModel],
            search: str,
            q: Select,
    ):
        string_columns = [
            column
            for column in cls.__mapper__.c
            if "string" in type(column.type).__name__.lower()
        ]
        # print('string columns', string_columns)
        matching = [column.ilike(f"%{search}%") for column in string_columns]
        # print(matching)
        return q.filter(or_(*matching))

    @classmethod
    def _get_relationship_type(cls, field: str) -> Type | None:
        if not hasattr(cls, field):
            return None
        attrs = dict(cls.__mapper__.attrs)  # noqa
        val = attrs.get(field)
        if not val:
            return None
        if isinstance(val, Relationship):
            return val.mapper.class_

    @staticmethod
    def __make_select__(
            cls: Type[DBModel],
            *clauses: ClausesType,
            order_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            group_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            limit: int = None,
            offset: int = None,
    ):
        q = select(cls)
        if clauses and clauses[0] is not None:
            q = q.where(*clauses)
        if order_by is not None:
            q = q.order_by(order_by)
        if group_by:
            q = q.group_by(group_by)
        if limit:
            q = q.limit(limit)
        if offset:
            if not limit:
                limit = 16
            if not isinstance(limit, int):
                limit = int(limit)
            q = q.offset(offset * limit)
        return q

    @classmethod
    async def query(
            cls: Type[DBModel],
            *clauses: ClausesType,
            order_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            group_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            limit: int = None,
            offset: int = None,
            search: str = None,
    ) -> List[DBModel]:
        """
        query object from the database, it will always return a list
        :param clauses:
        :param order_by:
        :param group_by:
        :param limit:
        :param offset:
        :param search:
        :return:
        """

        q = cls.__make_select__(
            cls,
            *clauses,
            order_by=order_by,
            group_by=group_by,
            limit=limit,
            offset=offset,
        )
        if search:
            q = cls.__make_string_search_query__(cls, search, q)
        q = q.order_by(cls.id_.desc())

        async with factory() as session:
            scalars = await session.scalars(q)
            return list(scalars.all())

    @classmethod
    async def query_with_stats(
            cls: Type[DBModel],
            *clauses: ClausesType,
            order_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            group_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            limit: int = 16,
            offset: int = 0,
            search: str = None,
    ) -> ResultWithStatsType[DBModel]:
        """
        query object from the database, it will always return a list
        :param clauses:
        :param order_by:
        :param group_by:
        :param limit:
        :param offset:
        :param search:
        :return:
        """
        q = select(cls, func.count(cls.id_).over().label('count'))
        if clauses and clauses[0] is not None:
            q = q.where(*clauses)
        if order_by is not None:
            q = q.order_by(order_by)
        if group_by:
            q = q.group_by(group_by)
        if limit:
            q = q.limit(limit)
        if offset:
            if not limit:
                limit = 16
            if not isinstance(limit, int):
                limit = int(limit)
            q = q.offset(offset * limit)
        if search:
            q = cls.__make_string_search_query__(cls, search, q)
        q = q.order_by(cls.id_.desc())
        async with factory() as session:
            result = await session.execute(q)
            results = result.fetchall()
            # pagination = Pagination()
            #
            # pagination_ = [r[0] for r in list(results)]
            # try:
            #     count_max_ = results[0][-1]
            # except IndexError:
            #     count_max_ = 0
            #
            # offset_ = getattr(q, "_offset") or 0
            # limit_ = getattr(q, "_limit") or 16
            #
            # total_pages_, total_remainder_ = divmod(count_max_, limit_)
            # if total_remainder_ and count_max_ // limit_:
            #     total_pages_ += 1
            # cur_page_, cur_remainder_ = divmod(offset_, limit_)
            # if cur_remainder_ and offset_ // limit_:
            #     cur_page_ += 1
            # num_pages_ = total_pages_
            # current_page_ = cur_page_
            # count_ = min(len(pagination_), limit_)
            # range_ = offset_, offset_ + min(count_, limit_)
            #
            # pagination.offset = offset_
            # pagination.count = count_
            # pagination.range = range_
            # pagination.total_pages = total_pages_
            # pagination.num_pages = num_pages_
            # pagination.limit = limit_
            # pagination.cur_page = cur_page_
            #
            # for r in pagination_:
            #     r.pagination = pagination
            # return pagination_

            return ResultWithStats(rows=results, select_instance=q)

    @classmethod
    async def query_single(
            cls: Type[DBModel],
            *clauses: ClausesType,
            order_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            group_by: UnaryExpression | BinaryExpression | InstrumentedAttribute = None,
            limit: int = None,
            offset: int = None,
            search: str = None,
    ) -> DBModel:
        """
        query a single object from the database, returns a single item
        :param clauses:
        :param order_by:
        :param group_by:
        :param limit:
        :param offset:
        :param search:
        :return:
        """
        q = cls.__make_select__(
            cls,
            *clauses,
            order_by=order_by,
            group_by=group_by,
            limit=limit,
            offset=offset,
        )
        if search:
            q = cls.__make_string_search_query__(cls, search, q)
        async with factory() as session:
            scalars = await session.scalars(q)
            return scalars.first()

    @classmethod
    async def count(cls: DBModel) -> int:
        async with factory() as session:
            scalars = await session.scalars(select(func.count(cls.id_)))
            return scalars.first()

    async def update(self):
        """
        updates or adds a object to/in the database
        :return:
        """
        async with factory() as session:
            session.add(self)

    async def delete(self):
        """
        delete the object from the database
        :return:
        """
        async with factory() as session:
            await session.delete(self)

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        # if Factory.connection_string is None:
        #     raise RuntimeError("connection_string is not set on Factory. run configure_factory first")
        # if Factory.echo_queries is None:
        #     raise RuntimeError("echo_queries is not set on Factory.  run configure_factory first")
        super().__init_subclass__(*args, **kwargs)
        print('baseclass of Base is created', args, kwargs)


class ResultWithStats(ResultWithStatsType):
    data: DBModel

    def __init__(self, rows: Sequence[Row], select_instance: Select):

        _rows = list(rows)
        self.data = [r[0] for r in _rows]
        try:
            self.count_max = _rows[0][-1]
        except IndexError:
            self.count_max = 0

        self.offset = getattr(select_instance, "_offset") or 0
        self.limit = getattr(select_instance, "_limit") or 16

        total_pages, total_remainder = divmod(self.count_max, self.limit)
        if total_remainder and self.count_max // self.limit:
            total_pages += 1
        cur_page, cur_remainder = divmod(self.offset, self.limit)
        if cur_remainder and self.offset // self.limit:
            cur_page += 1
        self.num_pages = total_pages
        self.current_page = cur_page
        self.count = min(len(self.data), self.limit)
        self.range = self.offset, self.offset + min(len(self.data), self.limit)

    @property
    def stats(self) -> Dict[str, int]:
        s = dict(
            count_max=self.count_max,
            per_page=self.limit,
            count=self.count,
            page_max=self.num_pages,
            has_next=self.range[-1] < self.count_max,
            has_prev=self.range[0] > 0,
            page_index=self.current_page,
            range=self.range
        )
        return s

    def __repr__(self):
        base = f"<ResultWithStats[{{}}]\n\nstats:[{{}}]>"
        return base.format(self.data, self.stats)
