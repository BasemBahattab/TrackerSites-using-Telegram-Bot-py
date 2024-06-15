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

# This is a standard variable that will be used in the app
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

for i, url in enumerate(urls):
    tempProduct = f"{urls[i]} {nameURL[i]} {currentTime} init"
    product.append(tempProduct)

file_name = 'status.txt'
file_found = 'founded.txt'

# Def is responsable to initialize all the thread for each URL to track and init initialize.
async def init_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = [finder(url, index, update, context) for index, url in enumerate(urls)]
    tasks.append(logs())
    tasks.append(monitor_threads(update, context))
    await asyncio.gather(*tasks)
    print("All tasks initialized.")
    await update.message.reply_text("All tasks initialized.")

# Finder def is a infinite loop that monitor the site if got change.
async def finder(url, index, update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        print(f"Finding... {url}")
        currTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        dummy = await searchURL(url)
        print(index, url, dummy)
        if dummy:
            changeContext(index, f"{url} {nameURL[index]} {currTime} Not Found")
            await asyncio.sleep(30)
        else:
            await update.message.reply_text(f'Product found:  {nameURL[index]} \n {url}')
            changeContext(index,  f"{url} {nameURL[index]} {currTime} Found")
            await writeFounded(f'Product found:  {nameURL[index]}:  {url}')
            await asyncio.sleep(600)

# searchURL def is responsable to send a HTTP Request to the url and sent the result back to finder
async def searchURL(url):
    await asyncio.sleep(5)
    response = requests.get(url)
    found = True
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find('div', class_=div_class)
        if div:
            context = div.get_text(strip=True)
            print(context)
        else:
            found = False
            print("Div not found.")
    else:
        print("Failed to retrieve URL:", response.status_code)
    return found

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
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            while True:
                lines = file.readline()
                if len(lines) >= 2:
                    print("[logs file]: " + lines)
                else:
                    await asyncio.sleep(30)
                
    except FileNotFoundError:
        return "Need to be fixed!!!"

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
        statusBuilterStr = await statusBuilder(update, context)
        print(statusBuilterStr)
        if "Need to be restarted" in statusBuilterStr:
            for line in statusBuilterStr.split('\n')[1:]:
                if line:
                    url = line.split()[-1]
                    index = urls.index(url)
                    # asyncio.create_task(finder(urls[index], index, update, context))
        await asyncio.sleep(60)

# TELEGRAM COMMANDS 
async def fixBrokenThreads(index, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.gather(finder(urls[index], index, update, context))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Use /track to start tracking.')

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    asyncio.create_task(init_tasks(update, context))

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    statusBuilterStr = await statusBuilder(update, context)
    print(statusBuilterStr)
    await update.message.reply_text(statusBuilterStr)

# Handle user messages from telegram.
# You can use this based on user input.
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # In case if you want to add more commands you need to add the handler below
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("status", status))

    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Polling...")
    application.run_polling()

if __name__ == '__main__':
    checkIfThereIsInstance()
    asyncio.run(main())
