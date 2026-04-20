# Speak — универсальный мессенджер

**Speak** — это мессенджер, в котором легко и доступно общаться.  
Отлично подходит для повседневного общения и малого бизнеса.

---

## 📁 Документация проекта

| Тип | Ссылка |
| --- | ------ |
| 🔗 **Макеты (Figma)** | [Ссылка на макеты (wireframes)](https://www.figma.com/design/JOO8HrxHshwN3qOGFVSHaH/%D0%BC%D0%B5%D1%81%D1%81%D0%B5%D0%BD%D0%B4%D0%B6%D0%B5%D1%80-SPEAK?node-id=0-1&t=j7FRV1dnuoXR96Ot-1) |
| 📄 **Протокол встреч** | [Google Drive](https://docs.google.com/document/d/1VR7v1zu5sdNoHEPyArpj-ybU7lgKAVEj/edit?usp=drive_link&ouid=102861828266811402403&rtpof=true&sd=true) |
| 📋 **User Stories** | [Google Drive](https://docs.google.com/document/d/1A9zpAwSXmT2BHRVZm1PjfzQvz_ZGmDDZ/edit?usp=drive_link&ouid=102861828266811402403&rtpof=true&sd=true) |
| 🗃️ **Структура БД** | [Google Drive](https://docs.google.com/document/d/1yTPxP3k4MRH7LLv5NE1Tp1eeIluOdLHp/edit?usp=drive_link&ouid=102861828266811402403&rtpof=true&sd=true) |
| 🔌 **API (OpenAPI)** | После запуска: `http://localhost:5000/docs` |
| 🧪 **CI/CD** | GitHub Actions (линтеры, тесты) |

---

## 🧩 Ключевые сценарии (MVP)

1. Регистрация / вход
2. Создание личного и группового чата
3. Приглашение участников
4. Отправка и получения сообщений в реальном времени
5. Редактирование сообщений в реальном времени
6. Редактирование и просмотр профиля

> Полный список User Stories — в документе выше.

---

## 🧱 Технологический стек

| Слой | Технологии |
|------|-------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL 15+, Redis 7+ |
| **Auth** | JWT (access + refresh) |
| **Frontend** | React 18+, Zustand, Axios, Socket.io-client |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions |

---

## Структура проекта


---


---

## Основные эндпоинты (v1)

### Auth
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация пользователя |
| POST | `/api/v1/auth/login` | Вход в систему (JWT) |
| POST | `/api/v1/auth/refresh` | Обновление access токена |
| POST | `/api/v1/auth/logout` | Выход |

### Users
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/users/me` | Получить свой профиль |
| PATCH | `/api/v1/users/me` | Обновить профиль |

### Chats
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/chats` | Список чатов пользователя |
| POST | `/api/v1/chats/private` | Создать личный чат |
| POST | `/api/v1/chats/group` | Создать групповой чат |
| GET | `/api/v1/chats/{chat_id}` | Детали чата |
| POST | `/api/v1/chats/{chat_id}/invite` | Сгенерировать ссылку-приглашение |
| POST | `/api/v1/chats/join/{invite_code}` | Вступить по ссылке |

### Messages
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/chats/{chat_id}/messages` | История сообщений (пагинация) |
| POST | `/api/v1/chats/{chat_id}/messages` | Отправить сообщение |

### WebSocket
| Эндпоинт | Описание |
|----------|----------|
| `ws://localhost:8000/ws/{user_id}` | Подключение к WebSocket (с JWT в query params) |

---

## Быстрый старт

### Требования
- Docker / Docker Compose
- Python 3.11+ (для локальной разработки без Docker)
- Node.js 18+ (для фронтенда)

### Запуск через Docker Compose (рекомендовано)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/your-team/speak.git
cd speak

# 2. Скопировать и настроить переменные окружения
cp backend/.env backend/.env
cp frontend/.env frontend/.env

# 3. Запустить все сервисы
docker-compose up -d

# 4. Применить миграции БД
docker-compose exec backend alembic upgrade head
```
---

## Команда

| Роль | Имя | Контакт |
|-------|----------|----------|
| Team Lead / System Analyst | Григорий Каппес | https://t.me/gr1kap |
| UI/UX Designer | 	Никита Исмайлов | https://t.me/Zimchanos |
| Backend Developer | 	Анастасия Подольская | https://t.me/vinolix |

---

## Ссылки

Репозиторий: https://github.com/vinolix88/speak.git

Kaiten: https://aipodolskaya88.kaiten.ru/space/573977/boards

Google Drive (отчетность): https://drive.google.com/drive/folders/1Pz0iUUDjw11oXb3WDSIryYetoW2Q_Fzd?usp=drive_link

ER-диаграмма:  https://drive.google.com/drive/folders/1Pz0iUUDjw11oXb3WDSIryYetoW2Q_Fzd?usp=drive_link

Use Case Diagram:  https://drive.google.com/drive/folders/1Pz0iUUDjw11oXb3WDSIryYetoW2Q_Fzd?usp=drive_link
