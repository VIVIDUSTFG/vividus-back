import asyncio

from src.core.database.initialise import init_db
from src.core.database.session import SessionLocal


async def init() -> None:
    async with SessionLocal() as session:
        await init_db(session)


async def main() -> None:
    await init()


if __name__ == "__main__":
    asyncio.run(main())
