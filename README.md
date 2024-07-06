# URL Monitor with Telegram Notifications

This script monitors specified URLs and checks for changes in specified HTML elements. When a change is detected, it sends a notification through a Telegram bot. The script is designed to run continuously and automatically restarts monitoring tasks if they fail.

## Requirements

- Python 3.7+
- Required Python packages: `aiohttp`, `beautifulsoup4`, `python-telegram-bot`
- Heroku for deployment (Procfile file included in src).
P.S. You can use other deployment frameworks, but they might not work. The last section `Comments for Deployment on Multi-Instance Platforms` in the README file might fix the issue.

## Installation

- Clone the repository.
- Install the required packages:
   ```bash
   pip install pip install -r /requirements.txt
    ```

## Configuration
- Replace ENTER_YOUR_TOKEN with your Telegram bot token.
- Replace ENTER DIV NAME TO KEEP THE TRACK ON IF IT GOT REMOVED with the class name of the HTML div you want to monitor.
- Add the URLs you want to monitor to the urls list.
- Add the corresponding names for the URLs to the nameURL list in the same order.

## Running the Script

To run the script, use: 
   ```bash
   python main.py
   ```

## Code Structure
### Initialization
The script initializes variables and creates tasks for each URL to monitor.

```bash
TOKEN: Final = "ENTER_YOUR_TOKEN"
div_class: Final = 'ENTER DIV NAME TO KEEP THE TRACK ON IF IT GOT REMOVED'
urls: Final = ['https://www.example.com/'] #You can add more than 1 URL, but make sure to add a name in nameURL array below.
nameURL: Final = ['Enter the name of the tracker in order of the url above']
```

### Functions
- init_tasks(): Initializes tasks for URL monitoring, logging, and thread monitoring.
- finder(): Monitors the URL and checks for changes.
- finderAfter(): Monitors the URL to check if the change is reverted.
- searchURL(): Sends HTTP requests and checks for the specified HTML div.
- changeContext(): Logs the current status of each thread.
- statusBuilder(): Builds a status report of the monitoring tasks.
- logs(): Logs the current status of monitoring tasks to the console.
- writeFounded(): Logs found changes to a file.
- monitor_threads(): Monitors tasks and restarts them if they fail.

### Telegram Commands
- /start: Sends a greeting message.
- /track: Starts the monitoring tasks.
- /status: Sends the current status of the monitoring tasks.

### Comments for Deployment on Multi-Instance Platforms
Uncomment the following section to ensure that the code runs only once, even if deployed on a platform with multiple instances:
This ensures that the backup code executes in case the app crashes.

```bash
# The following commands ensure that the code runs only once, even if deployed on a platform with multiple instances.
# This guarantees that the backup code executes in case the app crashes.

# file_init = "working.txt"
# def write_message(file_init):
#     with open(file_init, 'w') as file:
#         current_time = datetime.now().isoformat()
#         file.write(f"{current_time}\n")

# def read_message(file_init):
#     try:
#         with open(file_init, 'r') as file:
#             lines = file.readlines()
#             if len(lines) >= 1:
#                 timestamp = lines[0].strip()
#                 file_time = datetime.fromisoformat(timestamp)
#                 return file_time
#     except FileNotFoundError:
#         return None

# def checkIfThereIsInstance():
#     file_time = read_message(file_init)
#     while True:
#         current_time = datetime.now()
#         time_difference = current_time - file_time
#         if time_difference > timedelta(minutes=1):
#             print("Init App")
#             write_message(file_init)
#             return
#         else:
#             time_difference_str = str(time_difference)
#             temp  = current_time.strftime("%Y-%m-%d %H:%M:%S")
#             print("sleeping " + temp + " " + time_difference_str)
#             time.sleep(10)
```