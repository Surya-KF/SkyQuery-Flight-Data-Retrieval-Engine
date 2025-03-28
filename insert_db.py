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
    exit(1)

# Sample flight data
flights_data_dict = {
    "AI123": {"flight_number": "AI123", "departure_time": "08:00 AM", "destination": "Delhi", "status": "Delayed"},
    "EK500": {"flight_number": "EK500", "departure_time": "10:30 AM", "destination": "Dubai", "status": "On Time"},
    "LH789": {"flight_number": "LH789", "departure_time": "02:00 PM", "destination": "Frankfurt", "status": "Boarding"},
    "EK900": {"flight_number": "EK900", "departure_time": "10:30 AM", "destination": "Kathmandu", "status": "On Time"},
    "LH788": {"flight_number": "LH788", "departure_time": "09:00 PM", "destination": "Coimbatore", "status": "Boarding"},

}

flights_data = list(flights_data_dict.values())

# Insert data into the collection
try:
    result = flights_collection.insert_many(flights_data)
    print("✅ Inserted successfully:", result.inserted_ids)
except Exception as e:
    print(f"❌ Insertion failed: {e}")
finally:
    client.close()
    print("🔒 MongoDB connection closed.")