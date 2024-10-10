# Now it works with Google Calendar too !!!
import os
from urllib.request import Request
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ics import Calendar, Event
from colorama import Fore, Style, init
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Initialize colorama
init()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Calendar API settings
SCOPES = ['https://www.googleapis.com/auth/calendar']

class TerminalStyle:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    SUBHEADER = Fore.CYAN + Style.BRIGHT
    PROMPT = Fore.GREEN + Style.BRIGHT
    INFO = Fore.BLUE + Style.NORMAL
    SUCCESS = Fore.GREEN + Style.NORMAL
    WARNING = Fore.YELLOW + Style.NORMAL
    ERROR = Fore.RED + Style.BRIGHT
    TASK = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL

def get_calendar_choice():
    """Get user's preferred calendar type."""
    while True:
        print(f"\n{TerminalStyle.PROMPT}Choose your calendar option:{TerminalStyle.RESET}")
        print("1. ICS File")
        print("2. Google Calendar")
        choice = input(f"{TerminalStyle.PROMPT}Enter your choice (1 or 2):{TerminalStyle.RESET} ").strip()
        
        if choice in ['1', '2']:
            return int(choice)
        print(f"{TerminalStyle.WARNING}Invalid choice! Please enter 1 or 2.{TerminalStyle.RESET}")

def get_google_calendar_credentials():
    """Get or refresh Google Calendar credentials."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

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

def get_task_schedule(task):
    """Get intelligent time suggestions from OpenAI for the task."""
    try:
        system_prompt = """You are a scheduling assistant. For any given task, provide a schedule in the following format:

Is this a multi-day task? (Answer with just 'Yes' or 'No' on the first line)

Task Analysis:
[Provide a brief analysis of the task's complexity and requirements]

Scheduling Plan:
[Task Name]: [Estimated Duration] hours
Day: [Day Number]
Time: [Start Time] - [End Time]
Topic/Activity: [Specific focus for this session]

Example response:
Yes

Task Analysis:
This is a complex study topic requiring multiple sessions.

Scheduling Plan:
Advanced Mathematics: 2 hours
Day: 1
Time: 09:00 - 11:00
Topic/Activity: Introduction and basic concepts"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a detailed schedule for: {task}"}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        schedule = response.choices[0].message.content
        
        # Validate response format
        if not schedule or not any(x in schedule for x in ['Task Analysis:', 'Scheduling Plan:']):
            print(f"{TerminalStyle.ERROR}Error: Invalid response format from AI. Please try again.{TerminalStyle.RESET}")
            return None
            
        return schedule
        
    except openai.error.OpenAIError as e:
        print(f"{TerminalStyle.ERROR}OpenAI API Error: {str(e)}{TerminalStyle.RESET}")
        return None
    except Exception as e:
        print(f"{TerminalStyle.ERROR}Unexpected error: {str(e)}{TerminalStyle.RESET}")
        return None

def parse_schedule(schedule_text, start_date):
    """Parse the OpenAI response into structured event data."""
    if not schedule_text:
        return []
        
    events = []
    lines = schedule_text.split('\n')
    
    try:
        # Find the main sections
        is_multi_day = lines[0].lower().startswith('yes')
        
        analysis_start = -1
        schedule_start = -1
        
        for i, line in enumerate(lines):
            if 'Task Analysis:' in line:
                analysis_start = i
            elif 'Scheduling Plan:' in line:
                schedule_start = i
                break
        
        if analysis_start == -1 or schedule_start == -1:
            print(f"{TerminalStyle.ERROR}Error: Could not find required sections in the response{TerminalStyle.RESET}")
            return []
            
        # Print analysis
        analysis = '\n'.join(lines[analysis_start+1:schedule_start]).strip()
        print(f"\n{TerminalStyle.SUBHEADER}Task Analysis:{TerminalStyle.RESET}")
        print(f"{TerminalStyle.INFO}{analysis}{TerminalStyle.RESET}")
        print(f"\n{TerminalStyle.SUBHEADER}Scheduled Sessions:{TerminalStyle.RESET}")
        
        # Parse schedule
        current_task = None
        current_day = None
        schedule_lines = lines[schedule_start+1:]
        
        for line in schedule_lines:
            line = line.strip()
            if not line:
                continue
                
            if ': ' in line and not any(x in line.lower() for x in ['day:', 'time:', 'topic:']):
                current_task = line.split(':')[0].strip()
                continue
                
            if line.startswith('Day: '):
                try:
                    day_num = int(line.replace('Day: ', '').split()[0]) - 1
                    current_day = start_date + timedelta(days=day_num)
                except ValueError:
                    print(f"{TerminalStyle.WARNING}Warning: Invalid day format in line: {line}{TerminalStyle.RESET}")
                    continue
                    
            elif line.startswith('Time: '):
                try:
                    time_str = line.replace('Time: ', '')
                    start_time_str, end_time_str = time_str.split(' - ')
                    
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()
                    
                    if current_task and current_day:
                        start_datetime = datetime.combine(current_day, start_time)
                        end_datetime = datetime.combine(current_day, end_time)
                        
                        events.append({
                            'name': current_task,
                            'start': start_datetime,
                            'end': end_datetime
                        })
                        
                        duration = (end_datetime - start_datetime).total_seconds() / 3600
                        print(f"{TerminalStyle.TASK}• {current_task}{TerminalStyle.RESET}")
                        print(f"  📅 {current_day.strftime('%d/%m/%y')}")
                        print(f"  🕒 {start_time_str} - {end_time_str} ({duration:.1f} hours)")
                        
                except ValueError as e:
                    print(f"{TerminalStyle.WARNING}Warning: Invalid time format in line: {line}{TerminalStyle.RESET}")
                    continue
                    
        return events
        
    except Exception as e:
        print(f"{TerminalStyle.ERROR}Error parsing schedule: {str(e)}{TerminalStyle.RESET}")
        return []

def add_to_google_calendar(events):
    """Add events to Google Calendar."""
    try:
        creds = get_google_calendar_credentials()
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
            
            service.events().insert(calendarId='primary', body=event).execute()
        
        print(f"\n{TerminalStyle.SUCCESS}✨ Events successfully added to Google Calendar{TerminalStyle.RESET}")
        print(f"{TerminalStyle.INFO}Total events scheduled: {len(events)}{TerminalStyle.RESET}\n")
        
    except HttpError as error:
        print(f"{TerminalStyle.WARNING}Error accessing Google Calendar: {error}{TerminalStyle.RESET}")

def create_ics_file(events, filename="my_schedule.ics"):
    """Create an ICS file for the events."""
    calendar = Calendar()
    
    for event_data in events:
        event = Event()
        event.name = event_data['name']
        event.begin = event_data['start']
        event.end = event_data['end']
        calendar.events.add(event)

    with open(filename, 'w') as f:
        f.writelines(calendar.serialize_iter())
    
    print(f"{TerminalStyle.SUCCESS}✨ ICS file '{filename}' created successfully!{TerminalStyle.RESET}")

def main():
    print(f"{TerminalStyle.HEADER}Welcome to the Smart Calendar Management App!{TerminalStyle.RESET}")

    tasks = []
    while True:
        task = input(f"{TerminalStyle.PROMPT}Enter a task (or 'done' to finish):{TerminalStyle.RESET} ")
        if task.lower() == 'done':
            break
        tasks.append(task)

    if not tasks:
        print(f"{TerminalStyle.WARNING}No tasks provided. Exiting.{TerminalStyle.RESET}")
        return

    start_date = get_start_date()
    events = []

    for task in tasks:
        schedule = get_task_schedule(task)
        events.extend(parse_schedule(schedule, start_date))

    calendar_choice = get_calendar_choice()

    if calendar_choice == 1:
        create_ics_file(events)
    elif calendar_choice == 2:
        add_to_google_calendar(events)

if __name__ == "__main__":
    main()