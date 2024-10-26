from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from openai import OpenAI
from ics import Calendar, Event as ICSEvent
import pytz
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mayday.db'
db = SQLAlchemy(app)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Calendar API settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_CONFIG = json.loads(os.getenv("GOOGLE_CLIENT_CONFIG"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('homepage'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Log the login attempt
        print(f"Login attempt - Email: {email}, Password: {password}")
        
        # Set a dummy user ID in the session
        session['user_id'] = 1
        
        # Redirect to homepage
        return redirect(url_for('homepage'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    events = Event.query.filter_by(user_id=session['user_id']).all()
    return render_template('homepage.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time'])
        new_event = Event(user_id=session['user_id'], title=title, start_time=start_time, end_time=end_time)
        db.session.add(new_event)
        db.session.commit()
        
        # Add event to Google Calendar
        if 'credentials' in session:
            credentials = Credentials(**session['credentials'])
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': title,
                'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
            }
            service.events().insert(calendarId='primary', body=event).execute()
        
        return redirect(url_for('homepage'))
    return render_template('add_event.html')

@app.route('/ai_schedule', methods=['GET', 'POST'])
def ai_schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        description = request.form['description']
        try:
            # Get current date and time
            now = datetime.now(pytz.UTC)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a scheduling assistant. Suggest a specific date and time for the following event. The date should be between tomorrow and 30 days from now. Provide a time between 9:00 AM and 9:00 PM. Respond in the format: 'DD/MM/YY HH:MM'. Also suggest a duration for the event."},
                    {"role": "user", "content": f"Current date and time: {now.strftime('%d/%m/%y %H:%M')}. Suggest a date, time, and duration for: {description}"}
                ]
            )
            suggestion = response.choices[0].message.content
            
            # Parse the suggestion
            match = re.search(r'(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2})', suggestion)
            duration_match = re.search(r'duration.*?(\d+)\s*(hour|minute)', suggestion, re.IGNORECASE)
            
            if match and duration_match:
                suggested_datetime = datetime.strptime(match.group(1) + ' ' + match.group(2), '%d/%m/%y %H:%M')
                suggested_datetime = pytz.timezone('UTC').localize(suggested_datetime)
                
                duration = int(duration_match.group(1))
                duration_unit = duration_match.group(2).lower()
                
                if duration_unit == 'hour':
                    duration_delta = timedelta(hours=duration)
                else:
                    duration_delta = timedelta(minutes=duration)
                
                # Ensure suggested time is in the future
                if suggested_datetime <= now:
                    suggested_datetime += timedelta(days=1)
                
                # Create ICS event
                cal = Calendar()
                event = ICSEvent()
                event.name = description
                event.begin = suggested_datetime
                event.end = suggested_datetime + duration_delta
                cal.events.add(event)
                
                # Save ICS file
                with open('event.ics', 'w') as f:
                    f.write(str(cal))
                
                # Add to Google Calendar
                if 'credentials' in session:
                    credentials = Credentials(**session['credentials'])
                    service = build('calendar', 'v3', credentials=credentials)
                    event = {
                        'summary': description,
                        'start': {'dateTime': suggested_datetime.isoformat(), 'timeZone': 'UTC'},
                        'end': {'dateTime': (suggested_datetime + duration_delta).isoformat(), 'timeZone': 'UTC'},
                    }
                    service.events().insert(calendarId='primary', body=event).execute()
                
                return render_template('ai_schedule.html', 
                                       suggestion=f"Suggested time: {suggested_datetime.strftime('%d/%m/%y %H:%M')}, Duration: {duration} {duration_unit}s", 
                                       ics_created=True, 
                                       calendar_added=True)
            else:
                return render_template('ai_schedule.html', suggestion=suggestion, error="Couldn't parse the suggested time or duration.")
        except Exception as e:
            print(f"Error: {str(e)}")
            return render_template('ai_schedule.html', error="An error occurred. Please try again.")
    return render_template('ai_schedule.html')

@app.route('/manual_schedule', methods=['GET', 'POST'])
def manual_schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time'])
        new_event = Event(user_id=session['user_id'], title=title, start_time=start_time, end_time=end_time)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('manual_schedule.html')

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('homepage'))

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
