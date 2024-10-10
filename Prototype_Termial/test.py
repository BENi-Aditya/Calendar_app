from datetime import datetime
from ics import Calendar, Event

c = Calendar()
e = Event()

e.summary = "Take your morning medication"
e.description = "Hello world"
e.begin = datetime.fromisoformat("2024-09-28T12:00:00+05:30")
e.end = datetime.fromisoformat("2024-09-28T13:00:00+05:30")
c.events.add(e)

with open("test.ics","w") as f:
    f.write(c.serialize())