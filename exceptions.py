class OnlyForLog(Exception):
    """Исключение не для пересылки в telegram. Когда нет такой возможности."""

    pass


class RequestAPIError(OnlyForLog):
    """Ошибка в ответе API."""

    pass


class TokenNotFoundException(OnlyForLog):
    """Обработка исключения при отсуствии хотя бы одного из токенов."""

    pass


class TelegramMessageError(OnlyForLog):
    """Ошибка отправки сообщения в telegram."""

    pass


class EndPointIsNotAvailiable(Exception):
    """Проблема с endopoint. response != 200."""

    pass


class JSONError(Exception):
    """Ошибка при декодировании сообщения JSON."""

    pass


class NoKey(Exception):
    """Ошибка отсутсвие необходимого ключа."""

    pass


class EmptyAnswer(Exception):
    """Пришёл пустой словарь в "homeworks":[]."""

    pass
