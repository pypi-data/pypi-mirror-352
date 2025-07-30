import logging
from types import NotImplementedType
from typing import Type, List

import fastapi.security.oauth2
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute

from ._repository import BaseRepository
from .types import DBModel, ReadModel, UpdateModel, CreateModel, FilterParams, PaginatedApiResponse
from ..db.types import ResultWithStatsType

logger = logging.getLogger(__name__)


class BaseRouter(APIRouter):
    """
    A base "Router" or fastapi Router.
    by passing in (either):
     - a DB model (SQLAlchemy), and Pydantic Models for Read, Create, Update
     - a Repository object
    it will return a APIRouter derivative, which contains 4 main actions but is of course
    extensible and customizable. All neatly document in FastAPI/OpenAPI docs/spec.

    this router can (should) work together with :ref:Repository
    the returned object consists of 4 main actions:

        - get_items()
            returns a list of items, based on filter params
            route: GET "/"

        - get_item()
            returns a single item, based on id
             route: "GET" "/{item_id:str}"
        - create_item()
            creates a new item
            route: "POST" "/"

        - update_item()
            updates an existing item
            route: "PATCH" "/{item_id:str}"

        - delete()
            deletes an item based on id
            route: "DELETE" "/{item_id:str}"

    """
    def __init__(
            self,
            *,
            db_model: Type[DBModel],
            model_create: Type[ReadModel] = None,
            model_read: Type[CreateModel] = None,
            model_patch: Type[UpdateModel] = None,
            repo_object: BaseRepository = None,
            prefix="",
            tags: List[str] = None,
            dependencies: List = None ,
            security: fastapi.security.oauth2.SecurityBase = None,
            redirect_slashes: bool = True,
            lifespan=None,
            include_in_schema: bool = True
    ):
        """

        :param db_model: the sqlalchemy db model class
        :param model_read: the pydantic model for read(get) operations
        :param model_create: the pydantic model for create(post) operations
        :param model_patch:  the pydantic model for update (patch) operations
        :param repo_object:  a custom repository instance (in case custom logic is needed)
        :param prefix:
        :param tags:
        :param dependencies:
        :param security:
        :param redirect_slashes:
        :param lifespan:
        :param include_in_schema:
        """
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies or [],
            redirect_slashes=redirect_slashes,
            lifespan=lifespan,
            include_in_schema=include_in_schema,
        )
        self.model_read = model_read
        self.model_create = model_create
        self.model_patch = model_patch
        self.security = security
        self.dependencies = dependencies or []
        if repo_object:
            self.repository = repo_object
        else:
            self.repository = BaseRepository[
                db_model, model_read, model_create, model_patch
            ](db_model)
        self.create_default_routes()

    async def list_response_hook(self, response_dict: ResultWithStatsType[ReadModel]):
        """
        a hook which is called before returning the final response of a list call (paginated response)
        this is dirty hack to enable subclassing (since all routes are created within create_default_routes()
        which in turn is a shortcoming in FastApi, which cannot handle the self param.
        this way data can be modified or checked if needed
        """
        return NotImplemented

    async def post_create_hook(self, data: CreateModel) -> CreateModel:
        """
        a hook which is called before further data processing.
        this is dirty hack to enable subclassing (since all routes are created within create_default_routes()
        which in turn is a shortcoming in FastApi, which cannot handle the self param.
        this way data can be modified or checked if needed
        """
        return NotImplemented

    async def get_read_hook(self, response: ReadModel) -> ReadModel:
        """
        a hook which is called before returning the final response of a list call (paginated response)
        this is dirty hack to enable subclassing (since all routes are created within create_default_routes()
        which in turn is a shortcoming in FastApi, which cannot handle the self param.
        this way data can be modified or checked if needed
        :param response:
        :type response:
        :return:
        :rtype:
        """
        return NotImplemented

    async def patch_update_hook(self, data: UpdateModel) -> UpdateModel:
        """
        a hook which is called before further data processing.
        this is dirty hack to enable subclassing (since all routes are created within create_default_routes()
        which in turn is a shortcoming in FastApi, which cannot handle the self param.
        this way data can be modified or checked if needed
        """
        return NotImplemented

    def create_default_routes(self):

        # these 3 are the response models passed in at __init__, and now used to annotate the return type of
        # our routes
        ModelRead = self.model_read  # noqa
        ModelCreate = self.model_create  # noqa
        ModelPatch = self.model_patch  # noqa

        self.routes.clear()

        extra = {}
        deps = []
        if self.security:
            self.dependencies.append(self.security)
            # extra.update(dependencies=[Depends(self.security)])
            # extra.update(dependencies=extra["dependencies"] + [*self.dependencies])

        self.dependencies = [Depends(x) if not hasattr(x, 'dependency') else x for x in self.dependencies]

        async def get_items(
                filter_params: FilterParams = Depends(FilterParams)
        ) -> PaginatedApiResponse[ModelRead]:
            r: ResultWithStatsType[ReadModel] = await self.repository.list(filter_params)

            x = await self.list_response_hook(r)
            if not isinstance(x, NotImplementedType):
                return x
            return r

        async def get_item(
                item_id: str,
        ) -> ModelRead:
            r = await self.repository.get(item_id)
            x = await self.get_read_hook(r)
            if not isinstance(x, NotImplementedType):
                return x
            return r

        async def create_item(
                data: ModelCreate
        ) -> ModelRead:
            x = await self.post_create_hook(data)
            if not isinstance(x, NotImplementedType):
                data = x
            return await self.repository.create(data)

        async def update_item(
                item_id: str, data: ModelPatch
        ) -> ModelRead:
            x = await self.patch_update_hook(data)
            if not isinstance(x, NotImplementedType):
                data = x
            return await self.repository.update(item_id, data)

        async def delete_item(item_id: str) -> str:
            return await self.repository.delete(item_id)

        self.add_api_route("/", get_items, methods=["GET"])
        self.add_api_route("/{item_id:str}", get_item, methods=["GET"])
        self.add_api_route("/", create_item, methods=["POST"])
        self.add_api_route("/{item_id:str}", update_item, methods=["PATCH"])
        self.add_api_route("/{item_id:str}", delete_item, methods=["DELETE"])
        return self

    def replace_route(self, index: int, new_route: APIRoute):
        self.routes[index] = new_route
        return self
