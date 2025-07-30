from typing import TypeVar, Optional, Generic, List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_snake
from ..db.types import FilterParams, DBModel, ResultWithStatsType


M = TypeVar("M", bound=BaseModel)


schema_model_conf = ConfigDict(
    alias_generator=to_camel,
    from_attributes=True,
    populate_by_name=True,
    use_enum_values=True,
)

ReadModel = TypeVar("ReadModel", bound=BaseModel)
UpdateModel = TypeVar("UpdateModel", bound=BaseModel)
CreateModel = TypeVar("CreateModel", bound=BaseModel)


class Pagination(BaseModel):
    model_config = schema_model_conf
    count_max: Optional[int] = None
    per_page: Optional[int] = None
    count: Optional[int] = None
    page_max: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None
    page_index: Optional[int] = None
    range: Optional[tuple[int, int]] = None


class PaginatedApiResponse(Pagination, Generic[M]):
    model_config = schema_model_conf
    data: Optional[List[M]] = None


