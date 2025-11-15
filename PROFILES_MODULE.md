# 👤 Модуль управления профилями - Документация

## ✅ Реализовано

### Endpoints для продавцов (Sellers)

1. **POST /sellers/profile** - Создать профиль продавца (требует авторизации, тип: seller)
2. **GET /sellers/profile** - Получить свой профиль продавца (требует авторизации, тип: seller)
3. **PUT /sellers/profile** - Обновить профиль продавца (требует авторизации, тип: seller)
4. **POST /sellers/payment-details** - Обновить платёжные реквизиты (требует авторизации, тип: seller)
5. **GET /sellers/stats** - Получить статистику продавца (требует авторизации, тип: seller)
6. **GET /sellers/{seller_id}** - Получить публичный профиль продавца (без авторизации)

### Endpoints для владельцев каналов (Channels)

1. **POST /channels/profile** - Создать профиль канала (требует авторизации, тип: channel_owner)
2. **GET /channels/profile** - Получить свой профиль канала (требует авторизации, тип: channel_owner)
3. **PUT /channels/profile** - Обновить профиль канала (требует авторизации, тип: channel_owner)
4. **GET /channels/stats** - Получить статистику канала (требует авторизации, тип: channel_owner)
5. **GET /channels/** - Поиск каналов по фильтрам (доступно всем)
6. **GET /channels/{channel_id}** - Получить публичный профиль канала (без авторизации)

## 🚀 Быстрый старт

### 1. Создание профиля продавца

```bash
# 1. Зарегистрируйтесь как продавец
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "password123",
    "full_name": "Иван Петров",
    "user_type": "seller"
  }'

# 2. Войдите и получите токен
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "password123"
  }'

# 3. Создайте профиль продавца
curl -X POST "http://localhost:8000/sellers/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_name": "Интернет-магазин TechStore",
    "shop_url": "https://wildberries.ru/seller/techstore",
    "shop_description": "Продаём качественную электронику",
    "category": "Техника",
    "notification_email": "seller@techstore.com"
  }'
```

### 2. Создание профиля канала

```bash
# 1. Зарегистрируйтесь как владелец канала
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "channel@example.com",
    "password": "password123",
    "full_name": "Владелец Канала",
    "user_type": "channel_owner"
  }'

# 2. Войдите и получите токен
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "channel@example.com",
    "password": "password123"
  }'

# 3. Создайте профиль канала
curl -X POST "http://localhost:8000/channels/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "vk",
    "channel_url": "https://vk.com/mychannel",
    "channel_name": "Мой канал о моде",
    "channel_description": "Тренды в моде и стиль жизни",
    "category": "Мода",
    "tags": ["lifestyle", "fashion", "shopping"],
    "subscribers_count": 50000,
    "avg_reach": 15000,
    "engagement_rate": 4.5,
    "audience_geo": "Москва",
    "audience_age_group": "18-25",
    "audience_gender": "F",
    "price_per_post": 5000.00,
    "price_per_story": 2000.00,
    "price_per_video": 10000.00
  }'
```

### 3. Поиск каналов

```bash
# Поиск каналов по фильтрам (доступно всем, без токена)
curl "http://localhost:8000/channels/?platforms=vk&platforms=telegram&categories=Мода&min_subscribers=10000&max_price=10000&sort_by=rating&sort_order=desc"
```

## 📋 Структура данных

### Профиль продавца (Seller)

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "shop_name": "Название магазина",
  "shop_url": "https://...",
  "shop_description": "Описание",
  "category": "Техника",
  "logo_url": "https://...",
  "balance": 150000.50,
  "total_spent": 5000.00,
  "total_campaigns": 12,
  "payment_method": "yoomoney",
  "payment_details": {
    "account": "...",
    "holder_name": "...",
    "bank_name": "..."
  },
  "notifications_enabled": true,
  "notification_email": "seller@example.com",
  "kyc_status": "not_verified",
  "is_active": true,
  "created_at": "2025-11-15T09:30:00Z",
  "updated_at": "2025-11-15T09:30:00Z"
}
```

### Профиль канала (Channel)

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "platform": "vk",
  "channel_url": "https://vk.com/...",
  "channel_name": "Название канала",
  "channel_description": "Описание",
  "channel_avatar_url": "https://...",
  "category": "Мода",
  "tags": ["lifestyle", "fashion"],
  "subscribers_count": 50000,
  "avg_reach": 15000,
  "engagement_rate": 4.5,
  "audience_geo": "Москва",
  "audience_age_group": "18-25",
  "audience_gender": "F",
  "price_per_post": 5000.00,
  "price_per_story": 2000.00,
  "price_per_video": 10000.00,
  "rating": 4.8,
  "total_orders": 25,
  "completed_orders": 24,
  "total_earned": 125000.00,
  "verified": true,
  "verification_date": "2025-11-15T09:30:00Z",
  "is_active": true,
  "created_at": "2025-11-15T09:30:00Z",
  "updated_at": "2025-11-15T09:30:00Z"
}
```

## 🔍 Фильтры поиска каналов

### Доступные параметры:

- **platforms**: Список платформ (vk, telegram, pinterest, instagram, tiktok)
- **categories**: Список категорий
- **min_subscribers / max_subscribers**: Диапазон подписчиков
- **min_engagement_rate / max_engagement_rate**: Диапазон ER
- **min_price / max_price**: Диапазон цен
- **geo**: Список географий аудитории
- **age_group**: Список возрастных групп
- **gender**: Пол аудитории (M, F, All)
- **min_rating**: Минимальный рейтинг
- **verified_only**: Только проверенные каналы
- **sort_by**: Сортировка (price, rating, subscribers, engagement_rate)
- **sort_order**: Порядок сортировки (asc, desc)

### Примеры запросов:

```bash
# Каналы VK и Telegram в категории "Мода" с минимум 10000 подписчиков
GET /channels/?platforms=vk&platforms=telegram&categories=Мода&min_subscribers=10000

# Каналы с ценой до 5000 рублей, отсортированные по рейтингу
GET /channels/?max_price=5000&sort_by=rating&sort_order=desc

# Только проверенные каналы с ER выше 3%
GET /channels/?min_engagement_rate=3&verified_only=true
```

## 🔒 Безопасность

### Защита endpoints

- **Требуют авторизации**: Все endpoints `/sellers/profile/*` и `/channels/profile/*`
- **Проверка типа пользователя**: 
  - Endpoints продавцов требуют `user_type = "seller"`
  - Endpoints владельцев каналов требуют `user_type = "channel_owner"`
- **Публичные endpoints**: 
  - `GET /sellers/{seller_id}` - доступен всем
  - `GET /channels/{channel_id}` - доступен всем
  - `GET /channels/` - поиск доступен всем

## 📊 Статистика

### Статистика продавца

```json
{
  "total_spent": 5000.00,
  "total_campaigns": 12,
  "active_campaigns": 3,
  "completed_campaigns": 9,
  "average_roi": null,
  "balance": 150000.50
}
```

### Статистика канала

```json
{
  "total_earned": 125000.00,
  "total_orders": 25,
  "completed_orders": 24,
  "completion_rate": 0.96,
  "average_price": 5000.00,
  "rating": 4.8,
  "balance": 0
}
```

## ⚠️ Ошибки

| Код | Описание |
|-----|----------|
| 400 | Некорректные данные в запросе |
| 401 | Не авторизован |
| 403 | Нет прав доступа (неправильный тип пользователя) |
| 404 | Профиль не найден |
| 500 | Внутренняя ошибка сервера |

## 📁 Структура файлов

```
app/
├── schemas/
│   ├── seller.py          # Pydantic схемы для продавцов
│   └── channel.py         # Pydantic схемы для каналов
├── services/
│   ├── seller_service.py  # Бизнес-логика продавцов
│   └── channel_service.py # Бизнес-логика каналов
└── routers/
    ├── sellers.py          # API endpoints продавцов
    └── channels.py         # API endpoints каналов
```

## ✅ Готово к использованию

Модуль управления профилями полностью реализован и готов к использованию!

