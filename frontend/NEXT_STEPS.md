# 🚀 СЛЕДУЮЩИЕ ШАГИ ДЛЯ РАЗРАБОТКИ ФРОНТЕНДА

## ✅ ЧТО УЖЕ ГОТОВО

1. ✅ Базовая структура Next.js 15
2. ✅ TypeScript типы и API клиенты
3. ✅ Zustand store для аутентификации
4. ✅ Socket.io клиент для WebSocket
5. ✅ UI компоненты (Shadcn/ui)
6. ✅ Формы входа и регистрации
7. ✅ Dashboard продавца (базовая версия)
8. ✅ Защита маршрутов

---

## 📋 ПРИОРИТЕТНЫЕ ЗАДАЧИ

### 1. Завершить аутентификацию

- [x] Login форма
- [x] Register форма
- [ ] Страница восстановления пароля
- [ ] Middleware для защиты маршрутов
- [ ] Автоматическое подключение WebSocket после логина

### 2. Dashboard для всех типов пользователей

- [x] Seller Dashboard (базовая версия)
- [ ] Channel Owner Dashboard
- [ ] Admin Dashboard
- [ ] Статистика и графики

### 3. Управление заявками

- [ ] Страница создания заявки (`/seller/campaigns/create`)
- [ ] Страница деталей заявки (`/seller/campaigns/[id]`)
- [ ] Список заявок с фильтрами
- [ ] Workflow заявок (accept, reject, submit, confirm)
- [ ] Timeline заявки

### 4. Поиск каналов

- [ ] Страница поиска каналов (`/seller/channels`)
- [ ] Компонент фильтров
- [ ] Карточка канала
- [ ] Модальное окно с деталями канала
- [ ] Рейтинг и отзывы канала

### 5. Профили пользователей

- [ ] Страница профиля продавца (`/seller/profile`)
- [ ] Редактирование профиля
- [ ] Страница профиля канала (`/channel/profile`)
- [ ] Настройки уведомлений

### 6. Платежи

- [ ] Страница баланса (`/seller/balance`)
- [ ] Пополнение баланса (`/seller/balance/deposit`)
- [ ] История транзакций
- [ ] Вывод средств (для channel owners)

### 7. Real-time уведомления

- [ ] Компонент уведомлений
- [ ] Интеграция WebSocket
- [ ] Toast уведомления
- [ ] Badge с количеством непрочитанных

### 8. Отзывы и рейтинги

- [ ] Форма создания отзыва
- [ ] Отображение отзывов канала
- [ ] Рейтинг канала

### 9. Админ-панель

- [ ] Dashboard с статистикой
- [ ] Управление пользователями
- [ ] Обработка споров
- [ ] Обработка выводов
- [ ] Графики и аналитика

---

## 🛠 КОМАНДЫ ДЛЯ РАЗРАБОТКИ

```bash
# Установка зависимостей
cd frontend
npm install

# Запуск dev сервера
npm run dev

# Проверка типов
npm run type-check

# Линтинг
npm run lint

# Сборка
npm run build
```

---

## 📝 ПРИМЕРЫ КОДА

### Создание нового компонента

```tsx
// components/campaigns/CampaignCard.tsx
'use client';

import { Campaign } from '@/lib/types';
import { Card } from '@/components/ui/card';

export function CampaignCard({ campaign }: { campaign: Campaign }) {
  return (
    <Card>
      {/* ... */}
    </Card>
  );
}
```

### Использование React Query

```tsx
import { useQuery } from '@tanstack/react-query';
import { campaignsApi } from '@/lib/api/campaigns.api';

export function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.getMyCampaigns(),
  });
  
  // ...
}
```

### Использование WebSocket

```tsx
import { useEffect } from 'react';
import { connectSocket, onNotification } from '@/lib/socket';
import { useAuthStore } from '@/lib/store/auth.store';

export function useWebSocketNotifications() {
  const { user } = useAuthStore();
  
  useEffect(() => {
    if (!user) return;
    
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    const socket = connectSocket(token);
    
    const handleNotification = (notification: Notification) => {
      toast.success(notification.title);
    };
    
    onNotification(handleNotification);
    
    return () => {
      socket.disconnect();
    };
  }, [user]);
}
```

---

## 🎨 ДОБАВЛЕНИЕ НОВЫХ UI КОМПОНЕНТОВ

Для добавления Shadcn/ui компонентов:

```bash
npx shadcn-ui@latest add [component-name]
```

Например:
```bash
npx shadcn-ui@latest add select
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add dialog
```

---

## 🔗 ИНТЕГРАЦИЯ С BACKEND

### API Endpoints

Все API endpoints находятся в `src/lib/api/`:

- `auth.api.ts` - `/auth/*`
- `campaigns.api.ts` - `/campaigns/*`
- `channels.api.ts` - `/channels/*`
- `payments.api.ts` - `/payments/*`
- `reviews.api.ts` - `/reviews/*`
- `admin.api.ts` - `/admin/*`

### WebSocket

WebSocket подключение настраивается автоматически при логине через `lib/socket.ts`.

---

## ✅ ГОТОВО К РАЗРАБОТКЕ!

Базовая структура создана. Можно начинать добавлять остальные страницы и компоненты!

