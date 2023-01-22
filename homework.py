import logging
import os
import time
from logging.handlers import RotatingFileHandler

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
    "homework.log", encoding="utf-8", maxBytes=10_000, backupCount=4
)
logger.addHandler(handler)
handler.setFormatter(formatter)


def check_tokens() -> bool:
    """Проверяем переменные акружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отпарвляет пользователю сообщение в телеграмм."""
    try:
        logger.debug(
            f'Начинаю отправку сообщения в телеграмм: "{message[:15]}..."'
        )
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        message = f"Ошибка отправки сообщения, статуса в telegram: {error}"
        logger.error(message, exc_info=True)
        raise exceptions.TelegramError(message)
    else:
        logger.debug(f'Сообщение отправлено: "{message[:15]}..."')


# def get_api_answer(timestamp):
#     ...


# def check_response(response):
#     ...


# def parse_status(homework):
#     ...

#     return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = "Не указаны переменные акружения в файле .env!"
        logger.critical(message)
        raise exceptions.TokenNotFoundException(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time())
    previous_message = ""

    while True:
        try:
            message = "I'm test message. My target is to be a text message."
            send_message(bot, message)

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
