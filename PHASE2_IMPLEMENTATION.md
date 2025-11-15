# 📡 PHASE 2 BACKEND: Real-time WebSocket + Email + Background Tasks

## ✅ РЕАЛИЗОВАНО

### 1. WebSocket сервер (Socket.io)
- ✅ `app/core/websocket.py` - Socket.io сервер для real-time уведомлений
- ✅ Аутентификация через JWT токен
- ✅ Управление активными подключениями
- ✅ Отправка уведомлений конкретным пользователям
- ✅ Broadcast уведомления для всех пользователей
- ✅ Heartbeat (ping/pong) для поддержания соединения

### 2. Email-уведомления (SendGrid)
- ✅ `app/services/email_service.py` - Сервис для отправки email
- ✅ HTML шаблоны для email:
  - `welcome.html` - Приветственное письмо
  - `new_campaign.html` - Уведомление о новой заявке
  - `campaign_accepted.html` - Уведомление о принятии заявки
  - `campaign_completed.html` - Уведомление о выплате
- ✅ Интеграция с SendGrid API
- ✅ Поддержка Jinja2 шаблонов

### 3. Background Tasks (APScheduler)
- ✅ `app/core/scheduler.py` - Планировщик фоновых задач
- ✅ Ежедневное обновление статистики платформы (00:00 UTC)
- ✅ Еженедельная очистка старых уведомлений (>30 дней)
- ✅ Проверка необработанных выводов (каждые 6 часов)

### 4. Обновлённый Notification Service
- ✅ Интеграция WebSocket + Email
- ✅ Автоматическое получение данных пользователя, если не переданы
- ✅ Уведомления для всех ключевых событий:
  - Новая заявка
  - Заявка принята
  - Заявка завершена (выплата)

### 5. Обновлённый Campaign Service
- ✅ Отправка уведомлений с полными данными (email, имя)
- ✅ Интеграция с NotificationService для всех событий

### 6. Обновлённый main.py
- ✅ Интеграция Socket.io с FastAPI через ASGI
- ✅ Lifecycle events (startup/shutdown)
- ✅ Запуск планировщика при старте
- ✅ Health check с информацией о WebSocket подключениях

---

## 📦 УСТАНОВКА ЗАВИСИМОСТЕЙ

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите новые зависимости Phase 2
pip install python-socketio==5.10.0 aioredis==2.0.1 apscheduler==3.10.4 sendgrid==6.11.0 jinja2==3.1.2 vk-api==11.9.9 python-telegram-bot==20.7 redis==5.0.1

# Или установите все зависимости из requirements.txt
pip install -r requirements.txt
```

---

## ⚙️ КОНФИГУРАЦИЯ

### Обновлённые переменные окружения:

Добавьте в `.env`:

```env
# Redis (опционально, для масштабирования WebSocket)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# WebSocket
WEBSOCKET_CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Email (SendGrid)
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@advertising-marketplace.com
SENDGRID_FROM_NAME=Advertising Marketplace

# VK API (опционально)
VK_SERVICE_KEY=your_vk_service_token_here

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Background Tasks
ENABLE_BACKGROUND_TASKS=true

# Frontend URL (для email ссылок)
FRONTEND_URL=http://localhost:3000
```

---

## 🚀 ЗАПУСК

### Локальная разработка:

```bash
# Запуск с WebSocket поддержкой
python main.py

# Или через uvicorn напрямую
uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload
```

**ВАЖНО**: Используйте `socket_app` вместо `app` для поддержки WebSocket!

---

## 📡 WEBSOCKET API

### Подключение:

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  path: '/socket.io',
  auth: {
    token: 'YOUR_JWT_ACCESS_TOKEN'
  }
});

socket.on('connected', (data) => {
  console.log('Connected:', data);
  // { status: 'ok', user_id: '...' }
});

socket.on('notification', (notification) => {
  console.log('Notification:', notification);
  // {
  //   type: 'new_campaign',
  //   title: 'Новая заявка на размещение',
  //   message: '...',
  //   campaign_id: '...',
  //   timestamp: '...'
  // }
});

socket.on('pong', (data) => {
  console.log('Pong:', data);
});

// Отправка ping для поддержания соединения
setInterval(() => {
  socket.emit('ping', { timestamp: Date.now() });
}, 5000);
```

### События:

- **`connect`** - Подключение с JWT токеном
- **`disconnect`** - Отключение
- **`ping`** - Heartbeat (клиент → сервер)
- **`pong`** - Ответ на ping (сервер → клиент)
- **`notification`** - Real-time уведомление (сервер → клиент)
- **`connected`** - Подтверждение подключения (сервер → клиент)

---

## 📧 EMAIL УВЕДОМЛЕНИЯ

### Типы email:

1. **Welcome Email** - После регистрации пользователя
2. **New Campaign** - Владельцу канала о новой заявке
3. **Campaign Accepted** - Продавцу о принятии заявки
4. **Campaign Completed** - Владельцу канала о выплате

### Использование:

```python
from app.services.email_service import EmailService

# Отправка приветственного письма
await EmailService.send_welcome_email(
    user_email="user@example.com",
    user_name="Иван Иванов"
)
```

---

## ⏰ BACKGROUND TASKS

### Задачи:

1. **update_platform_stats** - Ежедневно в 00:00 UTC
   - Обновляет статистику платформы в `platform_stats`

2. **cleanup_old_notifications** - Еженедельно (воскресенье, 02:00 UTC)
   - Удаляет уведомления старше 30 дней

3. **send_pending_withdrawal_reminders** - Каждые 6 часов
   - Проверяет выводы, ожидающие более 24 часов

### Отключение:

Установите в `.env`:
```env
ENABLE_BACKGROUND_TASKS=false
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Тест WebSocket (Python):

```python
# test_websocket.py
import socketio
import time

sio = socketio.Client()

@sio.on('connected')
def on_connected(data):
    print(f"✅ Connected: {data}")

@sio.on('notification')
def on_notification(data):
    print(f"📬 Notification received: {data}")

@sio.on('pong')
def on_pong(data):
    print(f"🏓 Pong: {data}")

# Подключаемся с JWT токеном
access_token = "YOUR_JWT_TOKEN_HERE"
sio.connect(
    'http://localhost:8000',
    auth={'token': access_token},
    socketio_path='/socket.io'
)

# Отправляем ping каждые 5 секунд
while True:
    sio.emit('ping', {'timestamp': time.time()})
    time.sleep(5)
```

Запуск:
```bash
python test_websocket.py
```

---

## 🚢 DEPLOYMENT

### Railway:

Создайте `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:socket_app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile (альтернатива):

```
web: uvicorn main:socket_app --host 0.0.0.0 --port $PORT
```

---

## 📝 ЗАМЕТКИ

### Для Production:

- ✅ Настройте конкретные CORS origins вместо `*`
- ✅ Используйте Redis для масштабирования WebSocket (multi-server)
- ✅ Настройте SendGrid API key
- ✅ Настройте VK и Telegram API (если нужны)
- ✅ Настройте правильный `FRONTEND_URL`
- ✅ Включите мониторинг background tasks

### Улучшения:

- Добавить rate limiting для WebSocket
- Добавить reconnection logic на клиенте
- Реализовать очередь для email (Celery)
- Добавить метрики для WebSocket подключений
- Реализовать VK и Telegram интеграции

---

## ✅ PHASE 2 ЗАВЕРШЁН!

Все основные функции Phase 2 реализованы:
- ✅ WebSocket сервер для real-time уведомлений
- ✅ Email-уведомления через SendGrid
- ✅ Background tasks с APScheduler
- ✅ Интеграция всех компонентов
- ✅ Готов к deployment

**Следующие шаги:**
1. Установите зависимости: `pip install -r requirements.txt`
2. Настройте переменные окружения в `.env`
3. Запустите приложение: `python main.py`
4. Протестируйте WebSocket подключение
5. Проверьте отправку email

Платформа готова к использованию! 🚀

