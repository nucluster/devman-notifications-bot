from time import time, sleep
import logging
import os
import sys

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

DEVMAN_TOKEN = os.getenv("DEVMAN_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {"Authorization": f"Token {DEVMAN_TOKEN}"}
url = "https://dvmn.org/api/long_polling/"
params = {
    "timestamp": time()
}
timeout = 120


def send_message(msg: str) -> None:
    """Отправка сообщения ботом."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.info(f"Инициализируем бота {bot}")
        logger.info(f"Бот пытается отправить сообщение: {msg}")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        logger.debug("Бот отправил сообщение")
    except telegram.error.TelegramError as error:
        logger.error(error)


if __name__ == "__main__":
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            status = data.get("status")
            if status == "timeout":
                params["timestamp"] = data.get("timestamp_to_request")
                logger.debug("В ответе отсутствуют новые статусы")
            elif status == "found":
                new_attempts = data["new_attempts"][0]
                lesson_title = new_attempts['lesson_title']
                lesson_url = new_attempts['lesson_url']
                message = f'Работа "{lesson_title}" проверена.\n\n'
                if new_attempts["is_negative"]:
                    message += f'Есть замечания. {lesson_url}'
                else:
                    message += f'Замечаний нет. Работа принята.'
                send_message(message)
                params["timestamp"] = data.get("last_attempt_timestamp")
        except requests.exceptions.HTTPError as err:
            logger.error(f"Ошибка в процессе выполнения запроса: {err}")
            sleep(5)
            continue
        except requests.exceptions.ReadTimeout as err:
            logger.error(f"Ошибка таймаута")
            sleep(5)
            continue
        except requests.exceptions.ConnectionError as err:
            logger.error(f"Ошибка в процессе соединения с сервером: {err}")
            sleep(5)
            continue
