# Укажите базовый образ Python 3.11 с минимальными зависимостями
FROM python:3.11-slim

# Установите необходимые системные пакеты для сборки и работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установите Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - 
ENV PATH="${PATH}:/root/.local/bin"

# Установите рабочую директорию
WORKDIR /app

# Скопируйте файл для управления зависимостями в контейнер
COPY pyproject.toml poetry.lock* /app/

# Установите зависимости с помощью Poetry (без dev-зависимостей и без установки самого проекта)
RUN poetry install --no-root --no-dev

# Скопируйте все остальные файлы проекта в контейнер
COPY . .

# Укажите команду для выполнения миграций и запуска сервера
ENTRYPOINT ["sh", "-c", "poetry run python manage.py migrate && poetry run python manage.py runserver 0.0.0.0:8000"]
