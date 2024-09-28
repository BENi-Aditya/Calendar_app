import os
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ics import Calendar, Event

# Load values from the .env file if it exists
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_response(prompt):
    """Get a response from the OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print("Error communicating with OpenAI API:", e)
        return None

def get_event_duration(activity_type):
    """Return a default duration for different activities."""
    durations = {
        "study": 60,   # 60 minutes
        "exercise": 30,  # 30 minutes
        "meeting": 45,   # 45 minutes
        "break": 15      # 15 minutes
    }
    return durations.get(activity_type.lower(), 30)  # Default to 30 minutes if type is unknown

def suggest_event_time_and_duration(event_name, automatic=True):
    """Suggest start time and duration for the event."""
    if automatic:
        prompt = f"Suggest a start time and a duration for the event '{event_name}'. Include the duration in minutes."
        response = get_response(prompt)
        
        # Print the raw response for debugging
        print("API Response:", response)
        
        return parse_response(response)
    else:
        # For manual input, you can handle it separately
        return input("Enter the start time and duration manually.")

def parse_response(response):
    """Parse the API response to extract start time and duration."""
    if response is None or response.strip() == "":
        print("Received an empty response from the API.")
        return None, None  # Handle case where response is None

    try:
        # Print the entire response to understand its structure
        print("Raw Response for Parsing:", response)
        
        # Assuming response is something like "Start at 14:00 and duration is 60 minutes"
        lines = response.split("\n")
        start_time_line = next((line for line in lines if "Start at" in line), None)
        duration_line = next((line for line in lines if "duration" in line), None)

        if not start_time_line or not duration_line:
            print("Could not find expected lines in response.")
            return None, None

        start_time_str = start_time_line.split("at ")[1].strip()
        duration_str = duration_line.split("is ")[1].strip().split(" ")[0]
        
        start_time = datetime.strptime(start_time_str, "%H:%M")
        duration = int(duration_str)

        end_time = start_time + timedelta(minutes=duration)
        return start_time, end_time
    except Exception as e:
        print("Error parsing response:", e)
        return None, None


def create_event(event_name, start_time, end_time):
    """Create an ICS event."""
    event = Event()
    event.name = event_name
    event.begin = start_time
    event.end = end_time

    return event

def main():
    event_name = input("Enter the name of the event: ")
    automatic_time_allocation = input("Do you want automatic time allocation? (yes/no): ").lower() == "yes"

    start_time, end_time = suggest_event_time_and_duration(event_name, automatic_time_allocation)
    
    if start_time and end_time:
        print(f"Event '{event_name}' starts at {start_time} and ends at {end_time}.")
        event = create_event(event_name, start_time, end_time)

        # Save to ICS file
        calendar = Calendar()
        calendar.events.add(event)
        with open('events.ics', 'w') as f:
            f.writelines(calendar)

        print(f"Event saved to events.ics")
    else:
        print("Failed to set event time and duration.")

if __name__ == "__main__":
    main()
