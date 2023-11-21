#Telegram-бот
## Описание.
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

Данный бот запущен на время прохождения обучения и используется для отслеживания состояния задания.
https://t.me/kirill_kitty_bot

## Используемые технологии:
* Python 3.9
* python-dotenv 0.19.0
* python-telegram-bot 13.7

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/lirostin/homework_bot.git
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```
Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

Записать в переменные окружения (файл .env) необходимые ключи:

* PRACTICUM_TOKEN. Токен профиля на Яндекс.Практикуме. [Ссылка](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a) на получение.
* TELEGRAM_TOKEN. Токен телеграм-бота. Для этого вам нужно создать бота и получить `API Token` у @BotFather в телеграмме
* TELEGRAM_CHAT_ID. Свой ID в телеграме. Можно получить свой `Current chat ID` у бота @getmyid_bot

## Запустить проект:

```
python homework.py
```
# Запуск проекта на сервере чере systemd

* Создаём директорию для приложения в `/opt` и даём права пользователю, в моём примере `pyuser`
```
sudo mkdir /opt/homework_bot
sudo chown student:student /opt/homework_bot/
```
## Настройка приложения
* Скачиваем приложение в папку `/opt/homework_bot` созданную ранее
```
cd /opt/
git clone https://github.com/lirostin/homework_bot.git
cd homework_bot
```
* Правим файл
```
vim /opt/homework_bot/Makefile
```
Указываем как запускается python, для linux `python3`
```
PYTHON = py -3.9
```
в `setup` меняем `ACTIVATE_WINDOWS` на `ACTIVATE_LINUX`
сохраняем и выходим.
* Запускаем создание виртуального пространсва командой
```
make setup
```
## Настройа сервиса
* Для автоматического запуска после перезагрузки создаём сервис.
```
sudo vim /etc/systemd/system/telegram-home.service  
```
* Заполняем telegram-home.service сохраняем и выходим.
```
[Unit]
Description = homework bot
After = network.target

[Service]
User=pyuser
Group=pyuser
WorkingDirectory=/opt/homework_bot/
ExecStart = /opt/homework_bot/venv/bin/python3 /opt/homework_bot/homework.py
Restart = on-failure
RestartSec = 5
TimeoutStartSec = infinity

[Install]
WantedBy=multi-user.target
```
* Запускаем сервис и активируем автозапуск
```
sudo systemctl start telegram-home.service
sudo systemctl enable telegram-home.service
```
* Проверяем логи
```
tail -f /opt/homework_bot/homework.log
```
При кореектном запуске вы увидете запись:
```
2023-11-21 16:56:15,421 - [DEBUG] - {'вернулся со статусом: 200.  Текст: {"homeworks":[],"current_date":1700574975}.Причина: OK. Запрос: https://practicum.yandex.ru/api/user_api/homework_statuses/, {\'Authorization\': \'ТУТ ЧТО-ТО СЕКРЕТНОЕ\'}, ТУТ ЧТО-ТО СЕКРЕТНОЕ: '} - get_api_answer
2023-11-21 16:56:15,422 - [DEBUG] - Пришёл пустой ответ. - main
```