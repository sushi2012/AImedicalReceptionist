
import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dental_clinic")

client: AsyncMongoClient | None = None
database: AsyncDatabase | None = None


async def connect_to_mongodb() -> None:
    """Create one MongoDB connection and verify it works."""
    global client, database

    if client is not None and database is not None:
        return

    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI is missing from the environment")

    new_client = AsyncMongoClient(MONGODB_URI)

    try:
        await new_client.admin.command("ping")
        client = new_client
        database = new_client[DATABASE_NAME]
        print("Connected to MongoDB successfully!")
    except Exception:
        await new_client.close()
        raise


def get_database() -> AsyncDatabase:
    """Return the database after the connection is initialized."""
    if database is None:
        raise RuntimeError(
            "MongoDB is not connected. "
            "Call connect_to_mongodb() first."
        )

    return database


async def close_mongodb_connection() -> None:
    """Close the connection when the application shuts down."""
    global client, database

    if client is not None:
        await client.close()

    client = None
    database = None
