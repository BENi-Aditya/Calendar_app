<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendar App Project</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        header {
            background-color: #5C6BC0;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
        header img {
            max-width: 100%;
            height: auto;
        }
        h1, h2 {
            color: #333;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        h2 {
            font-size: 1.8rem;
            margin-top: 2rem;
        }
        p {
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        .container {
            width: 90%;
            margin: 2rem auto;
            background-color: #fff;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .code-block {
            background-color: #f9f9f9;
            padding: 1rem;
            border-left: 4px solid #5C6BC0;
            font-family: 'Courier New', Courier, monospace;
            overflow-x: auto;
        }
        footer {
            background-color: #5C6BC0;
            color: #fff;
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
        }
    </style>
</head>
<body>

<header>
    <h1>Calendar App</h1>
    <img src="Algorithm/AlgorithMermaid Sept 28 (1).png" alt="Algorithm Diagram">
</header>

<div class="container">
    <section>
        <h2>About the App</h2>
        <p>
            The Calendar App is a smart scheduling application that helps you organize your events effortlessly. It leverages AI-powered features to automatically suggest the best time for your event based on your preferences and other constraints. 
        </p>
        <p>
            Whether you're planning a meeting, an appointment, or a personal event, this app ensures that all events are properly scheduled with accurate start times and durations. The app interacts with APIs to receive suggestions and handles all the backend logic required to create calendar events.
        </p>
    </section>

    <section>
        <h2>Features</h2>
        <ul>
            <li>Automatic time allocation based on event preferences</li>
            <li>Duration suggestions for each event</li>
            <li>Integration with external APIs for smart scheduling</li>
            <li>User-friendly interface for manual time inputs</li>
            <li>Error handling and robust response parsing</li>
        </ul>
    </section>

    <section>
        <h2>Installation</h2>
        <p>To install and run the Calendar App, follow these steps:</p>
        <div class="code-block">
            <pre>
1. Clone the repository:
   <code>git clone https://github.com/yourusername/CalendarApp.git</code>

2. Navigate to the project directory:
   <code>cd CalendarApp</code>

3. Create a virtual environment:
   <code>python3 -m venv venv</code>

4. Activate the virtual environment:
   - For macOS/Linux: <code>source venv/bin/activate</code>
   - For Windows: <code>venv\Scripts\activate</code>

5. Install the required dependencies:
   <code>pip install -r requirements.txt</code>

6. Run the application:
   <code>python save.py</code>
            </pre>
        </div>
    </section>

    <section>
        <h2>Usage</h2>
        <p>To use the Calendar App:</p>
        <ol>
            <li>Run the app by executing <code>python save.py</code>.</li>
            <li>Input the event name when prompted.</li>
            <li>Select whether you want automatic time allocation (<code>yes</code>/<code>no</code>).</li>
            <li>For automatic allocation, the app will suggest start times and durations based on external API recommendations.</li>
            <li>For manual allocation, you will be prompted to enter the start time and duration manually.</li>
        </ol>
    </section>

    <section>
        <h2>API Integration</h2>
        <p>
            The app interacts with external APIs to suggest the optimal start time and duration for events. It uses AI-based decision-making to recommend times that best fit your schedule. The API response is parsed and automatically added to your event details.
        </p>
    </section>

    <section>
        <h2>License</h2>
        <p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
    </section>
</div>

<footer>
    <p>Created by <strong>Your Name</strong>. View the project on <a href="https://github.com/BENi-Aditya/Calender_app" style="color: #fff;">GitHub</a>.</p>
</footer>

</body>
</html>
