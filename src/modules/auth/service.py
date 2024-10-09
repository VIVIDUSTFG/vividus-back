from src.core.utils.security import verify_password
from src.modules.user.model import User


async def login_service(session, form_data):
    user = await User.get(session, username=form_data.username)
    if user and verify_password(form_data.password, user.password):
        return user

    return None
