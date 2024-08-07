import asyncio
import os

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

# tokens
BOT_API_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('URL')

ASK_NAME, ASK_SURNAME, ASK_EMAIL, ASK_TIME = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Создание клавиатуры с кнопкой (Creating keys with a key)
    keyboard = [['Записатись на зустріч']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправка сообщения с клавиатурой (Sending a message with the keyboard)
    await update.message.reply_text('Привіт!', reply_markup=reply_markup)
    return ConversationHandler.END


async def handle_appointment_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Будь-ласка, введіть ваше імя:',
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_NAME


async def handle_ask_name_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Будь-ласка, введіть вашу фамілію:')
    return ASK_SURNAME


async def handle_ask_surname_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['surname'] = update.message.text
    await update.message.reply_text('Будь-ласка, введіть ваш e-mail:')
    return ASK_EMAIL


async def handle_ask_email_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text

    keyboard = [
        ['11:00-13:30', '14:00-17:00', '17:00-19:00']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text('Виберіть проміжок часу о якій вам удобно подзвонити:', reply_markup=reply_markup)
    return ASK_TIME


async def handle_ask_time_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    name = context.user_data['name']
    surname = context.user_data['surname']
    email = context.user_data['email']
    time = context.user_data['time']

    data_file = {
        'first_name': name,
        'last_name': surname,
        'email': email,
        'time': time
    }

    try:
        response = requests.post(WEBHOOK_URL, json=data_file)
        if response.status_code == 200:
            print('Дані успішно відправлені')
            await update.message.reply_text(
                text='Дякую, %(name)s %(surname)s! Ви записані на зустріч.\nВаш e-mail: %(email)s\nЧас дзвінку: %(time)s' % {
                    'name': name,
                    'surname': surname,
                    'email': email,
                    'time': time
                },
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            print(f'Помилка відправки даних, статус-код: {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Виникла помилка під час відправки даних: {e}')
        await update.message.reply_text(
            text=f'Під час відправки даних виникла помилка, спробуйте ще раз.',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def main() -> None:
    app = ApplicationBuilder().token(BOT_API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex('^Записатись на зустріч$'), handle_appointment_message)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ask_name_message)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ask_surname_message)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ask_email_message)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ask_time_message)],
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
