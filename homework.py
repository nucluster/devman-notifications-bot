import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (NotCorrectKey, NotCorrectResponseType, NoTokenError,
                        NotOkStatusCode)

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 300
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка собшения ботом."""
    try:
        logger.info(f'Бот пытается отправить сообщение: {message}')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Бот отправил сообщение')
    except telegram.error.TelegramError as error:
        logger.error(error)


def get_api_answer(current_timestamp: int):
    """Получения ответа от API Практимума."""
    timestamp = current_timestamp
    request_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        response = requests.get(**request_params)
    except Exception as err:
        logger.error(f'Ошибка при запросе к основному API Практикума: {err}')
    if response.status_code != HTTPStatus.OK:
        logger.error('Статус код отличен от 200')
        raise NotOkStatusCode(f'Not OK status code: {response.status_code}')
    response = response.json()
    return response


def check_response(response: dict) -> list:
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        logger.error('Ответ от API приходит не в виде словаря')
        raise NotCorrectResponseType('Not correct response type')
    try:
        homeworks = response['homeworks']
    except KeyError:
        logger.error('Некорректный ответ API Практикума')
        raise NotCorrectKey('Not correct key')
    if not isinstance(homeworks, list):
        logger.error('Нужный ответ от API приходит не в виде списка')
        raise NotCorrectResponseType('Not correct response type')
    return homeworks


def parse_status(homework: dict) -> str:
    """Парсинг статуса."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        logger.error('Нет необходимых ключей в словаре homework')
        raise NotCorrectKey('Not correct key')
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        logger.error('Пришел недокументированный статус домашней работы')
        raise NotCorrectKey('Not correct key')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверка наличия всех токенов."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    check = all(tokens.values())
    if not check:
        null_tokens = [k for k, v in tokens.items() if v is None]
        logger.critical(
            f'Отсутствуют обязательные переменные окружения : {null_tokens}'
        )
        return check
    logger.info('Токены успешно загружены')
    return check


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise NoTokenError('No tokens')
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.info(f'Инициализируем бота {bot}')
    except telegram.error.TelegramError as error:
        logger.error(error)
    current_timestamp = int(time.time())
    err_cnt = {}
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.debug('В ответе отсутствуют новые статусы')
                time.sleep(RETRY_PERIOD)
                continue
            homework = homeworks[0]
            status = parse_status(homework)
            send_message(bot=bot, message=status)
            current_timestamp = int(time.time())
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if not err_cnt.get(f'{error}'):
                err_cnt[f'{error}'] = 1
                send_message(bot=bot, message=message)
            else:
                err_cnt[f'{error}'] += 1
            logger.debug(f'Суммарные сбои в работе программы: {err_cnt}')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
