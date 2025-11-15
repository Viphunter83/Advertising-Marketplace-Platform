# 🚀 БЫСТРЫЙ СТАРТ: Advertising Marketplace Platform

## 📖 ПЕРВЫЕ ШАГИ

1. **Прочитать**: `PROJECT_CONTEXT.md` — полный контекст проекта
2. **Изучить**: `BUG_404_AFTER_LOGIN.md` — детальное описание проблемы
3. **Проверить**: Запустить backend и frontend, воспроизвести проблему

## ⚡ БЫСТРЫЙ ЗАПУСК

### Backend
```bash
cd "Advertising Marketplace Platform"
source venv/bin/activate
python main.py
# Проверить: http://localhost:8000/health
```

### Frontend
```bash
cd frontend
npm run dev
# Открыть: http://localhost:3000
```

## 🐛 ТЕКУЩАЯ ПРОБЛЕМА

**404 после логина** — после успешного логина пользователь видит "404 Page not found"

**Ключевые файлы**:
- `frontend/src/components/forms/LoginForm.tsx`
- `frontend/src/components/common/AuthInitializer.tsx`
- `frontend/src/app/(seller)/layout.tsx`
- `frontend/src/lib/store/auth.store.ts`

**Рекомендации**: См. `BUG_404_AFTER_LOGIN.md` → Решение 5 (улучшить AuthInitializer)

## 🧪 ТЕСТОВЫЕ ДАННЫЕ

- **Seller**: `seller@test.com` / `seller123`
- **Channel**: `channel@test.com` / `channel123`
- **Admin**: `admin@test.com` / `admin123`

## 📁 ВАЖНЫЕ ФАЙЛЫ

- `PROJECT_CONTEXT.md` — полный контекст
- `BUG_404_AFTER_LOGIN.md` — детали проблемы
- `main.py` — точка входа backend
- `frontend/src/app/providers.tsx` — провайдеры React
- `.env` — переменные окружения (НЕ коммитить!)

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health: http://localhost:8000/health

---

**Для деталей см. PROJECT_CONTEXT.md**

