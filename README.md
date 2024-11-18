# Chat_integration

Телеграмм бот для написания API.

## Установка

1. Для передачи инструкций боту используется этот [файл](instruction.txt)
2. Для вопроса боту используется [файл](api_data.txt) с данными по необходимому апи
3. Заполните env файл в соответствии с [примером](env_example)
4. Установка зависимостей:
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

Для остановки:
```bash
docker-compose down
```

## Работа с ботом

1. Начало работы `/start`
