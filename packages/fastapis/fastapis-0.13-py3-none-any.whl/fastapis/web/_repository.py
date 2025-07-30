from __future__ import annotations
import logging
from typing import Generic, List, Type, TypeVar, Union, Optional

from fastapi import HTTPException


from .types import schema_model_conf, BaseModel
from .types import ReadModel, CreateModel, UpdateModel
from .types import DBModel, FilterParams, ResultWithStatsType

logger = logging.getLogger(__name__)


class BaseRepository(Generic[DBModel, ReadModel, CreateModel, UpdateModel]):
    """
    A base class a "repository", in which database operations simply can be defined,
    by passing in a DB model (SQLAlchemy), and Pydantic Models for Read, Create, Update

    the returned object consists of 4 main actions:

        - list()
            returns a list of items, based on filter params
        - get()
            returns a single item, based on id
        - create()
            creates a new item
        - update()
            updates an existing item
        - delete()
            deletes an item based on id

    """
    def __init__(self, model: Type[DBModel]):
        self.model = model
        super().__init__()

    async def list(
            self, filter_params: FilterParams
    ) -> ResultWithStatsType[ReadModel]:
        results: ResultWithStatsType[ReadModel] = await self.model.query_with_stats(
            offset=filter_params.offset,
            limit=filter_params.limit,
            order_by=filter_params(self.model).order_by,
            group_by=filter_params(self.model).group_by,
            search=filter_params.search,
        )
        return results

    async def get(
            self, item_id: str = None, search: str = None,
    ) -> ReadModel:
        item = None
        if item_id:
            item: DBModel = await self.model.query_single(self.model.id == item_id)
        elif search:
            item: DBModel = await self.model.query_single(search=search)
        if not item:
            raise Exception("Item not found with id '%s'" % item_id)
            # raise HTTPException(404, "could not find item with id '%s'" % item_id)
        return item

    async def update(
            self, item_id: str, data: UpdateModel,
    ) -> ReadModel:
        item: DBModel = await self.model.query_single(self.model.id == item_id)
        for k, v in dict(data).items():
            if not hasattr(item, k):
                logger.warning(
                    "during patching of %s, a key was not found in the to-be-patched object: %s"
                    % (k, item)
                )
                continue
            if getattr(item, k) != v:
                setattr(item, k, v)
        try:
            await item.update()
            return await self.model.query_single(self.model.id == item.id)

        except:  # noqa
            # logger.exception("could not update %s" % item, exc_info=True)
            raise Exception("could not update item with id '%s' and data '%s" % (item_id, data))

    async def delete(self, item_id: str) -> str:
        item: DBModel = await self.model.query_single(self.model.id == item_id)
        try:
            await item.delete()
            return item.id
        except:  # noqa
            raise Exception("could not delete item with id: %s  -> %s" % (item_id, item))
            # raise HTTPException(405, "could not delete item with id '%s'" % item_id)

    async def create(self, data: CreateModel) -> ReadModel:
        item: DBModel = self.model()
        for k, v in dict(data).items():
            if not hasattr(item, k):
                logger.warning(
                    "during creation of %s, a key was not found in the to-be-patched object: %s"
                    % (k, item)
                )
                continue
            setattr(item, k, v)

        # if item._get_relationship_type("user") == User:  # noqa
        #     setattr(item, "user", user)

        try:
            await item.update()
            # this is needed to avoid DetachedstateError for .user attribute
            return await self.model.query_single(self.model.id == item.id)
        except:  # n oqa
            raise Exception("could not create item fromdata '%s'" % (data))


