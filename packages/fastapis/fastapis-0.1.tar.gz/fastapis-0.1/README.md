Faster**Apis**
====================
just a pet project for own use.

as the name implies, this let's you create FastAPI's combined with SQLAlchemy even FASTER.


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