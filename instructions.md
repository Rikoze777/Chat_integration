# Подготовка
1. Заполните `.env` файл в соответствии с [примером](env_example)
2. Установка зависимостей:
```bash
pip install -r requirements.txt
```

## Запуск
```bash
python3 bot.py
```

## Запуск с Docker
```bash
docker-compose up -d --build
```
Применение миграций:
```bash
docker compose exec chat alembic upgrade head
```

Для остановки:
```bash
docker-compose down
```

## Работа с ботом

1. Начало работы `/start`
2. Помощь `/help`
3. Парсинг текста сайта в бд `/docs <url>`
4. Парсинг `.sql` в бд - после переноса файла в тг, подпишите`/sql`
5. Добавление инструкции к вашим запросам - `/prompt <text>`
6. Запросы в бот через `/grok`, `/openrouter`, `/openai` 
7. Пример: `/openrouter Напиши апи сайта`