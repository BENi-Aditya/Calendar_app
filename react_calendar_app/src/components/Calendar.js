import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css'; // Import the CSS

const localizer = momentLocalizer(moment); // Set the localizer

const MyCalendar = () => {
    const [events, setEvents] = useState([]); // State to hold events

    useEffect(() => {
        // Sample events
        const sampleEvents = [
            {
                start: new Date(),
                end: new Date(moment().add(1, 'hours')),
                title: "Sample Event",
            },
        ];
        setEvents(sampleEvents);
    }, []);

    const handleSelectSlot = (slotInfo) => {
        const title = window.prompt('New Event name');
        if (title) {
            setEvents((prevEvents) => [
                ...prevEvents,
                {
                    start: slotInfo.start,
                    end: slotInfo.end,
                    title,
                },
            ]);
        }
    };

    return (
        <div>
            <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                style={{ height: 500, margin: "50px" }}
                selectable
                onSelectSlot={handleSelectSlot} // Handle slot selection
            />
        </div>
    );
};

export default MyCalendar;
