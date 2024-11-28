# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

RUN apt-get update && apt-get install -y wget

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

RUN wget -P /knowledge/docs https://storage.yandexcloud.net/drivers.data/docs/siemens/simovert/masterdrives-rru_m_en.pdf

# Запускаем скрипт для создания индекса
RUN /bin/sh -c "python create_rag_index.py"


# Указываем команду для запуска приложения
CMD ["python", "main.py"]
