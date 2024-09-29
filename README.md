<!-- README.md -->

<h1 align="center" style="color: #4CAF50;">Calendar App</h1>

<p align="center" style="font-size: 1.2em;">Ever feel like adding events to your calendar is just another chore? Whether it's scheduling lectures, study sessions, or practice, it can be a headache trying to fit everything in without conflicts.

The **Smart Calendar App** fixes that. It automates the process, adding events and intelligently allocating time based on your schedule. No more juggling or guessing—just let the app handle it. It’s like having a personal assistant for your day!</p>

---

<div align="center">
    <img src="Algorithm/AlgorithMermaid Sept 28 (1).png" alt="Flowchart Algorithm" style="width:80%;">
</div>

---

<h2 style="color: #f39c12;">Tech Stack</h2>
<ul style="font-size: 1.1em;">
    <li><strong>Python</strong> - Core logic for event handling</li>
    <li><strong>Flask</strong> - Web framework</li>
    <li><strong>Google Calendar API</strong> - For calendar event integration</li>
    <li><strong>OpenAI API</strong> - AI-powered suggestions for event timing</li>
</ul>

---

<h2 style="color: #f39c12;">How to Run</h2>

1. **Clone the repository:**

    ```sh
    git clone https://github.com/BENi-Aditya/Calendar_app.git
    ```

2. **Navigate to the project directory:**

    ```sh
    cd Calendar_app
    ```

3. **Create and activate a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # For Windows use `venv\Scripts\activate`
    ```

4. **Install the required libraries:**

    ```sh
    pip install -r requirements.txt
    ```

5. **Create a `.env` file in the project root and add your API keys:**

    ```sh
    touch .env
    ```

6. **Add the following to your `.env` file:**

    ```sh
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key
    ```

7. **Run the application:**

    ```sh
    python save.py
    ```

8. **Follow the prompt to enter the event name and select whether to auto-allocate event time.**

---

<h2 style="color: #f39c12;">Usage</h2>

<ul style="font-size: 1.1em;">
    <li>Enter the event name when prompted.</li>
    <li>Select whether to enable automatic time allocation using AI suggestions.</li>
    <li>The app will suggest the best time for the event based on your calendar availability.</li>
    <li>Check your Google Calendar to see the event with its correct duration and allocated time.</li>
</ul>

---

<h2 style="color: #f39c12;">Features</h2>

<ul style="font-size: 1.1em;">
    <li>Automated event time suggestions based on calendar availability using OpenAI API.</li>
    <li>Seamless integration with Google Calendar to create and manage events.</li>
    <li>Automatic detection of overlapping events to prevent scheduling conflicts.</li>
    <li>Supports both manual and automatic time allocation modes for flexibility.</li>
</ul>

---

<h2 style="color: #f39c12;">Need for the Idea</h2>
<p style="font-size: 1.1em;">
    In today's fast-paced world, managing time efficiently is essential. Our Calendar App is designed to automate the process of finding the perfect event time based on your availability and preferences, reducing the hassle of manually checking for free slots and preventing schedule conflicts. With AI-assisted suggestions, it ensures that your events are intelligently allocated, saving time and effort.
</p>

---

<h2 style="color: #f39c12;">Contributions</h2>
<p style="font-size: 1.1em;">
    We welcome contributions from the community to improve this project! Feel free to fork the repository, make your changes, and submit a pull request. Please ensure your contributions align with the project's goals and adhere to our coding standards.
</p>

<p style="font-size: 1.1em;">Here's how you can contribute:</p>
<ul style="font-size: 1.1em;">
    <li>Fork the repository: <a href="https://github.com/BENi-Aditya/Calendar_app">https://github.com/BENi-Aditya/Calendar_app</a></li>
    <li>Create a new branch: <code>git checkout -b feature-branch-name</code></li>
    <li>Make your changes and commit them: <code>git commit -m 'Description of your changes'</code></li>
    <li>Push to the branch: <code>git push origin feature-branch-name</code></li>
    <li>Submit a pull request</li>
</ul>

---

<p align="center" style="font-size: 1.2em;">Built with ❤️ by <strong><a href="https://github.com/BENi-Aditya">BENi-Aditya</a></strong></p>
