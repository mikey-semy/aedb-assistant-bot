# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем скрипт для создания индекса
RUN /bin/sh -c "python create_rag_index.py"


# Указываем команду для запуска приложения
CMD ["python", "main.py"]
