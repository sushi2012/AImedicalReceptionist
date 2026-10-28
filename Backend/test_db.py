
import asyncio

from app.database.mongodb import (
    connect_to_mongodb,
    get_database,
    close_mongodb_connection,
)


async def main():
    try:
        await connect_to_mongodb()

        db = get_database()

        print("Database selected:", db.name)
        print("MongoDB connection test passed!")

    finally:
        await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(main())
