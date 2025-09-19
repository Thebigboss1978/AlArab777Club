
import os
import time
import telebot_handler as tele

COMMAND_FOLDER = "command_queue"

def execute_command(command):
    result = f"✅ تم تنفيذ الأمر: {command}"
    tele.bot.send_message(tele.CHAT_ID, result)

def monitor_and_execute():
    os.makedirs(COMMAND_FOLDER, exist_ok=True)
    processed = set()
    while True:
        files = os.listdir(COMMAND_FOLDER)
        for file in files:
            if file.endswith(".txt") and file not in processed:
                with open(os.path.join(COMMAND_FOLDER, file), "r", encoding="utf-8") as f:
                    command = f.read().strip()
                execute_command(command)
                processed.add(file)
        time.sleep(5)
