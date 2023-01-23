class OnlyForLog(Exception):
    """Исключение не для пересылки в telegram. Когда нет такой возможности."""

    pass


class RequestAPIError(OnlyForLog):
    """Ошибка в ответе API."""

    pass


class TokenNotFoundException(OnlyForLog):
    """Обработка исключения при отсуствии хотя бы одного из токенов."""

    pass


class TelegramError(OnlyForLog):
    """Ошибка отправки сообщения в telegram."""

    pass


class EmptyAnswer(Exception):
    """Ответ содержит пустой словарь."""

    pass


class EndPointIsNotAvailiable(Exception):
    """Проблема с endopoint. response != 200."""

    pass
