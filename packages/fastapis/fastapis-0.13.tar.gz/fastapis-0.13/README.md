Faster**Apis**
====================
just a pet project for own use.

as the name implies, this let's you create FastAPI's combined with SQLAlchemy even FASTER.

the db module has a Base object which you can build db models upon.
it gives every model useful methods and fields.
eg:

```python
from fastapis import Base, Mapped 

class MyModel(Base):
    username: Mapped[str]
    password: Mapped[str]

obj = MyModel()
```

### await obj.update()   

commit to database, whether it is create of update

### obj.updated_at
gives a timestamp of last modification to the object
1748424353 

### obj.created_at
gives a timestamp of creation time
1748107770

### obj.id
by default uses uuid4
'edb45110-6520-42e6-9eaf-cd8b11df5e6f'

### obj.id_
internal id
2 

### await obj.query()
returns all objects
[<some.module.Object at 0x71418e77b970>,
 <some.module.Object at 0x71418e77a4d0>]

### obj.dict
converts to json serializable dict 
{"username": "myname",
"created_at": 124233,
"updated_at": 342423,
"id": ...
"id_": ...
}


### await obj.query(MyModel.password == "something", order_by=MyModel.username.desc(), limit=10, offset=4)
use filters to query database


### await obj.query_single()
returns a single (latest) item. also works with filters  like obj.query()


### await obj.query_with_stats()
same as query() but returns a ResultWithStatsType, containing stats like total count,
pagination etc.

- data: list of objects, just like regular query(), but this always is a list 
- count_max: 634222, 
- per_page: 16, 
- count: 16, 
- page_max: 39639, 
- has_next: True, 
- has_prev: False,
- page_index: 0, 
- range: (0, 63422)




# **Full example Fastapi and SQLAlchemy**

```python
from __future__ import annotations

from typing import Optional

from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.testing.schema import mapped_column

from fastapis.db import Base, Mapped, relationship, ForeignKey
from fastapis.web import BaseRouter
from fastapis.web import app
from fastapis.web.types import schema_model_conf, BaseModel


# database models

class DBUser(Base):
    __tablename__ = "db_user"

    username: Mapped[str]
    password: Mapped[Optional[str]]
    token: Mapped[DBToken] = relationship(uselist=False, lazy="selectin")


class DBToken(Base):
    __tablename__ = "db_token"

    value: Mapped[str]
    user_id: Mapped[DBUser] = mapped_column(ForeignKey("db_user.id"))


# fastapi (pydantic) models

class UserRead(BaseModel):
    model_config = schema_model_conf
    username: str
    password: Optional[str] = None
    token: Optional[TokenRead] = None


class UserCreate(BaseModel):
    username: str
    password: str


class TokenRead(BaseModel):
    model_config = schema_model_conf
    value: Optional[str]


# fastapi security

security = OAuth2PasswordBearer(tokenUrl="/token")


# manual route for tokens

@app.post("/token")
async def get_token():
    return dict(access_token="123", token_type="Bearer")


# dependency

async def some_dependency():
    yield "test"


# router for users
# creates all route handlers for CRUD

user_router = BaseRouter(
    db_model=DBUser,
    model_read=UserRead,
    model_create=UserCreate,
    model_patch=UserCreate,
    security=security,
    dependencies=[some_dependency]
)

# include the above router
app.include_router(user_router, prefix="/user", tags=["user"])

# done!

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

Result
-----------------------
![output api](img.png "Output API")