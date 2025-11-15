#!/bin/bash
# Скрипт для запуска бэкенда с поддержкой WebSocket

cd "$(dirname "$0")"

# Активируем виртуальное окружение если оно есть
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запускаем бэкенд с socket_app для поддержки WebSocket
echo "🚀 Starting backend with WebSocket support..."
python main.py

