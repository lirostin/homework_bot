class OnlyForLog(Exception):
    """Исключение не для пересылки в telegram. Когда нет такой возможности."""

    pass


class TokenNotFoundException(OnlyForLog):
    """Обработка исключения при отсуствии хотя бы одного из токенов."""

    pass


class TelegramError(OnlyForLog):
    """Ошибка отправки сообщения в telegram."""

    pass
