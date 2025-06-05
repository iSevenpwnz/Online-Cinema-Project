[![codecov](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project/branch/main/graph/badge.svg)](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project)

# Online Cinema Project

## Структура проєкту

```
.
├── src/
│   ├── main.py                 # Точка входу FastAPI
│   ├── config/                 # Налаштування додатку (settings.py, dependencies.py)
│   ├── database/               # Моделі, міграції, сесії БД, валідатори БД
│   ├── exceptions/             # Кастомні винятки
│   ├── notifications/          # Обробка сповіщень (напр., email)
│   ├── routes/                 # FastAPI ендпоінти (маршрутизація)
│   ├── schemas/                # Pydantic-схеми (валідація даних)
│   ├── security/               # Логіка безпеки (автентикація, авторизація, токени)
│   ├── storages/               # Інтеграція зі сховищами (напр., S3)
│   ├── tests/                  # Внутрішні тести для src (e2e, integration, doubles)
│   └── validation/             # Специфічна бізнес-валідація
├── tests/                      # Тести на верхньому рівні (unit)
├── alembic.ini                 # Налаштування Alembic (міграції БД)
├── commands/                   # Допоміжні скрипти (deploy, run_migrations і т.д.)
├── configs/                    # Конфігурації для зовнішніх сервісів (напр., nginx)
├── docker/                     # Dockerfiles для різних компонентів (mailhog, minio_mc, nginx, tests)
├── docker-compose-dev.yml      # Docker Compose для середовища розробки
├── docker-compose-prod.yml     # Docker Compose для продакшен середовища
├── docker-compose-tests.yml    # Docker Compose для тестового середовища
├── Dockerfile                  # Docker-образ для основного додатку FastAPI
├── .env.example                # Приклад файлу змінних оточення
├── .flake8                     # Конфігурація для лінтера flake8
├── pyproject.toml              # Конфігурація проекту та залежностей (Poetry)
├── README.md                   # Цей файл документації
└── .codecov.yml                # Налаштування Codecov для звітності по покриттю тестами
```

**Коротко:**
- `models/` — структура БД, ORM-моделі
- `schemas/` — Pydantic-схеми для API
- `services/` — бізнес-логіка, інтеграції
- `routes/` — HTTP endpoints FastAPI
- `core/` — базові утиліти, спільний код
- `celery/` — фонові задачі
- `tests/` — всі тести
- `config.py`, `db.py` — налаштування та підключення до БД

<!-- решта твого README.md нижче -->