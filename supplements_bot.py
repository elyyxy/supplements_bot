#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import datetime
import pytz
import random

# === График добавок ===
week_1_schedule = {
    "08:00": ["(๑•̀ㅂ•́)و✧ Сорбифер + Витамин C (после завтрака)", "(≧◡≦) Омега-3 (утро)"],
    "18:00": ["(≧◡≦) Омега-3 (вечер)"],  # первая неделя сорбифер только утром
    "23:00": ["(*≧ω≦) 5-HTP перед сном", "(=^-ω-^=) Мелатонин перед сном"]
}

week_later_schedule = {
    "08:00": ["(๑•̀ㅂ•́)و✧ Сорбифер + Витамин C (после завтрака)", "(≧◡≦) Омега-3 (утро)"],
    "18:00": ["(｡♥‿♥｡) Сорбифер + Витамин C (после ужина)", "(≧◡≦) Омега-3 (вечер)"],
    "23:00": ["(*≧ω≦) 5-HTP перед сном", "(=^-ω-^=) Мелатонин перед сном"]
}

taken_today = {}
current_week = 1  # первая неделя, потом 2 и далее одинаково

motivational_phrases = [
    "Ты молодец! (^‿^)", 
    "Продолжай в том же духе! (≧◡≦)", 
    "Не забывай про своё здоровье! (*≧ω≦)", 
    "Умница! (｡♥‿♥｡)"
]

# === Команды бота ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Статус", callback_data="status")],
        [InlineKeyboardButton("Следующее", callback_data="next")],
        [InlineKeyboardButton("Мотивируй", callback_data="motivate")],
        [InlineKeyboardButton("Напоминание", callback_data="reminder")],
        [InlineKeyboardButton("Сброс", callback_data="reset")],
        [InlineKeyboardButton("Неделя", callback_data="week")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! (≧◡≦) Я твой милый бот-напоминалка по добавкам! (✿◠‿◠)\n"
        "Выбирай действие в меню ниже ⬇️",
        reply_markup=reply_markup
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data["chat_id"]
    now = datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M")
    schedule = week_1_schedule if current_week == 1 else week_later_schedule

    if now == "08:00":
        await context.bot.send_message(chat_id=chat_id, text="おはようございます! (≧◡≦) Доброе утро! ☀️")
    if now == "23:00":
        await context.bot.send_message(chat_id=chat_id, text="おやすみなさい! (*≧ω≦) Спокойной ночи! 🌙")

    if now in schedule:
        for supplement in schedule[now]:
            keyboard = [[InlineKeyboardButton("✅ Принято", callback_data=supplement)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Напоминание: {supplement} (≧ω≦)\nТы приняла?",
                                           reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    schedule = week_1_schedule if current_week == 1 else week_later_schedule

    if data == "status":
        message = "Статус на сегодня 📝:\n"
        for time, supplements in schedule.items():
            for s in supplements:
                status = "✅" if taken_today.get(s) else "❌"
                message += f"{s}: {status}\n"
        await query.edit_message_text(message)
    elif data == "next":
        now = datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M")
        upcoming = [(t, s) for t, supplements in schedule.items() for s in supplements if t > now]
        if upcoming:
            t, s = upcoming[0]
            await query.edit_message_text(f"Скоро: {s} в {t} (๑•̀ㅂ•́)و✧")
        else:
            await query.edit_message_text("Ближайших добавок больше нет сегодня! (*≧ω≦)")
    elif data == "motivate":
        phrase = random.choice(motivational_phrases)
        await query.edit_message_text(phrase)
    elif data == "reset":
        global taken_today
        taken_today = {}
        await query.edit_message_text("Отметки сброшены для нового дня! (≧◡≦)")
    elif data == "week":
        await query.edit_message_text(f"Сейчас неделя: {current_week}")
    elif data == "help":
        help_text = (
            "/start — приветствие\n"
            "/status — статус добавок\n"
            "/next — ближайшее добавление\n"
            "/motivate — мотивирующая фраза\n"
            "/reset — сбросить отметки за день\n"
            "/week — какая сейчас неделя\n"
        )
        await query.edit_message_text(help_text)
    else:
        # Если нажата кнопка "✅ Принято" или любое другое
        taken_today[data] = True
        await query.edit_message_text(text=f"{data} — ✅ Принято (*^‿^*)\nХорошая работа! (≧◡≦)")

# Сообщения, которые бот не понимает
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ой-ёй-ёй, ничего не понимаю! (｡>﹏<｡)")

# Сброс отметок каждый день
async def reset_marks(context: ContextTypes.DEFAULT_TYPE):
    global taken_today
    taken_today = {}
    print("Отметки сброшены для нового дня (≧◡≦)")

# === Запуск бота ===
def main():
    TOKEN = "8300638506:AAH1_yFgQ6EAlEkYu5_f3gV37V-l6o2407M"
    CHAT_ID = 447074125  # твой chat_id

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), unknown_message))

    # JobQueue для напоминаний каждую минуту
    app.job_queue.run_repeating(send_reminder, interval=60, first=0, data={"chat_id": CHAT_ID})
    # Сброс отметок каждый день
    app.job_queue.run_daily(reset_marks, time=datetime.time(hour=0, minute=1, tzinfo=pytz.timezone("Europe/Moscow")))

    app.run_polling()

if __name__ == "__main__":
    main()

