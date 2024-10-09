from typing import List

from pydantic import BaseModel

from src.core.deps import SessionDep
from src.core.utils.security import get_hashed_password
from src.modules.user import model, schema


async def create_user(session, user_in: schema.UserCreate) -> model.User | None:
    hashed_password = get_hashed_password(user_in.password)
    return await model.User.create(session, username=user_in.username, email=user_in.email, password=hashed_password)


async def check_user(session: SessionDep, **kwargs) -> bool:
    return await model.User.exists(session, **kwargs)


async def get_user_details(session: SessionDep, **kwargs) -> model.User | None:
    return await model.User.get(session, **kwargs)


async def update_user(session: SessionDep, old_user: model.User, user_in: BaseModel) -> model.User:
    return await old_user.update(session, **user_in.model_dump(exclude_unset=True))


async def get_users(session: SessionDep) -> List[schema.UserOut]:
    return await model.User.get_multi(session)
