import asyncio
from app.database.mongodb import (
    connect_to_mongodb,
    check_mongodb_connection,
)


async def main():
    await connect_to_mongodb()
    await check_mongodb_connection()


asyncio.run(main())
