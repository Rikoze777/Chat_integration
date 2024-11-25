# Chat_integration

Телеграмм бот для написания API.
проверка гипотез в [colab](https://colab.research.google.com/drive/1S5eyoxD0q3bIv84mbrWIq784wpUYYbBX?usp=sharing#scrollTo=IeCqRnFBnV1K)

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


op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

op.execute("DROP EXTENSION IF EXISTS vector;")