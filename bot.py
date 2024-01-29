import logging
import os
import sys
from time import sleep, time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

URL = "https://dvmn.org/api/long_polling/"
PARAMS = {"timestamp": time()}
TIMEOUT = 120


def main():
    load_dotenv()
    devman_token = os.getenv("DEVMAN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    headers = {"Authorization": f"Token {devman_token}"}
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    bot = telegram.Bot(token=telegram_token)
    logger.info(f"Инициализируем бота {bot}")
    while True:
        try:
            response = requests.get(
                URL, headers=headers, params=PARAMS, timeout=TIMEOUT)
            response.raise_for_status()
            check = response.json()
            status = check.get("status")
            if status == "timeout":
                PARAMS["timestamp"] = check.get("timestamp_to_request")
                logger.debug("В ответе отсутствуют новые статусы")
            elif status == "found":
                new_attempt = check["new_attempts"][0]
                lesson_title = new_attempt['lesson_title']
                lesson_url = new_attempt['lesson_url']
                message = f'Работа "{lesson_title}" проверена.\n\n'
                if new_attempt["is_negative"]:
                    message += f'Есть замечания. {lesson_url}'
                else:
                    message += 'Замечаний нет. Работа принята.'
                logger.info(f"Бот пытается отправить сообщение: {message}")
                try:
                    bot.send_message(chat_id=telegram_chat_id, text=message)
                except telegram.error.TelegramError as error:
                    logger.error(error)
                logger.debug("Бот отправил сообщение")
            PARAMS["timestamp"] = check.get("last_attempt_timestamp")
        except requests.exceptions.HTTPError as err:
            logger.error(f"Ошибка в процессе выполнения запроса: {err}")
            sleep(5)
            continue
        except requests.exceptions.ReadTimeout as err:
            logger.error(f"Ошибка таймаута {err}")
            continue
        except requests.exceptions.ConnectionError as err:
            logger.error(f"Ошибка в процессе соединения с сервером: {err}")
            sleep(5)
            continue


if __name__ == "__main__":
    main()
