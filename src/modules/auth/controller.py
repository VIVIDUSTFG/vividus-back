from src.modules.auth import service


async def login_controller(session, form_data):
    return await service.login_service(session, form_data)