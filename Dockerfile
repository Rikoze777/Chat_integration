FROM python:3.9-slim

COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app/

CMD ["python", "bot.py"]