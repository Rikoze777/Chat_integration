# Chat_integration

Телеграмм бот для написания API.

## Установка

1. Для передачи инструкций боту используется этот [файл](instruction.txt)
2. Для вопроса боту используется [файл](api_data.txt) с данными по необходимому апи
3. Заполните env файл в соответствии с [примером](env_example)

## Запуск
```bash
python3 bot.py
```

## Запуск с Docker
```bash
docker-compose up -d --build
```

Для остановки:
```bash
docker-compose down
```

## Работа с ботом

1. Приветствие `/start`
2. Вопрос к моделям OpenRouter: `/openrouter Ваш вопрос`
3. Вопрос к моделям OpenAI: `/openai Ваш вопрос`
