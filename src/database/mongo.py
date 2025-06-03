from motor.motor_asyncio import AsyncIOMotorClient

from src.config import MONGO_USER, MONGO_PASSWORD


uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.ej2wy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(uri)
db = client.Quiz_Tg_Bot
quiz_collection = db.Quizes
