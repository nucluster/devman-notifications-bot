import logging
import time

from telegram import Bot, Update

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token='YOUR_BOT_TOKEN')


def check_status(update: Update):
    work_id = update.message.text
    logging.info('Checking status of work with ID %s', work_id)

    # Получить статус проверки работы
    status = bot.get_work_status(work_id)

    # Отправить сообщение пользователю с текущим статусом
    if status == 'pending':
        bot.send_message(chat_id=update.message.chat_id, text='Ваша работа ещё не проверена.')
    elif status == 'approved':
        bot.send_message(chat_id=update.message.chat_id, text='Ваша работа одобрена.')
    elif status == 'rejected':
        bot.send_message(chat_id=update.message.chat_id, text='Ваша работа отклонена.')


@bot.message_handler(commands=['start'])
def start(update: Update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет! Я бот, который проверяет статус проверки ваших работ преподавателем.')
    bot.send_message(chat_id=update.message.chat_id, text='Чтобы проверить статус проверки работы, отправьте мне её ID.')


@bot.message_handler(content_types=['text'])
def handle_message(update: Update):
    check_status(update)


while True:
    updates = bot.get_updates(timeout=20)
    for update in updates:
        handle_message(update)
