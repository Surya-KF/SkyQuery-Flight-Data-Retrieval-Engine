import os
import urllib.parse
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Encode MongoDB password
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))

# MongoDB Connection URI
MONGO_URI = f"mongodb+srv://suryakf1974:{MONGO_PASSWORD}@cluster0.pgvt85f.mongodb.net/Flights?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client["Flights"]  # Database name
    flights_collection = db["flights"]  # Collection name

    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
