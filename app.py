import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta
from ics import Calendar, Event
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Calendar API settings
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simulated user database (replace with a real database in production)
users = {
    "user1": "password1",
    "user2": "password2"
}

# Simulated events storage (replace with a real database in production)
events = []

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        event_name = request.form['event-name']
        event_date = request.form.get('event-date')
        event_time = request.form.get('event-time')
        
        if not event_date or not event_time:
            # AI scheduling
            ai_suggestion = get_ai_suggestion(event_name)
            event_date = ai_suggestion['date']
            event_time = ai_suggestion['time']
        
        new_event = {
            'name': event_name,
            'date': event_date,
            'time': event_time
        }
        events.append(new_event)
        
        # Create ICS file
        create_ics_file(new_event)
        
        # Add to Google Calendar
        add_to_google_calendar(new_event)
        
        return jsonify({'success': True})
    
    return render_template('add_event.html')

@app.route('/get_events')
def get_events():
    if 'username' not in session:
        return jsonify([])
    return jsonify(events)

@app.route('/ai_schedule', methods=['POST'])
def ai_schedule():
    event_name = request.json['event_name']
    suggestion = get_ai_suggestion(event_name)
    return jsonify(suggestion)

def get_ai_suggestion(event_name):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a scheduling assistant. Suggest a date and time for the given event."},
                {"role": "user", "content": f"Suggest a date and time for: {event_name}"}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        suggestion = response.choices[0].message.content
        # Parse the suggestion to extract date and time (you may need to adjust this based on the AI's output format)
        date, time = suggestion.split(',')
        return {'date': date.strip(), 'time': time.strip()}
    except Exception as e:
        print(f"Error in AI suggestion: {str(e)}")
        # Return a default suggestion if AI fails
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'time': '09:00'}

def create_ics_file(event):
    cal = Calendar()
    ics_event = Event()
    ics_event.name = event['name']
    event_datetime = datetime.strptime(f"{event['date']} {event['time']}", '%Y-%m-%d %H:%M')
    ics_event.begin = event_datetime
    ics_event.end = event_datetime + timedelta(hours=1)  # Assume 1-hour duration
    cal.events.add(ics_event)
    
    with open('event.ics', 'w') as f:
        f.writelines(cal.serialize_iter())

def get_google_calendar_credentials():
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

def add_to_google_calendar(event):
    try:
        creds = get_google_calendar_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        event_datetime = datetime.strptime(f"{event['date']} {event['time']}", '%Y-%m-%d %H:%M')
        end_datetime = event_datetime + timedelta(hours=1)  # Assume 1-hour duration
        
        calendar_event = {
            'summary': event['name'],
            'start': {
                'dateTime': event_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=calendar_event).execute()
        print(f"Event added to Google Calendar: {event.get('htmlLink')}")
    except HttpError as error:
        print(f"Error adding event to Google Calendar: {error}")

if __name__ == "__main__":
    app.run(debug=True)