# TGNotesBot

Веб-приложение и Telegram-бот для управления заметками с возможностью авторизации через Telegram и поддержки REST API. Реализовано на Django, PostgreSQL, Celery, Docker.

## Возможности

### Telegram-бот

- Авторизация через Telegram-виджет
- Создание и просмотр заметок
- Поиск по заголовку, содержимому и тегам
- Установка напоминаний (через Celery)

### Веб-интерфейс

- Просмотр, создание, редактирование и удаление заметок
- Фильтрация по категориям и тегам
- Экспорт заметок в текстовый файл

### API (JWT/Session Based)

- Поддержка всех CRUD-операций с заметками
- Авторизация через Telegram

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://
cd t
```



### 2. Установка зависимостей и запуск через Docker

```bash
docker-compose build
```

```bash
docker-compose up
```

### 3. Применение миграций

```bash
docker-compose exec web python manage.py migrate
```

### 4. Создание суперпользователя (опционально)

```bash
docker-compose exec web python manage.py createsuperuser
```


### 5. Подключение ngrok (для авторизации Telegram)

Telegram требует публичный HTTPS-домен. Запустите:

```bash
ngrok http 8000
```

Скопируйте `https://*.ngrok-free.app` и добавьте в:

- Telegram-бот через BotFather: `/setdomain`
- `data-auth-url` в `templates/registration/telegram_login.html`

## Тестирование API

Используйте Postman или curl:

```http
GET https://<ngrok-domain>.ngrok-free.app/api/notes/
```

Сначала авторизуйтесь через Telegram-виджет, чтобы получить сессию (cookie).



## Дамп базы данных (опционально)

```bash
docker-compose exec web python manage.py dumpdata > dump.json
```

## Сдача

- Репозиторий: GitHub с полным кодом
- README с инструкциями
- Swagger-страница
- Telegram-бот должен быть доступен по username
- Веб-домен через ngrok или развернутый сервер

