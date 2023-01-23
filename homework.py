import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - %(message)s - %(funcName)s"
)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    "homework.log", encoding="utf-8", maxBytes=10_00_000, backupCount=4
)
logger.addHandler(handler)
handler.setFormatter(formatter)


def check_tokens() -> bool:
    """Проверяем переменные акружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отпарвляет пользователю сообщение в телеграмм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        message = f"Ошибка отправки сообщения, статуса в telegram: {error}"
        logger.error(message, exc_info=True)
        raise exceptions.TelegramError(message)
    else:
        logger.debug(f'Сообщение отправлено: "{message[:15]}..."')


def get_api_answer(timestamp: int) -> dict:
    """Запрашиваем список домашних работ."""
    try:
        response = requests.get(
            url=ENDPOINT, headers=HEADERS, params={"from_date": timestamp}
        )
        if response.status_code != 200:
            raise exceptions.EndPointIsNotAvailiable(response.status_code)
    except requests.exceptions.RequestException as error:
        raise exceptions.RequestAPIError(
            f"Ошибка при запросе к основному API: {error}"
        )
    return response.json()


def get_time_interval(days: int) -> int:
    """За какой период проверить сообщения."""
    if days == 0:
        return 0
    sec = days * 24 * 60 * 60
    return int(time.time()) - sec


def check_response(response: dict) -> dict:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError("Ответ API не является dict")
    homework_list = response.get("homeworks")
    if not isinstance(homework_list, list):
        raise TypeError("homeworks не является list")
    if len(homework_list) == 0:
        raise exceptions.EmptyAnswer("Пришёл пустой ответ.")
    homework = homework_list[0]
    return homework


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работе и её статус."""
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_name is None:
        raise KeyError("В ответе API отсутствует ключ homework_name")
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f"Статус {homework_status} не найден")
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = "Не указаны переменные акружения в файле .env!"
        logger.critical(message)
        raise exceptions.TokenNotFoundException(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_message = ""

    while True:
        try:
            response = get_api_answer(timestamp)
            homework_dict = check_response(response)
            message = parse_status(homework_dict)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
                timestamp = int(time.time())
            else:
                logger.debug("Cтатус домашней работы не изменился.")

        except exceptions.OnlyForLog as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message, exc_info=True)

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message, exc_info=True)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
