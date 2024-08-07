import asyncio
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

# Определяем состояния разговора
ASK_NAME, ASK_SURNAME, ASK_EMAIL, ASK_TIME = range(4)


# Функция обработчика команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Создание клавиатуры с кнопкой
    keyboard = [['Записатись на зустріч']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправка сообщения с клавиатурой
    await update.message.reply_text('Привіт!', reply_markup=reply_markup)
    return ConversationHandler.END



async def appointment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Будь-ласка, введіть ваше імя:',
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_NAME



async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Будь-ласка, введіть вашу фамілію:')
    return ASK_SURNAME



async def ask_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['surname'] = update.message.text
    await update.message.reply_text('Будь-ласка, введіть ваш e-mail:')
    return ASK_EMAIL



async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text


    keyboard = [
        ['11:00-13:30', '14:00-17:00', '17:00-19:00']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text('Виберіть проміжок часу о якій вам удобно подзвонити:', reply_markup=reply_markup)
    return ASK_TIME



async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    name = context.user_data['name']
    surname = context.user_data['surname']
    email = context.user_data['email']
    time = context.user_data['time']

    await update.message.reply_text(
        text=f'Дякую, {name} {surname}! Ви записані на зустріч.\nВаш e-mail: {email}\nЧас дзвінку: {time}',
        reply_markup=ReplyKeyboardRemove()
    )


    url = 'https://hook.eu2.make.com/lpl68r47bpl5to15jxmgv91a922uyg9a'


    data_file = {
        'first_name': name,
        'last_name': surname,
        'email': email,
        'time': time
    }


    try:
        response = requests.post(url, json=data_file)
        if response.status_code == 200:
            print('Дані успішно відправлені')
        else:
            print(f'Помилка відправки даних, статус-код: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Виникла помилка під час відправки даних: {e}')

    return ConversationHandler.END



async def main() -> None:

    app = ApplicationBuilder().token('6155476263:AAFyMG6DaokGWflvHHaUAKc0kAF6x0h4uWI').build()


    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex('^Записатись на зустріч$'), appointment)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
        },
        fallbacks=[CommandHandler('start', start)]
    )


    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)


    await app.initialize()
    await app.start()

    try:
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
