import json
import os
import re
from dotenv import load_dotenv
from together import Together
from pymongo import MongoClient
import urllib.parse

# Load environment variables
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# MongoDB Connection Setup
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
MONGO_URI = f"mongodb+srv://suryakf1974:{MONGO_PASSWORD}@cluster0.pgvt85f.mongodb.net/Flights?retryWrites=true&w=majority&appName=Cluster0"


# 1️⃣ Flight database retrieval from MongoDB
def get_flight_info(flight_number: str) -> dict:
    """Retrieves structured flight data for a given flight number from MongoDB."""
    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["Flights"]
        flights_collection = db["flights"]

        # Query MongoDB for flight info
        flight_info = flights_collection.find_one({"flight_number": flight_number})

        if flight_info:
            # Remove MongoDB's internal '_id' field and return the data
            flight_info.pop('_id', None)
            return flight_info
        return {"flight_number": flight_number, "status": "Not Found"}

    except Exception as e:
        print(f"❌ MongoDB query failed: {e}")
        return {"flight_number": flight_number, "status": "Not Found"}
    finally:
        mongo_client.close()


# 2️⃣ Info Agent (strictly JSON response)
def info_agent_request(flight_number: str) -> str:
    """Calls get_flight_info and returns the data as a JSON string."""
    flight_info = get_flight_info(flight_number)
    return json.dumps(flight_info)


# 3️⃣ Improved Flight Number Extraction
def extract_flight_number(text: str) -> str:
    """Extracts a flight number using regex."""
    match = re.search(r"\b([A-Z]{2,3}\d{2,4})\b", text)
    return match.group(1) if match else None


# 4️⃣ QA Agent (extracts flight number, fetches info, and returns JSON)
def qa_agent_respond(user_query: str) -> str:
    """Processes user query, extracts flight number, and returns structured flight info."""

    # Call Together AI for better flight number extraction
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
            {"role": "system",
             "content": "Extract the flight number from the query and return ONLY the flight number."},
            {"role": "user", "content": user_query},
        ],
    )
    flight_number = response.choices[0].message.content.strip()

    # If AI fails, use regex extraction
    if not re.match(r"^[A-Z]{2,3}\d{2,4}$", flight_number):
        flight_number = extract_flight_number(user_query)

    # If no valid flight number is found
    if not flight_number:
        return json.dumps({"answer": "No valid flight number found in the query."})

    # Get flight info from Info Agent
    flight_info_json = info_agent_request(flight_number)
    flight_info = json.loads(flight_info_json)

    # Handle "Not Found" case exactly as required
    if flight_info["status"] == "Not Found":
        return json.dumps({"answer": f"Flight {flight_number} not found in database."})

    # Construct structured response
    answer = {
        "answer": f"Flight {flight_info['flight_number']} departs at {flight_info['departure_time']} "
                  f"to {flight_info['destination']}. Current status: {flight_info['status']}."
    }

    return json.dumps(answer)


# 🎯 Interactive User Input Mode
if __name__ == "__main__":
    print("✈️  Welcome to the Airline QA System!")
    print("Ask about a flight (e.g., 'When does Flight AI123 depart?') or type 'exit' to quit.")

    while True:
        user_input = input("🔍 Your question: ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye! Have a safe journey!")
            break

        response_json = qa_agent_respond(user_input)
        print(f"🤖 AI Response: {response_json}")