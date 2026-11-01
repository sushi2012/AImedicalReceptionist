import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dental_clinic")

client: AsyncMongoClient | None = None
database: AsyncDatabase | None = None


async def connect_to_mongodb() -> None:
    """Create one MongoDB connection and verify it works."""
    global client, database

    if client is not None and database is not None:
        return

    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is missing from the environment")

    new_client = AsyncMongoClient(MONGODB_URL)

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


def get_client() -> AsyncMongoClient:
    """Return the MongoDB client for starting transactions."""
    if client is None:
        raise RuntimeError(
            "MongoDB is not connected. "
            "Call connect_to_mongodb() first."
        )

    return client


async def close_mongodb_connection() -> None:
    """Close the connection when the application shuts down."""
    global client, database

    if client is not None:
        await client.close()

    client = None
    database = None


async def check_mongodb_connection() -> bool:
    """Ping MongoDB to verify the connection is alive."""
    if client is None:
        print("MongoDB connection failed: client is not initialised. Call connect_to_mongodb() first.")
        return False
    try:
        await client.admin.command("ping")
        print("MongoDB connected successfully!")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False
