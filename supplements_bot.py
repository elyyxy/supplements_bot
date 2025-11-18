#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime
import pytz
import random

# ===============================
# График добавок с каомодзи
week_1_schedule = {
    "08:00": ["(๑•̀ㅂ•́)و✧ Сорбифер + Витамин C (после завтрака)", "(≧◡≦) Омега-3 (утро)"],
    "18:00": ["(≧◡≦) Омега-3 (вечер)"],
    "23:00": ["(*≧ω≦) 5-HTP перед сном", "(=^-ω-^=) Мелатонин перед сном"]
}

week_2_schedule = {
    "08:00": ["(๑•̀ㅂ•́)و✧ Сорбифер + Витамин C (после завтрака)", "(≧◡≦) Омега-3 (утро)"],
    "18:00": ["(｡♥‿♥｡) Сорбифер + Витамин C (после ужина)", "(≧◡≦) Омега-3 (вечер)"],
    "23:00": ["(*≧ω≦) 5-HTP перед сном", "(=^-ω-^=) Мелатонин перед сном"]
}

# ===============================
# Картинки и гифки котиков
morning_cats = [
    "https://i.imgur.com/9Qy7r8X.jpeg",
    "https://i.imgur.com/FvP8pVz.jpeg"
]

night_cats = [
    "https://i.imgur.com/nt0JvXh.jpeg",
    "https://i.imgur.com/hN2vQ2x.jpeg"
]

supplement_gifs = [
    "https://i.imgur.com/vZQ2TnX.gif",
    "https://i.imgur.com/UqVVS2Q.gif"
]

# ===============================
taken_today = {}
bot_start_date = datetime.datetime.now(pytz.timezone("Europe/Moscow")).date()  # день запуска бота

# ===============================
# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! (≧◡≦) Я твой милый бот-напоминалка по добавкам! (✿◠‿◠)\n"
        "Я буду присылать уведомления, и ты сможешь отмечать ✅, что приняла."
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data["chat_id"]
    now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    time_str = now.strftime("%H:%M")
    
    # Определяем неделю
    days_passed = (now.date() - bot_start_date).days
    current_week = 1 if days_passed < 7 else 2
    schedule_dict = week_1_schedule if current_week == 1 else week_2_schedule

    # Доброе утро
    if time_str == "08:00":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=random.choice(morning_cats),
            caption="おはようございます! (≧◡≦) Доброе утро! ☀️\nНе забудь свои добавки!"
        )
    # Спокойной ночи
    if time_str == "23:00":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=random.choice(night_cats),
            caption="おやすみなさい! (*≧ω≦) Спокойной ночи! 🌙\nПора 5-HTP и Мелатонин"
        )

    # Напоминания по добавкам
    if time_str in schedule_dict:
        for supplement in schedule_dict[time_str]:
            keyboard = [[InlineKeyboardButton("✅ Принято", callback_data=supplement)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            gif = random.choice(supplement_gifs)
            await context.bot.send_animation(chat_id=chat_id, animation=gif)
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Напоминание: {supplement} (≧ω≦)",
                                           reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    supplement = query.data
    taken_today[supplement] = True
    await query.edit_message_text(text=f"{supplement} — ✅ Принято (*^‿^*)")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    days_passed = (now.date() - bot_start_date).days
    current_week = 1 if days_passed < 7 else 2
    schedule_dict = week_1_schedule if current_week == 1 else week_2_schedule
    
    message = "Статус на сегодня 📝:\n"
    for time, supplements in schedule_dict.items():
        for s in supplements:
            status = "✅" if taken_today.get(s) else "❌"
            message += f"{s}: {status}\n"
    await update.message.reply_text(message)

async def reset_marks(context: ContextTypes.DEFAULT_TYPE):
    global taken_today
    taken_today = {}
    print("Отметки сброшены для нового дня (≧◡≦)")

# ===============================
# Запуск бота
def main():
    TOKEN = "8300638506:AAH1_yFgQ6EAlEkYu5_f3gV37V-l6o2407M"
    CHAT_ID = 447074125

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button))

    # JobQueue для напоминаний каждую минуту
    app.job_queue.run_repeating(send_reminder, interval=60, first=0, data={"chat_id": CHAT_ID})
    # Сброс отметок каждый день в 00:01
    app.job_queue.run_daily(reset_marks, time=datetime.time(hour=0, minute=1, tzinfo=pytz.timezone("Europe/Moscow")))

    print("Бот запущен ❤️")
    app.run_polling()

if __name__ == "__main__":
    main()

