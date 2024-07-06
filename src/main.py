import os
import time
from bs4 import BeautifulSoup
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from typing import Final
import re
from datetime import datetime, timedelta

############## Remove comment if you deploy the app into a platform that might run multiple instance ##############
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
############## Remove comment if you deploy the app into a platform that might run multiple instance ##############

#### Unchanged variables #### 
TOKEN: Final = "ENTER_YOUR_TOKEN"
div_class: Final = 'ENTER DIV NAME TO KEEP THE TRACK ON IF IT GOT REMOVED'

# You can easily add a link below and a name of the URL that will be send to telegram if the url changed.
# Note: you must add the url and nameURL in order.
urls: Final = [
    'https://www.examble.com/'
]
nameURL: Final = [
    'Enter the name of the tracker in order of the url above'
]

currentTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
product = []
tasks = {}

file_name = 'status.txt'
file_found = 'founded.txt'
#### Unchanged variables #### 

for i, url in enumerate(urls):
    tempProduct = f"{urls[i]} {nameURL[i]} {currentTime} init"
    product.append(tempProduct)



# Def is responsable for:
# - loop url: Initialize all tracker thread for each URL.
# - Logs: each tracker and print it in terminal to identify in case one of the thread acts unusual.
# - Monitor: thread to monitor all threads in case it fail, it will reinit the thread to keep it alive.
async def init_tasks(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None):
    for index, url in enumerate(urls):
        tasks[url] = asyncio.create_task(finder(url, index, update, context))
    tasks['logs'] = asyncio.create_task(logs())
    tasks['monitor'] = asyncio.create_task(monitor_threads(update, context))
    if update:
        await update.message.reply_text("All tasks initialized.")

# Finder def is a infinite loop that monitor the site if got change and sleep in certian time based on the result.
# Responsable for the following:
# - Send an http request to the url given in "searchURL" def and it will return a boolean:
#   - True  = div found.
#       - Thread will sleep for 30 sec.
#   - False = div not found.
#       - Notify the users in Telegram.
#       - Start "afterFinding" def in order to notify the user in case the URL changed back.
#       - Sleep for 600 sec.
#   - None  = HTTP request failed
async def finder(url, index, update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        print(f"Finding... {url}")
        currTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        dummy = await searchURL(url)
        print(index, url, dummy)
        if dummy == True:
            changeContext(index, f"{url} \t\t {currTime} Not Found")
            await asyncio.sleep(30)
        elif dummy == False:
            if update:
                await update.message.reply_text(f'Product found:  {nameURL[index]} \n {url}')
            changeContext(index,  f"{url} \t\t {currTime} Found")
            await writeFounded(f'Product found:  {nameURL[index]}:  {url}')
            await asyncio.sleep(30)
            asyncio.create_task(finderAfter(url, index, update, context))
            await asyncio.sleep(600)

# Notify the user in case the URL changed back.
async def finderAfter(url, index, update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        print(f"[AFTER] Finding... ", url)
        dummy = await searchURL(url)
        print("--------", index, url, dummy)
        if dummy:
            if update:
                await update.message.reply_text(f'❌❌❌ \n [Site changed back]  {nameURL[index]}')
                print(f'[OUT OF STOCK] Product:  {nameURL[index]}   {url}  {dummy}')
                return
        await asyncio.sleep(15)

# searchURL def is responsable to send a HTTP Request to the url and sent the result back to finder
async def searchURL(url):
    retries = 3
    delay = 2
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        div = soup.find('div', class_=div_class)
                        if div:
                            context = div.get_text(strip=True)
                            print(f' {url} - {context}')
                            return True
                        else:
                            print(f'[Found] {response.status} - {url}')
                            return False
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(delay)
        return None

# cchangeContext def used to log to the status.txt to make sure each thread is working find
def changeContext(index, text):
    product[index] = text
    with open(file_name, 'w', encoding='utf-8') as file:
        for p in product:
            file.write(f"{p}\n")

# statusBuilder def is called when the user request for current status of the app.
# The def will see each thread timing based on a status.txt file. 
# In case if there is a thread is broken it will build a string with the url and nameURL to notify the user which one is broken
async def statusBuilder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    counter = 0
    brokenThread = []
    fixerCounter = 0
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            while True:
                lines = file.readline()
                if len(lines) >= 2:
                    fixerCounter += 1
                    timestamp_pattern = r"\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}"
                    match = re.search(timestamp_pattern, lines)
                    timestamp_str = match.group(0)
                    timestamp_format = "%m/%d/%Y, %H:%M:%S"
                    provided_time = datetime.strptime(timestamp_str, timestamp_format)
                    current_time = datetime.now()
                    time_difference = current_time - provided_time
                    if(time_difference.total_seconds() < 30 or time_difference.total_seconds() < 600):
                        counter += 1
                    else: 
                        brokenThread.append(lines)
                else:
                    break
    except FileNotFoundError:
        return "Need to be fixed!!!"
    
    if(counter == 8):
        return "Tracking is working fine"
    else:
        tempStr = "These links are current unavailable in the tracking (Need to be restarted)\n"
        for i in brokenThread:
            url_pattern = re.compile(r'https?://[^\s]+')
            match = url_pattern.search(i)
            tempStr +=  nameURL[urls.index(match.group(0))] +" " +  match.group(0) + "\n"
        return tempStr
        
# Logs def to make sure that the code is working and each thread is working from terminal. 
async def logs():
    currLogs = []
    print("Logs is init!!!")
    await asyncio.sleep(20)
    while True:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                while True:
                    lines = file.readline()
                    if len(lines) >= 2:
                        currLogs.append(lines)
                    else:
                        break
        except FileNotFoundError:
            return "Need to be fixed!!!"
        
        print(f'[STARTLOGS]\n{currLogs}\n[END LOGS]')
        currLogs = []
        await asyncio.sleep(120)

# In case if one of the URL is change it will log to founded.txt with the time found.
async def writeFounded(content):
    try:
        with open(file_found, "a", encoding='utf-8') as file:
            current_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            file.write(current_time + " "+ content + "\n") 
            file.close() 
    except FileNotFoundError:
        return "Need to be fixed!!!"

# Monitor each thread if the thread is broken it will try to create new thread without human involve or needed to restart the app
async def monitor_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        for url, task in tasks.items():
            if task.done() or task.cancelled():
                print("----------------------FIXING: {url} ---------------------")
                print("---[Before]---", task)
                print(f'Task for {url} is not running. Restarting...')
                if(url == "logs"):
                    tasks[url] = asyncio.create_task(logs())
                else:
                    index = urls.index(url)
                    tasks[url] = asyncio.create_task(finder(url, index, update, context))
                    print("---[After]---", tasks[url])
        await asyncio.sleep(90)

# TELEGRAM COMMANDS 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Use /track to start tracking.')

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await init_tasks(update, context)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    statusBuilterStr = await statusBuilder(update, context)
    print(statusBuilterStr)
    await update.message.reply_text(statusBuilterStr)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Polling...")
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

