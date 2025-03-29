import json
import os
import re
from dotenv import load_dotenv
from together import Together
from pymongo import MongoClient
import urllib.parse
import time
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init()

# Load environment variables
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# MongoDB Connection Setup
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
MONGO_URI = f"mongodb+srv://suryakf1974:{MONGO_PASSWORD}@cluster0.pgvt85f.mongodb.net/Flights?retryWrites=true&w=majority&appName=Cluster0"


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
        print(f"{Fore.RED}❌ MongoDB query failed: {e}{Style.RESET_ALL}")
        return {"flight_number": flight_number, "status": "Not Found"}
    finally:
        mongo_client.close()


def info_agent_request(flight_number: str) -> str:
    """Calls get_flight_info and returns the data as a JSON string."""
    flight_info = get_flight_info(flight_number)
    return json.dumps(flight_info)


def extract_flight_number(text: str) -> str:
    """Extracts a flight number using regex."""
    match = re.search(r"\b([A-Z]{2,3}\d{2,4})\b", text)
    return match.group(1) if match else None


def qa_agent_respond(user_query: str) -> dict:
    """Processes user query, extracts flight number, and returns structured flight info."""
    
    # Simulate typing effect
    print(f"{Fore.YELLOW}🔍 Processing your query...{Style.RESET_ALL}")
    
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
        return {"answer": "No valid flight number found in your query. Please provide a flight number in the format like 'AI123' or 'EK500'."}

    # Get flight info from Info Agent
    flight_info_json = info_agent_request(flight_number)
    flight_info = json.loads(flight_info_json)

    # Handle "Not Found" case
    if flight_info["status"] == "Not Found":
        return {"answer": f"Flight {flight_number} not found in our database. Please check the flight number and try again."}

    # Construct structured response
    return {
        "answer": f"Flight {flight_info['flight_number']} departs at {flight_info['departure_time']} "
                  f"to {flight_info['destination']}. Current status: {flight_info['status']}.",
        "flight_data": flight_info
    }


def generate_chatbot_response(user_query: str) -> dict:
    """Generate a more conversational response based on the user query"""
    
    # Check if it's a greeting or farewell
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    farewells = ["bye", "goodbye", "see you", "farewell", "exit", "quit"]
    help_queries = ["help", "what can you do", "how does this work", "instructions"]
    
    query_lower = user_query.lower()
    
    # Handle greetings
    if any(greeting in query_lower for greeting in greetings):
        return {
            "answer": "Hello! I'm SkyBot, your flight information assistant. How can I help you today? You can ask me about flight status, departure times, or destinations."
        }
    
    # Handle farewells
    elif any(farewell in query_lower for farewell in farewells):
        return {
            "answer": "Thank you for using SkyBot! Have a safe journey and a wonderful day. Goodbye!"
        }
    
    # Handle help requests
    elif any(help_query in query_lower for help_query in help_queries):
        return {
            "answer": "I can help you find information about flights. Try asking questions like:\n"
                     "- When does Flight AI123 depart?\n"
                     "- What is the status of Flight EK500?\n"
                     "- Tell me about Flight LH789\n"
                     "Just make sure to include a flight number in your question!"
        }
    
    # Check if it's likely a flight query
    elif "flight" in query_lower or re.search(r"\b[A-Z]{2,3}\d{2,4}\b", user_query):
        return qa_agent_respond(user_query)
    
    # General fallback
    else:
        return {
            "answer": "I'm specialized in providing flight information. Please ask me about a specific flight by including the flight number (like AI123 or EK500) in your question."
        }


def simulate_typing(text, delay=0.03):
    """Simulate typing effect for more natural conversation"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def run_chatbot():
    """Run the interactive chatbot interface"""
    
    # Welcome message
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}✈️  Welcome to SkyBot - Your Flight Information Assistant!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Ask about flight status, departure times, or destinations.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Type 'exit' to end the conversation.{Style.RESET_ALL}\n")

    chat_history = []
    
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
        
        if user_input.lower() == "exit":
            print(f"\n{Fore.CYAN}SkyBot: {Style.RESET_ALL}", end="")
            simulate_typing("Thank you for using SkyBot! Have a safe journey! 👋")
            break
        
        # Add to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        # Get response
        response = generate_chatbot_response(user_input)
        
        # Print response with typing effect
        print(f"\n{Fore.CYAN}SkyBot: {Style.RESET_ALL}", end="")
        simulate_typing(response["answer"])
        
        # Add to chat history
        chat_history.append({"role": "assistant", "content": response["answer"]})
        
        # If flight data is available, offer more details
        if "flight_data" in response:
            time.sleep(0.5)
            print(f"\n{Fore.YELLOW}Would you like to know more details about this flight? (yes/no){Style.RESET_ALL}")
            follow_up = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip().lower()
            
            if follow_up in ["yes", "y", "sure", "yeah"]:
                flight_data = response["flight_data"]
                details = (
                    f"\nHere are the complete details for Flight {flight_data['flight_number']}:\n"
                    f"- Departure Time: {flight_data['departure_time']}\n"
                    f"- Destination: {flight_data['destination']}\n"
                    f"- Current Status: {flight_data['status']}\n"
                )
                
                print(f"\n{Fore.CYAN}SkyBot: {Style.RESET_ALL}", end="")
                simulate_typing(details)
        
        print()  # Add a blank line for better readability


if __name__ == "__main__":
    run_chatbot()
