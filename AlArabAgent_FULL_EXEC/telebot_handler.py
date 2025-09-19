
import telebot

API_TOKEN = "8299239489:AAEl4Kh05_wxWEAGdm2Ji3Qy8GVLMr4vkdg"
CHAT_ID = "931702670"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 النظام مفعّل بالكامل، يا عرّاب.")

def start_bot():
    import threading
    threading.Thread(target=bot.polling, daemon=True).start()
