from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.utils.security import get_hashed_password
from src.modules.user.model import User


async def init_db(session: AsyncSession) -> None:
    user = await User.get(session, and_(User.username == settings.FIRST_SUPERUSER_USERNAME, User.email == settings.FIRST_SUPERUSER_EMAIL))
    if not user:
        hashed_password = get_hashed_password(
            settings.FIRST_SUPERUSER_PASSWORD)
        await User.create(session, username=settings.FIRST_SUPERUSER_USERNAME, email=settings.FIRST_SUPERUSER_EMAIL, password=hashed_password, role="ADMIN")
