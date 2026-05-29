# Wallet API

REST API для работы с балансом кошельков пользователей.

## Запуск (Docker)

Скопируйте переменные окружения:

```bash
cp .env.example .env
```

Поднять приложение и PostgreSQL:

```bash
docker compose up --build
```

- Swagger API: http://localhost:8000/docs

При старте контейнера `app` автоматически: `alembic upgrade head` → seed → uvicorn.

Сгенерировать файл миграции:

```bash
docker compose run --rm --entrypoint sh app -c "alembic revision --autogenerate -m 'описание_изменений'"
```

Применить миграции к БД:

```bash
docker compose run --rm --entrypoint sh app -c "alembic upgrade head"
```

Остановка:

```bash
docker compose down
```

Сброс данных БД:

```bash
docker compose down -v
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/wallets/{wallet_uuid}` | Текущий баланс |
| POST | `/api/v1/wallets/{wallet_uuid}/operation` | DEPOSIT / WITHDRAW |

Пример тела операции:

```json
{
  "operation_type": "DEPOSIT",
  "amount": 1000
}
```

## Seed (тестовые кошельки)

| UUID | Баланс |
|------|--------|
| `11111111-1111-1111-1111-111111111111` | 1000.00 |
| `22222222-2222-2222-2222-222222222222` | 500.00 |

Повторный seed вручную:

```bash
docker compose run --rm --entrypoint sh app -c "python -m scripts.seed"
```

## Тесты

```bash
docker compose run --rm --entrypoint sh app -c "alembic upgrade head && pytest -q"
```
**ОСТОРОЖНО! Выполнение команды очистит таблицы wallets, operations в БД.**

Покрытие: health, GET/POST wallets, 404/400/422, конкурентный withdraw.

## Линтер (PEP8) — `pyproject.toml` + Ruff

В корне лежит **`pyproject.toml`** — конфигурация инструментов Python

Проверка стиля в Docker:

```bash
docker compose run --rm --entrypoint sh app -c "ruff check . && ruff format --check ."
```

`ruff format .` — автоформатирование; `ruff format --check .` — только проверка без изменений файлов.

## Решения по домену

- Кошельки создаются скриптом seed. По несуществующему UUID → `404`.
- Суммы — `Decimal` / `NUMERIC` в БД.
- Невалидное тело запроса → `422`. Недостаточно средств при `WITHDRAW` → `400`.
- Ошибки API: `{"code": "...", "message": "..."}`.

## Конкурентность: почему race condition решена

При параллельных списаниях с одного кошелька баланс не уходит в минус: используется атомарный `UPDATE` в PostgreSQL (`WHERE balance >= amount` для WITHDRAW) и одна транзакция на операцию (обновление баланса + запись в `operations`).

Реализация: `app/services/operation_service.py`.

Проверка: `tests/test_concurrency.py` — 10 параллельных WITHDRAW по 200 при балансе 1000.
