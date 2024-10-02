import os
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ics import Calendar, Event
from colorama import Fore, Style, init
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Initialize colorama
init()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Terminal styling
class TerminalStyle:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    SUBHEADER = Fore.CYAN + Style.BRIGHT
    PROMPT = Fore.GREEN + Style.BRIGHT
    INFO = Fore.BLUE + Style.NORMAL
    SUCCESS = Fore.GREEN + Style.NORMAL
    WARNING = Fore.YELLOW + Style.NORMAL
    TASK = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL

def get_start_date():
    """Get preferred start date from user."""
    while True:
        print(f"\n{TerminalStyle.PROMPT}Enter preferred start date (dd/mm/yy) or press Enter for today:{TerminalStyle.RESET}")
        date_input = input().strip()
        
        if not date_input:  # User pressed Enter, use today
            return datetime.now().date()
        
        try:
            return datetime.strptime(date_input, "%d/%m/%y").date()
        except ValueError:
            print(f"{TerminalStyle.WARNING}Invalid date format! Please use dd/mm/yy (e.g., 15/03/24){TerminalStyle.RESET}")

# Updated Instructions for OpenAI
INSTRUCTIONS = """Analyze the given task and create an intelligent scheduling plan following these guidelines:
...
"""

def get_task_schedule(task):
    """Get intelligent time suggestions from OpenAI for the task."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": f"Create a detailed schedule for: {task}"}
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content

def parse_schedule(schedule_text, start_date):
    """Parse the OpenAI response into structured event data."""
    events = []
    
    # First, check if it's a multi-day task
    lines = schedule_text.split('\n')
    is_multi_day = False
    analysis_start = 0
    
    for i, line in enumerate(lines):
        if line.lower().startswith('yes'):
            is_multi_day = True
            analysis_start = i + 1
            break
        elif line.lower().startswith('no'):
            analysis_start = i + 1
            break
    
    # Get analysis and schedule sections
    schedule_text = '\n'.join(lines[analysis_start:])
    sections = schedule_text.split("\nScheduling Plan:\n")
    if len(sections) != 2:
        print(f"{TerminalStyle.WARNING}Warning: Unexpected response format{TerminalStyle.RESET}")
        return events
    
    analysis = sections[0].replace("Task Analysis:\n", "").strip()
    schedule = sections[1].strip()
    
    # Print the analysis
    print(f"\n{TerminalStyle.SUBHEADER}Task Analysis:{TerminalStyle.RESET}")
    print(f"{TerminalStyle.INFO}{analysis}{TerminalStyle.RESET}")
    print(f"\n{TerminalStyle.SUBHEADER}Scheduled Sessions:{TerminalStyle.RESET}")
    
    # Parse schedule entries
    current_task = None
    current_day = None
    
    for line in schedule.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if ': ' in line and 'Day:' not in line and 'Time:' not in line and 'Topic:' not in line:
            current_task = line.split(': ')[0]
            continue
            
        if line.startswith('Day: '):
            day_num = int(line.replace('Day: ', '').split()[0]) - 1  # Convert to 0-based index
            current_day = start_date + timedelta(days=day_num)
        elif line.startswith('Time: '):
            time_str = line.replace('Time: ', '')
            start_time_str, end_time_str = time_str.split(' - ')
            
            try:
                start_time = datetime.combine(current_day, 
                    datetime.strptime(start_time_str, "%H:%M").time())
                end_time = datetime.combine(current_day, 
                    datetime.strptime(end_time_str, "%H:%M").time())
                
                if current_task:
                    events.append({
                        'name': current_task,
                        'start': start_time,
                        'end': end_time
                    })
                    
                    # Print friendly format
                    duration = (end_time - start_time).total_seconds() / 3600
                    print(f"{TerminalStyle.TASK}• {current_task}{TerminalStyle.RESET}")
                    print(f"  📅 {current_day.strftime('%d/%m/%y')}")
                    print(f"  🕒 {start_time_str} - {end_time_str} ({duration:.1f} hours)")
                    
            except ValueError as e:
                print(f"{TerminalStyle.WARNING}Error parsing datetime: {e}{TerminalStyle.RESET}")
    
    return events

def create_ics_file(events, filename="my_schedule.ics"):
    """Create an ICS file for the events."""
    cal = Calendar()
    for event_data in events:
        event = Event()
        event.name = event_data['name']
        event.begin = event_data['start']
        event.end = event_data['end']
        cal.events.add(event)
    
    with open(filename, 'w') as f:
        f.write(str(cal))
    
    if os.path.exists(filename):
        print(f"\n{TerminalStyle.SUCCESS}✨ Schedule saved to '{filename}'{TerminalStyle.RESET}")
        print(f"{TerminalStyle.INFO}Total events scheduled: {len(events)}{TerminalStyle.RESET}\n")
    else:
        print(f"\n{TerminalStyle.WARNING}❌ Error: Failed to create schedule file{TerminalStyle.RESET}\n")

def add_events_to_google_calendar(events):
    """Add the scheduled events to the user's Google Calendar."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    for event_data in events:
        event = {
            'summary': event_data['name'],
            'start': {
                'dateTime': event_data['start'].isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_data['end'].isoformat(),
                'timeZone': 'UTC',
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

def main():
    print(f"\n{TerminalStyle.HEADER}🗓️  Smart Calendar Management App{TerminalStyle.RESET}")
    print(f"{TerminalStyle.INFO}Let's create your intelligent schedule!{TerminalStyle.RESET}\n")
    
    all_events = []
    
    while True:
        print(f"{TerminalStyle.PROMPT}Tell us what you want to do:{TerminalStyle.RESET}")
        task = input().strip()
        
        if task:
            print(f"\n{TerminalStyle.INFO}Analyzing task and generating personalized schedule...{TerminalStyle.RESET}")
            
            # Get schedule
            schedule = get_task_schedule(task)
            
            # Check if it's a multi-day task
            is_multi_day = schedule.lower().startswith('yes')
            
            # Get start date if it's a multi-day task
            start_date = get_start_date() if is_multi_day else datetime.now().date()
            
            # Parse schedule
            events = parse_schedule(schedule, start_date)
            
            if events:
                all_events.extend(events)
            
        print(f"\n{TerminalStyle.PROMPT}Do you want to add another task? (y/n):{TerminalStyle.RESET}")
        if input().strip().lower() != 'y':
            break
    
    if all_events:
        print(f"\n{TerminalStyle.PROMPT}Choose your saving method: (1) ICS file (2) Google Calendar{TerminalStyle.RESET}")
        choice = input().strip()
        
        if choice == '1':
            create_ics_file(all_events)
        elif choice == '2':
            add_events_to_google_calendar(all_events)
        else:
            print(f"{TerminalStyle.WARNING}Invalid choice! Please select a valid option.{TerminalStyle.RESET}")

if __name__ == '__main__':
    main()
