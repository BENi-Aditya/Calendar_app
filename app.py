import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
from ics import Calendar, Event
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Google Calendar API settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
flow = Flow.from_client_secrets_file(
    'credentials.json',
    scopes=SCOPES)
flow.redirect_uri = 'http://localhost:5000/oauth2callback'

def get_google_calendar_service():
    if 'credentials' not in session:
        return None
    credentials = Credentials(**session['credentials'])
    return build('calendar', 'v3', credentials=credentials)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'Aditya' and password == '1234':
        session['user'] = username
        return redirect(url_for('homepage'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('login'))

@app.route('/homepage')
def homepage():
    if 'user' not in session:
        return redirect(url_for('login'))
    today = datetime.now()
    events = get_events_for_month(today.year, today.month)
    return render_template('homepage.html', current_month=today.strftime("%B %Y"), events=events)

@app.route('/add_event')
def add_event():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('add_event.html')

@app.route('/ai_schedule', methods=['GET', 'POST'])
def ai_schedule():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        event_description = request.form.get('event_description')
        ai_suggestion = get_ai_suggestion(event_description)
        
        if ai_suggestion:  # Check if AI suggestion was received
            # Split the suggestion into date and time
            date_time_parts = ai_suggestion.split(' ')
            event_date = date_time_parts[0]
            event_time = date_time_parts[1]
            return render_template('ai_schedule.html', suggestion=ai_suggestion, description=event_description, date=event_date, time=event_time)
        else:
            flash("Could not get suggestion from AI. Please try again.")
            return redirect(url_for('ai_schedule'))
    
    return render_template('ai_schedule.html')

@app.route('/save_ai_event', methods=['POST'])
def save_ai_event():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    event_description = request.form.get('event_description')
    event_date = request.form.get('event_date')
    event_time = request.form.get('event_time')
    
    create_and_add_event(event_description, event_date, event_time)
    return redirect(url_for('homepage'))

@app.route('/manual_schedule', methods=['GET', 'POST'])
def manual_schedule():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        event_description = request.form.get('event_description')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        create_and_add_event(event_description, event_date, event_time)
        return redirect(url_for('homepage'))
    
    return render_template('manual_schedule.html')

@app.route('/authorize')
def authorize():
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    flow.fetch_token(code=request.args.get('code'))
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('homepage'))

def get_ai_suggestion(description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that suggests event dates and times. Provide your suggestion in the format 'YYYY-MM-DD HH:MM'."},
                {"role": "user", "content": f"Suggest a date and time for this event: {description}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error in get_ai_suggestion: {str(e)}")
        return None

def create_and_add_event(description, date, time):
    # Create ICS file
    calendar = Calendar()
    event = Event()
    event.name = description
    event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    event.begin = event_datetime
    event.end = event_datetime + timedelta(hours=1)  # Assume 1-hour duration
    calendar.events.add(event)
    
    with open('event.ics', 'w') as f:
        f.writelines(calendar.serialize_iter())
    
    # Add to Google Calendar
    service = get_google_calendar_service()
    if service:
        event = {
            'summary': description,
            'start': {
                'dateTime': event_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (event_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
        }
        try:
            service.events().insert(calendarId='primary', body=event).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")

def get_events_for_month(year, month):
    # Replace this with actual database logic to retrieve user-added events
    # Placeholder: return an empty list or fetch from your database
    return []

if __name__ == '__main__':
    app.run(debug=True)
