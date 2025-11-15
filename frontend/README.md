# 🎨 Advertising Marketplace Platform - Frontend

Next.js 15 frontend для платформы размещения рекламы.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
npm install
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env.local` и заполните:

```bash
cp .env.example .env.local
```

Обязательные переменные:
- `NEXT_PUBLIC_API_URL` - URL backend API (http://localhost:8000)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (ws://localhost:8000/socket.io)
- `NEXT_PUBLIC_FRONTEND_URL` - URL фронтенда (http://localhost:3000)

### 3. Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно на http://localhost:3000

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── app/              # Next.js App Router страницы
│   ├── components/       # React компоненты
│   ├── lib/              # Библиотеки и утилиты
│   ├── hooks/            # Custom React hooks
│   └── styles/           # Глобальные стили
├── public/               # Статические файлы
└── package.json
```

## 🛠 Технологии

- **Next.js 15** - React framework с App Router
- **TypeScript** - Типизация
- **TailwindCSS** - Utility-first CSS
- **Shadcn/ui** - UI компоненты
- **Zustand** - State management
- **TanStack Query** - Data fetching и caching
- **Socket.io-client** - WebSocket для real-time
- **React Hook Form + Zod** - Формы и валидация

## 📝 Основные функции

- ✅ Аутентификация (Login/Register)
- ✅ Dashboard для продавцов, владельцев каналов и админов
- ✅ Управление заявками
- ✅ Поиск каналов
- ✅ Платежи и баланс
- ✅ Real-time уведомления (WebSocket)
- ✅ Отзывы и рейтинги

## 🔗 Связь с Backend

Frontend подключается к backend API через:
- REST API: `NEXT_PUBLIC_API_URL`
- WebSocket: `NEXT_PUBLIC_WS_URL`

JWT токены автоматически добавляются в заголовки запросов через Axios interceptors.

## 🚢 Deployment

### Vercel

1. Подключите GitHub репозиторий к Vercel
2. Настройте environment variables в Vercel dashboard
3. Deploy автоматически при push в main

### Environment Variables на Vercel

```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/socket.io
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.vercel.app
```

## 📚 Документация

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query/latest)

