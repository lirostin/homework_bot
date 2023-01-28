import logging
import os
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError
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
        logger.debug(f'Сообщение отправлено: "{message}".')
    except telegram.error.TelegramError as error:
        raise exceptions.TelegramMessageError(
            f"Ошибка отправки сообщения, статуса в telegram: {error}"
        )


def get_api_answer(timestamp: int) -> dict:
    """Запрашиваем список домашних работ."""
    try:
        response = requests.get(
            url=ENDPOINT, headers=HEADERS, params={"from_date": timestamp}
        )
        about_response = (
            f"Запрос: {ENDPOINT}, {HEADERS}, {timestamp}: "
            f"вернулся со статусом: {response.status_code}. "
            f"Код ответа: {response.status_code}. "
            f"Причина: {response.reason}. "
            f"Текст: {response.text}."
        )
        if response.status_code != HTTPStatus.OK:
            raise exceptions.EndPointIsNotAvailiable(about_response)
        logger.debug(about_response)
        return response.json()
    except requests.exceptions.RequestException as error:
        raise exceptions.RequestAPIError(
            f"Ошибка при запросе к основному API: {error}"
        )
    except JSONDecodeError as error:
        raise exceptions.JSONError(f"Ошибка при декодировании JSON: {error}")


def check_response(response: dict) -> dict:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(f"Ответ API не является dict. {response}")
    if "homeworks" not in response or "current_date" not in response:
        raise exceptions.EmptyAnswer("Пришёл пустой ответ.")
    homework_list = response.get("homeworks")
    if not isinstance(homework_list, list):
        raise TypeError("homeworks не является list")
    if len(homework_list) == 0:
        raise exceptions.EmptyAnswer("Пришёл пустой ответ.")
    homework = homework_list[0]
    return homework


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работе и её статус."""
    if "homework_name" not in homework:
        raise KeyError("Нет ключа homework_name в ответе API")
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
            timestamp = response.get("current_date", int(time.time()))
            homework_dict = check_response(response)
            message = parse_status(homework_dict)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
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
