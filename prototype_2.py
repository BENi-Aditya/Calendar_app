# Added preferred start date functionality for multi-day events:
# 1. Introduced `get_start_date()` to handle user input for the start date with validation.
# 2. Updated OpenAI instructions to check for multi-day tasks and use relative day numbers.
# 3. Enhanced parsing logic to calculate dates based on the provided start date for multi-day tasks.
# 4. The main flow now only asks for the start date when necessary, improving scheduling flexibility.




import os
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ics import Calendar, Event
from colorama import Fore, Style, init

# Initialize colorama
init()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

1. For study topics:
   - Analyze the complexity and scope of the topic
   - Estimate total hours needed based on typical study patterns
   - Break down into appropriate session lengths (not limited to 2 hours)
   - Consider topic difficulty when suggesting time slots
   - For multi-day schedules, use relative day numbers (Day 1, Day 2, etc.)

2. For regular tasks:
   - Estimate appropriate duration based on task nature
   - Schedule during suitable hours (e.g., chores in morning/afternoon)

3. Include in your response:
First: Whether this is a multi-day task (Yes/No)
Then format the rest as follows:

Task Analysis:
[Brief analysis of task complexity and time requirements]

Scheduling Plan:
[Task Name]: [Duration] hours
Day: [Day Number]
Time: [HH:MM] - [HH:MM]
Topic/Activity: [Specific subtopic or activity focus for this session]

[Repeat for additional days if needed]"""

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
            
            # Parse and store events
            events = parse_schedule(schedule, start_date)
            all_events.extend(events)
        
        print(f"\n{TerminalStyle.PROMPT}Any other task? (N/n to finish):{TerminalStyle.RESET}")
        more = input().strip().lower()
        if more in ['n', 'no']:
            break
    
    if all_events:
        create_ics_file(all_events)

if __name__ == "__main__":
    main()