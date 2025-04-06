# Используем официальный Python 3.11 slim образ
FROM python:3.11-slim

# Устанавливаем системные зависимости (при необходимости)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Задаём рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь исходный код в контейнер
COPY . .

# Команда для запуска приложения через uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
