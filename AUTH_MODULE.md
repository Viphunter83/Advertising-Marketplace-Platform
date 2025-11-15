# 🔐 Модуль аутентификации - Документация

## ✅ Реализовано

### Endpoints

1. **POST /auth/register** - Регистрация нового пользователя
2. **POST /auth/login** - Вход в систему
3. **POST /auth/refresh** - Обновление access токена
4. **GET /auth/me** - Получить текущего пользователя (требует авторизации)
5. **POST /auth/logout** - Выход из системы (требует авторизации)

### Функциональность

- ✅ Регистрация пользователей (seller / channel_owner)
- ✅ Вход с проверкой пароля
- ✅ JWT токены (access + refresh)
- ✅ Обновление токенов
- ✅ Защита endpoints через зависимости
- ✅ Хеширование паролей (bcrypt)
- ✅ Валидация данных (Pydantic)

## 🚀 Быстрый старт

### 1. Запуск приложения

```bash
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Открыть Swagger UI

http://localhost:8000/docs

## 📝 Примеры использования

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "secure_password_123",
    "full_name": "Иван Петров",
    "phone": "+7 (999) 123-45-67",
    "user_type": "seller"
  }'
```

**Ответ**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Вход в систему

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "secure_password_123"
  }'
```

### Получить текущего пользователя

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Обновить токен

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## 🔒 Безопасность

### JWT Токены

- **Access Token**: Срок жизни - 24 часа (настраивается в `.env`)
- **Refresh Token**: Срок жизни - 7 дней
- **Алгоритм**: HS256
- **Подпись**: Секретный ключ из `JWT_SECRET_KEY`

### Пароли

- Хеширование: bcrypt
- Минимальная длина: 8 символов
- Пароли никогда не возвращаются в ответах API

### Защита endpoints

Используйте зависимости для защиты endpoints:

```python
from app.core.dependencies import get_current_user, get_seller_user

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@router.get("/seller-only")
async def seller_route(seller: dict = Depends(get_seller_user)):
    return {"seller": seller}
```

## 📋 Структура токена

### Access Token Payload

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "user_type": "seller",
  "type": "access",
  "exp": 1234567890
}
```

### Refresh Token Payload

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "user_type": "seller",
  "type": "refresh",
  "exp": 1234567890
}
```

## 🛠 Зависимости для защиты endpoints

### get_current_user
Проверяет, что пользователь авторизован. Возвращает:
```python
{
  "user_id": "uuid",
  "email": "user@example.com",
  "user_type": "seller" | "channel_owner" | "admin"
}
```

### get_seller_user
Проверяет, что пользователь - продавец.

### get_channel_owner_user
Проверяет, что пользователь - владелец канала.

### get_admin_user
Проверяет, что пользователь - администратор.

## ⚠️ Ошибки

| Код | Описание |
|-----|----------|
| 400 | Некорректные данные в запросе |
| 401 | Не авторизован или неверный токен |
| 403 | Нет прав доступа |
| 404 | Пользователь не найден |
| 500 | Внутренняя ошибка сервера |

## 📁 Структура файлов

```
app/
├── core/
│   ├── security.py          # JWT, хеширование паролей
│   └── dependencies.py       # Зависимости для защиты endpoints
├── schemas/
│   └── user.py              # Pydantic модели
├── services/
│   └── user_service.py      # Бизнес-логика пользователей
└── routers/
    └── auth.py              # API endpoints
```

## ✅ Готово к использованию

Модуль аутентификации полностью реализован и готов к использованию!

