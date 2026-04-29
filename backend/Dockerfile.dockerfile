FROM python:3.11-slim

ARG BUILD_ENV=production
ARG USER_ID=1000
ARG GROUP_ID=1000

# Создаем непривилегированного пользователя
RUN groupadd -r appuser -g ${GROUP_ID} && \
    useradd -r -g appuser -u ${USER_ID} -m appuser

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Проверка доступа к PyPI (опционально)
RUN echo "=== Проверка доступа к PyPI ===" && \
    curl -I https://pypi.org/simple/ 2>/dev/null | head -n 1 || \
    (echo "=== НЕТ ДОСТУПА К PyPI ===" && exit 1)

# Настройка pip
RUN pip install --upgrade pip && \
    pip config set global.index-url https://pypi.org/simple

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Том для персистентных данных
VOLUME ["/app/data", "/app/logs"]

# Переключаемся на непривилегированного пользователя
USER appuser

# Запуск приложения с помощью uvicorn (для production)
# Или используйте asyncio режим для разработки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]