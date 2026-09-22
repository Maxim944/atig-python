# ATIG — Guardian Trusted Autonomous Intelligence (Python)

Полноценный production-ready сайт на **Python (FastAPI)** с регистрацией через Magic Link (Supabase).

## Возможности

- Лендинг в тёмном neural/futuristic стиле
- Passwordless авторизация (Magic Link по email)
- Защищённые страницы: `/dashboard`, `/profile`, `/vault`, `/settings`
- Личный кабинет, профиль, заглушка Life Vault
- Footer с почтой создателя: **creator@atig.ai**
- Адаптивный дизайн (Tailwind CSS через CDN)

## Стек

- **FastAPI** — веб-фреймворк
- **Jinja2** — шаблоны
- **Supabase** — Auth (Magic Link) + Database
- **Uvicorn** — ASGI-сервер
- Tailwind CSS (CDN)

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/Maxim944/atig-python.git
cd atig-python
```

### 2. Создай виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# или
venv\Scripts\activate      # Windows
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Настрой Supabase

1. Создай проект на [supabase.com](https://supabase.com)
2. **Authentication → Providers → Email** — включи Email
3. **Authentication → URL Configuration**:
   - Site URL: `http://localhost:8000`
   - Redirect URLs: `http://localhost:8000/auth/callback`
4. Скопируй из **Project Settings → API**:
   - Project URL
   - `anon` `public` ключ

### 5. Создай `.env`

```bash
cp .env.example .env
```

Заполни:

```env
SUPABASE_URL=https://твой-проект.supabase.co
SUPABASE_KEY=твой-anon-ключ
SITE_URL=http://localhost:8000
```

### 6. Запусти

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Открой: **http://localhost:8000**

## Как работает Magic Link

1. Пользователь вводит email на `/login`
2. Supabase отправляет письмо со ссылкой
3. Пользователь кликает → попадает на `/auth/callback`
4. Создаётся сессия (cookies) → редирект в `/dashboard`

## Структура

```
atig-python/
├── main.py              # FastAPI приложение
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── callback.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── vault.html
│   ├── settings.html
│   ├── privacy.html
│   └── terms.html
└── static/
```

## Деплой

Можно деплоить на Railway / Render / Fly.io / VPS.

Не забудь обновить Redirect URLs в Supabase на production-домен.

## Контакты

creator@atig.ai
