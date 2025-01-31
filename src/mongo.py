import os
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.environ.get("MONGO_DB_NAME")]
qr_collection = db[os.environ.get("MONGO_QR_COLLECTION")]