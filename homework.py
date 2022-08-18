import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions
import settings

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)


def send_message(bot, message):
    """Sends the message to user."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('send_message succeed')
    except telegram.error.TelegramError as error:
        logging.error(f'Возникла ошибка {error}')


def get_api_answer(current_timestamp):
    """Makes a request to endpoint."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            settings.ENDPOINT,
            headers=settings.HEADERS,
            params=params
        )
    except Exception as error:
        message = 'Не можем получить ответ от API-сервиса.'
        logging.error(f'get_api_answer failed. {error}.')
        raise exceptions.StatusAPIError(message)

    if response.status_code != HTTPStatus.OK:
        message = f'Сервер не отвечает. Ошибка {response.status_code}.'
        logging.error('get_api_answer does not work')
        raise exceptions.StatusAPIError(message)
    try:
        logging.info('get_api_answer succeed')
        return response.json()
    except Exception as error:
        message = 'Неверный ответ сервера'
        logging.error(f'Wrong format returned from API. {error}')
        raise exceptions.ResponseFormatError(message)


def check_response(response):
    """Checks if the response is correct."""
    if not isinstance(response, dict):
        logging.error('response is not dict')
        raise TypeError('response is not dict')

    if 'homeworks' not in response:
        logging.error('check_response does not get "homeworks"')
        message = 'Домашняя работа не найдена'
        raise exceptions.NoHomeworkError(message)

    homework = response['homeworks']
    if not isinstance(homework, list):
        logging.error('homework is not a list')
        raise TypeError('homework is not a list')

    if not homework:
        logging.error('Список response домашних работ оказался пустым')
        message = 'У вас нет домашних работ'
        raise exceptions.NoHomeworkError

    logging.info('check_response succeed')
    return response['homeworks']


def parse_status(homework):
    """Gets status of exact homework."""
    if not isinstance(homework, dict):
        logging.error('В домашней работе передан не список')
        raise TypeError

    if 'homework_name' in homework.keys():
        homework_name = homework['homework_name']
        logging.info('homework_name in parse status succeed')
    else:
        raise KeyError('No homework_name')

    if 'status' in homework.keys():
        homework_status = homework['status']
        logging.info('homework_status in parse status succeed')
    else:
        raise KeyError('No homework_status')

    if homework_status not in settings.HOMEWORK_STATUSES:
        text = f'Нетипичный статус домашней работы {homework_status}'
        logging.error('parse_status failed')
        raise exceptions.WrongHomeworkStatusError(text)
    verdict = settings.HOMEWORK_STATUSES.get(homework_status)
    logging.info('parse_status succeed')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checks environmental variables."""
    constants = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    status = all(constants)
    logging.info('check_tokens succeed')
    return status


def main():
    """Main bot logic."""
    if not check_tokens():
        error = 'Необходимые перменные отсутствуют.'
        logging.error(error, exc_info=True)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - settings.MONTH_BACK)

    status = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Ошибка запроса к API сервису. {error}')
            time.sleep(settings.RETRY_TIME)
            continue
        try:
            if check_response(response):
                homework = check_response(response)[0]
                message = parse_status(homework)
            current_timestamp = current_timestamp
        except Exception as error:
            message = f'Сбой в программе. {error}'
            logging.error(error, exc_info=True)
        finally:
            if message != status:
                send_message(bot, message)
                status = message
            time.sleep(settings.RETRY_TIME)


if __name__ == '__main__':
    main()
