
import os, subprocess, platform, logging, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))
COMMAND_FOLDER = "COMMANDS"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ غير مصرح.")
    await update.message.reply_text("🤖 جاهز يا عرّاب. النظام يعمل.")

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ هذا النظام مخصص للعرّاب فقط.")
    cmd = update.message.text
    logging.info(f"🔹 أمر مباشر من Telegram: {cmd}")
    await run_command(cmd, update)

async def run_command(command, update=None):
    try:
        shell = "/bin/bash" if platform.system() != "Windows" else None
        result = subprocess.run(command, shell=True, executable=shell, capture_output=True, text=True)
        output = result.stdout or result.stderr or "✅ تم التنفيذ بدون مخرجات."
        msg = f"📤 النتيجة:\n\n{output[:4000]}"
    except Exception as e:
        msg = f"❌ خطأ أثناء التنفيذ:\n{str(e)}"

    if update:
        await update.message.reply_text(msg)
    else:
        await send_message(msg)

async def send_message(text):
    try:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=ALLOWED_USER_ID, text=text)
    except Exception as e:
        logging.error(f"خطأ في إرسال رسالة: {e}")

async def watch_command_folder():
    processed = set()
    os.makedirs(COMMAND_FOLDER, exist_ok=True)
    logging.info(f"📂 يراقب المجلد: {COMMAND_FOLDER}")
    while True:
        for fname in os.listdir(COMMAND_FOLDER):
            fpath = os.path.join(COMMAND_FOLDER, fname)
            if fpath in processed:
                continue
            if os.path.isfile(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                logging.info(f"🧾 تنفيذ ملف: {fname}")
                await run_command(content)
                processed.add(fpath)
        await asyncio.sleep(10)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), execute))
    logging.info("🤖 AlArabAgent بدأ التنفيذ...")

    loop = asyncio.get_event_loop()
    loop.create_task(watch_command_folder())
    app.run_polling()

if __name__ == "__main__":
    main()
