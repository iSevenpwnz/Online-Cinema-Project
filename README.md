[![codecov](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project/branch/main/graph/badge.svg)](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project)

# Online Cinema Project

## Структура проєкту

```
.
├── src/
│   └── app/
│       ├── main.py            # Точка входу FastAPI
│       ├── config.py          # Налаштування (env, конфіг)
│       ├── db.py              # Підключення до бази даних
│       ├── core/              # Ядро, утиліти, базові класи
│       ├── models/            # ORM-моделі (структура таблиць БД)
│       ├── schemas/           # Pydantic-схеми (валідація, серіалізація)
│       ├── services/          # Бізнес-логіка (робота з БД, сторонні сервіси)
│       ├── routes/            # FastAPI endpoints (роутінг)
│       └── celery/            # Celery таски (фонова обробка)
├── tests/                     # Тести (unit, інтеграційні)
├── alembic.ini                # Налаштування Alembic (міграції)
├── docker-compose.yml         # Docker-оркестрація сервісів
├── Dockerfile                 # Docker-образ для застосунку
├── .env.example               # Приклад змінних оточення
├── .flake8                    # Налаштування flake8 (стиль коду)
├── pyproject.toml             # Poetry/Nox конфіг, залежності
├── README.md                  # Документація проєкту
└── .codecov.yml               # Налаштування Codecov (ігнорування, цілі)
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