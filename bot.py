import logging
import os
import sys
from time import sleep, time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

url = "https://dvmn.org/api/long_polling/"
params = {"timestamp": time()}
timeout = 120


def main():
    while True:
        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            check = response.json()
            status = check.get("status")
            if status == "timeout":
                params["timestamp"] = check.get("timestamp_to_request")
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
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                except telegram.error.TelegramError as error:
                    logger.error(error)
                logger.debug("Бот отправил сообщение")

            params["timestamp"] = check.get("last_attempt_timestamp")
        except requests.exceptions.HTTPError as err:
            msg = f"Ошибка в процессе выполнения запроса: {err}"
            logger.error(msg)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, message=msg)
            sleep(5)
            continue
        except requests.exceptions.ReadTimeout as err:
            msg = f"Ошибка таймаута {err}"
            logger.error(msg)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            continue
        except requests.exceptions.ConnectionError as err:
            msg = f"Ошибка в процессе соединения с сервером: {err}"
            logger.error(msg)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            sleep(5)
            continue


if __name__ == "__main__":
    load_dotenv()
    DEVMAN_TOKEN = os.getenv("DEVMAN_TOKEN")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    headers = {"Authorization": f"Token {DEVMAN_TOKEN}"}
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
