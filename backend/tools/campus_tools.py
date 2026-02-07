from motor.motor_asyncio import AsyncIOMotorClient
import os

mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = mongo[os.environ["DB_NAME"]]


async def get_events():
    return await db.events.find(
        {"status": "upcoming"},
        {"_id": 0}
    ).to_list(10)


async def get_facilities():
    return await db.facilities.find(
        {"status": "available"},
        {"_id": 0}
    ).to_list(10)


async def create_booking(data: dict):
    await db.bookings.insert_one(data)
    return {
        "status": "confirmed",
        "booking": data
    }
