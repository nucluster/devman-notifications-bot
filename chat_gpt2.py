from telegram.ext import Updater, CommandHandler
import requests


# Ваш токен бота
TOKEN = 'YOUR_BOT_TOKEN'
# URL эндпоинта long polling
LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


def start(update, context):
    update.message.reply_text('Привет! Я бот, готовый к долгому опросу сервера.')


def handle_updates(data, context):
    status = data.get("status")

    if status == "found":
        new_attempts = data.get("new_attempts", [])
        last_attempt_timestamp = data.get("last_attempt_timestamp")

        # Обработка новых попыток или других данных по мере необходимости.
        context.bot.send_message(chat_id=update.message.chat_id, text=f"New attempts: {new_attempts}")
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Last attempt timestamp: {last_attempt_timestamp}")

    elif status == "timeout":
        timestamp_to_request = data.get("timestamp_to_request")
        # Обработка ситуации, когда больше нет свежих работ.
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Timeout. Timestamp to request: {timestamp_to_request}")

    # Другие возможные статусы могут быть добавлены в логику обработки.


def long_polling_example(context):
    while True:
        try:
            response = requests.get(LONG_POLLING_URL)
            response.raise_for_status()

            data = response.json()
            handle_updates(data, context)

        except requests.exceptions.RequestException as e:
            print(f"Error during long polling: {e}")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()

    # Запуск long polling в отдельном потоке
    updater.job_queue.run_repeating(long_polling_example, interval=60, first=0)

    updater.idle()


if __name__ == '__main__':
    main()
