import os
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ics import Calendar, Event
from colorama import Fore, Style

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Instructions for OpenAI
INSTRUCTIONS = "Suggest a time slot for each task based on their duration."

# Constants
TEMPERATURE = 0.5
MAX_TOKENS = 200

def get_response(instructions, tasks):
    """Get time suggestions from OpenAI for the tasks."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"Allocate time for these tasks: {tasks}"}
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content

def create_ics_file(events, filename="my_schedule.ics"):
    """Create an ICS file for the events."""
    cal = Calendar()
    for task, time in events.items():
        event = Event()
        event.name = task
        event.begin = time.strftime("%Y-%m-%d %H:%M:%S")
        cal.events.add(event)
    with open(filename, 'w') as f:
        f.write(str(cal))

def main():
    print(Fore.GREEN + Style.BRIGHT + "Welcome to the Automatic Time Allocation App!" + Style.RESET_ALL)
    
    # Get user input for tasks
    tasks = input("Please enter the tasks you want to do, separated by commas: ").split(',')
    tasks = [task.strip() for task in tasks]

    # Ask user if they want automatic time allocation
    use_automatic = input("Do you want to automatically allocate time for these tasks? (yes/no): ").strip().lower()
    
    if use_automatic == 'yes':
        # Get time allocation from OpenAI
        time_suggestions = get_response(INSTRUCTIONS, ', '.join(tasks))
        print(Fore.CYAN + Style.BRIGHT + "AI Suggestions: " + Style.NORMAL + time_suggestions)
        
        # Here, you can parse time_suggestions to create events with datetime
        # For now, we'll simulate that with simple incrementing
        start_time = datetime.now()
        events = {task: start_time + timedelta(hours=i) for i, task in enumerate(tasks)}
        
    else:
        events = {}
        for task in tasks:
            task_time = input(f"Please enter the time for '{task}' in format YYYY-MM-DD HH:MM: ")
            events[task] = datetime.strptime(task_time, "%Y-%m-%d %H:%M")
    
    # Create ICS file
    create_ics_file(events)
    print(Fore.GREEN + Style.BRIGHT + "ICS file created successfully: my_schedule.ics" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
