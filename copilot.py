import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я бот, который проверяет статус проверки работы преподавателем с помощью long polling.")


def check_status(update, context):
    # здесь должен быть код для проверки статуса проверки работы преподавателем
    context.bot.send_message(chat_id=update.effective_chat.id, text="Статус проверки работы преподавателем: OK")


def main():
    updater = Updater(token='YOUR_TOKEN', use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('check_status', check_status))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
